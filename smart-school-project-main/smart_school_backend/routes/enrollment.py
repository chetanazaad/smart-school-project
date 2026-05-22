from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
import json
import os
import sqlite3
import logging
import sys

# Fix imports to work from any directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from utils.db import get_db
except ImportError:
    from smart_school_backend.utils.db import get_db

try:
    from models.face_recognition import store_face_embedding, load_all_embeddings
except ImportError:
    from smart_school_backend.models.face_recognition import store_face_embedding, load_all_embeddings

# NOTE: face_engine.encoder is imported lazily in functions to avoid TensorFlow dependency at startup
enrollment_bp = Blueprint("enrollment", __name__)
logger = logging.getLogger(__name__)

def get_current_user_role():
    """Get current user's role from JWT"""
    try:
        db = get_db()
        cur = db.cursor()
        identity = get_jwt_identity()
        cur.execute("SELECT role FROM users WHERE email = ?", (identity,))
        row = cur.fetchone()
        return row["role"] if row else None
    except Exception:
        return None

@enrollment_bp.route("/enroll", methods=["POST"])
@jwt_required()
def enroll_face():
    """
    Enroll a face for a user (student or teacher)
    
    Authorization:
    - Admin: Can enroll any student
    - Class Teacher: Can enroll themselves and their students
    - Regular Teacher: Cannot enroll (no permission)
    - Student: Cannot enroll
    """
    try:
        data = request.get_json() or {}

        image = data.get("image")
        images = data.get("images", []) # List of base64 images
        user_id = data.get("user_id")
        role = data.get("role")
        clear_existing = data.get("clear_existing", True) # Default to true for backward compatibility or simple enrollment

        if not image and not images:
            return jsonify({"error": "No image provided"}), 400
        if not user_id or not role:
            return jsonify({"error": "Missing user_id or role"}), 400



        # Get current user's role and email for authorization
        try:
            current_identity = get_jwt_identity()
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT role FROM users WHERE email = ?", (current_identity,))
            user_row = cur.fetchone()
            current_user_role = user_row["role"] if user_row else None
        except Exception:
            current_user_role = None

        # Authorization check
        if current_user_role == "admin":
            # Admin can enroll anyone
            pass
        elif current_user_role == "teacher":
            # Teacher can only enroll themselves or their students
            if role == "teacher":
                # Teacher enrolling themselves
                if int(user_id) != int(data.get("current_teacher_id", -1)):
                    return jsonify({"error": "You can only enroll yourself as a teacher"}), 403
            elif role == "student":
                # Class teacher can enroll their students
                cur.execute("""
                    SELECT is_class_teacher, assigned_class, assigned_section
                    FROM teachers WHERE email = ?
                """, (current_identity,))
                teacher = cur.fetchone()
                
                if not teacher or not teacher["is_class_teacher"]:
                    return jsonify({"error": "Only class teachers can enroll students"}), 403
                
                # Check if student is in teacher's class
                cur.execute("""
                    SELECT id FROM students WHERE id = ? AND class_name = ? AND section = ?
                """, (user_id, teacher["assigned_class"], teacher["assigned_section"]))
                if not cur.fetchone():
                    return jsonify({"error": "This student is not in your class"}), 403
            else:
                return jsonify({"error": "Invalid role"}), 400
        else:
            return jsonify({"error": "You don't have permission to enroll faces"}), 403

        # Lazy import to avoid TensorFlow dependency at startup
        try:
            from face_engine.encoder import generate_embedding
        except ImportError:
            from smart_school_backend.face_engine.encoder import generate_embedding
        
        all_images = []
        if image:
            all_images.append(image)
        if images:
            all_images.extend(images)

        embeddings_to_save = []
        existing_embeddings = load_all_embeddings()
        
        for img in all_images:
            emb = generate_embedding(img)
            if emb is None:
                continue
            
            # Check for existing faces (duplicate detection)
            for existing in existing_embeddings:
                # Don't flag as duplicate if it's the SAME person we are enrolling
                # (We use str() for ID because user_id might be string initially)
                if existing["role"] == role and str(existing["person_id"]) == str(user_id):
                    continue
                    
                dist = np.linalg.norm(emb - existing["embedding"])
                if dist < 0.6:
                    return jsonify({
                        "error": f"One of the face angles is already enrolled by {existing['name']} ({existing['role']}).",
                        "existing_user": {
                            "person_id": existing["person_id"],
                            "role": existing["role"],
                            "name": existing["name"]
                        }
                    }), 409
            embeddings_to_save.append(emb)

        if not embeddings_to_save:
            return jsonify({"error": "No faces detected in any of the provided images"}), 400

        conn = get_db()
        cur = conn.cursor()

        user_data = None
        numeric_user_id = None  # We'll get the actual numeric ID
        
        if role == 'student':
            # Try to find by id (numeric), id_code (string), or email (string)
            if str(user_id).isdigit():
                cur.execute("SELECT id, name, email, class_name, section FROM students WHERE id = ?", (int(user_id),))
                user_data = cur.fetchone()
            if not user_data:
                cur.execute("SELECT id, name, email, class_name, section FROM students WHERE id_code = ?", (str(user_id),))
                user_data = cur.fetchone()
            if not user_data:
                cur.execute("SELECT id, name, email, class_name, section FROM students WHERE email = ?", (str(user_id),))
                user_data = cur.fetchone()
            if user_data:
                numeric_user_id = user_data['id']
        elif role == 'teacher':
            # Try to find by id (numeric), id_code, or email
            if str(user_id).isdigit():
                cur.execute("SELECT id, name, email, subject FROM teachers WHERE id = ?", (int(user_id),))
                user_data = cur.fetchone()
            if not user_data:
                cur.execute("SELECT id, name, email, subject FROM teachers WHERE id_code = ?", (str(user_id),))
                user_data = cur.fetchone()
            if not user_data:
                cur.execute("SELECT id, name, email, subject FROM teachers WHERE email = ?", (str(user_id),))
                user_data = cur.fetchone()
            if user_data:
                numeric_user_id = user_data['id']

        # If user not found, allow admin to create a placeholder record automatically
        if not user_data:
            if current_user_role == 'admin':
                if role == 'student':
                    # create a minimal student record using id_code for correlation
                    placeholder_name = f"Enrolled_{user_id}"
                    placeholder_email = f"enroll_{user_id}@example.com"
                    # Ensure NOT NULL columns have defaults
                    cur.execute(
                        "INSERT INTO students (name, email, id_code, class_name, section) VALUES (?, ?, ?, ?, ?)",
                        (placeholder_name, placeholder_email, str(user_id), 'Unassigned', 'Unassigned')
                    )
                    conn.commit()
                    cur.execute("SELECT id, name, email, class_name, section FROM students WHERE id_code = ?", (str(user_id),))
                    user_data = cur.fetchone()
                    if user_data:
                        numeric_user_id = user_data['id']
                else:
                    # create a minimal teacher record
                    placeholder_name = f"Enrolled_{user_id}"
                    placeholder_email = f"enroll_{user_id}@example.com"
                    cur.execute(
                        "INSERT INTO teachers (name, email, id_code, subject) VALUES (?, ?, ?, ?)",
                        (placeholder_name, placeholder_email, str(user_id), 'Unknown')
                    )
                    conn.commit()
                    cur.execute("SELECT id, name, email, subject FROM teachers WHERE id_code = ?", (str(user_id),))
                    user_data = cur.fetchone()
                    if user_data:
                        numeric_user_id = user_data['id']
            else:
                return jsonify({"error": f"User with id {user_id} and role {role} not found"}), 404

        # If still no user data, error out
        if not user_data or not numeric_user_id:
            return jsonify({"error": "Could not find or create user record"}), 404

        name = user_data['name']
        email = user_data['email']
        
        if role == 'student':
            class_name = user_data['class_name']
            section = user_data['section']
        else:
            class_name = None
            section = None

        # Store embeddings
        first = True
        for emb in embeddings_to_save:
            # Clear existing ONLY on the first insertion of this batch, and only if requested
            do_clear = clear_existing if first else False
            store_face_embedding(role, numeric_user_id, name, email, 
                                class_name, section, 
                                emb, clear_existing=do_clear)
            first = False


        return jsonify({
            "status": "success",
            "message": "Face enrolled successfully",
            "person_id": numeric_user_id,
            "role": role
        })

    except Exception as e:
        logger.error(f"Enrollment error: {type(e).__name__}")
        return jsonify({"error": "Enrollment failed"}), 500


# ----------------------------------------------------------
# GET /api/enrollment/<role>/<id>
# Get enrollment details for editing
# ----------------------------------------------------------
@enrollment_bp.route("/enrollment/<role>/<int:user_id>", methods=["GET"])
@jwt_required()
def get_enrollment_details(role, user_id):
    """
    Get enrollment details for a student or teacher
    Used when editing enrollment to pre-populate the form
    
    Authorization:
    - Admin: Can view any enrollment details
    - Class Teacher: Can view their own or their students' enrollment
    - Regular Teacher: Can view only their own
    - Student: Can view only their own
    """
    try:
        current_identity = get_jwt_identity()
        db = get_db()
        cur = db.cursor()
        
        # Get current user info
        cur.execute("""
            SELECT id, role, email FROM users WHERE email = ?
        """, (current_identity,))
        current_user = cur.fetchone()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 401
        
        # Authorization check
        current_user_role = current_user["role"]
        current_user_id = current_user["id"]
        
        if current_user_role == "admin":
            # Admin can view any enrollment
            pass
        elif current_user_role == "teacher":
            if role == "teacher" and current_user_id != user_id:
                return jsonify({"error": "Teachers can only view their own enrollment"}), 403
            elif role == "student":
                # Check if class teacher
                cur.execute("""
                    SELECT is_class_teacher, assigned_class, assigned_section
                    FROM teachers WHERE id = ?
                """, (current_user_id,))
                teacher = cur.fetchone()
                if not teacher or not teacher["is_class_teacher"]:
                    return jsonify({"error": "Only class teachers can view student enrollment"}), 403
                
                # Check if student is in their class
                cur.execute("""
                    SELECT id FROM students WHERE id = ? AND class_name = ? AND section = ?
                """, (user_id, teacher["assigned_class"], teacher["assigned_section"]))
                if not cur.fetchone():
                    return jsonify({"error": "This student is not in your class"}), 403
        elif current_user_role == "student":
            if role != "student" or current_user_id != user_id:
                return jsonify({"error": "Students can only view their own enrollment"}), 403
        else:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Fetch user details based on role
        if role == "student":
            cur.execute("""
                SELECT id, name, email, id_code, class_name, section from students where id = ?
            """, (user_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({"error": "Student not found"}), 404
            
            return jsonify({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "id_code": user["id_code"],
                "class": user["class_name"],
                "section": user["section"],
                "role": "student"
            }), 200
        
        elif role == "teacher":
            cur.execute("""
                SELECT id, name, email, id_code, subject, is_class_teacher, 
                       assigned_class, assigned_section from teachers where id = ?
            """, (user_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({"error": "Teacher not found"}), 404
            
            return jsonify({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "id_code": user["id_code"],
                "subject": user["subject"],
                "is_class_teacher": bool(user["is_class_teacher"]),
                "assigned_class": user["assigned_class"],
                "assigned_section": user["assigned_section"],
                "role": "teacher"
            }), 200
        else:
            return jsonify({"error": "Invalid role"}), 400
        
    except Exception as e:
        logger.error(f"Error fetching enrollment details: {type(e).__name__}")
        return jsonify({"error": "Failed to fetch enrollment details"}), 500


# ----------------------------------------------------------
# PUT /api/enrollment/<role>/<id>
# Update enrollment details (without re-enrolling face)
# ----------------------------------------------------------
@enrollment_bp.route("/enrollment/<role>/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_enrollment_details(role, user_id):
    """
    Update enrollment details for a student or teacher
    This updates user information without requiring a new face image
    
    Authorization: Same as GET /api/enrollment/<role>/<id>
    """
    try:
        current_identity = get_jwt_identity()
        db = get_db()
        cur = db.cursor()
        
        # Get current user info
        cur.execute("""
            SELECT id, role, email FROM users WHERE email = ?
        """, (current_identity,))
        current_user = cur.fetchone()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 401
        
        # Authorization check (same as GET)
        current_user_role = current_user["role"]
        current_user_id = current_user["id"]
        
        if current_user_role == "admin":
            pass
        elif current_user_role == "teacher":
            if role == "teacher" and current_user_id != user_id:
                return jsonify({"error": "Teachers can only update their own details"}), 403
            elif role == "student":
                cur.execute("""
                    SELECT is_class_teacher, assigned_class, assigned_section
                    FROM teachers WHERE id = ?
                """, (current_user_id,))
                teacher = cur.fetchone()
                if not teacher or not teacher["is_class_teacher"]:
                    return jsonify({"error": "Only class teachers can update student details"}), 403
                
                cur.execute("""
                    SELECT id FROM students WHERE id = ? AND class_name = ? AND section = ?
                """, (user_id, teacher["assigned_class"], teacher["assigned_section"]))
                if not cur.fetchone():
                    return jsonify({"error": "This student is not in your class"}), 403
        elif current_user_role == "student":
            if role != "student" or current_user_id != user_id:
                return jsonify({"error": "Students can only update their own details"}), 403
        else:
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update based on role
        if role == "student":
            # Update student details
            updates = []
            params = []
            
            if "name" in data:
                updates.append("name = ?")
                params.append(data["name"])
            if "email" in data:
                updates.append("email = ?")
                params.append(data["email"])
            if "id_code" in data:
                updates.append("id_code = ?")
                params.append(data["id_code"])
            # Note: class and section are typically not editable after creation
            
            if not updates:
                return jsonify({"error": "No valid fields to update"}), 400
            
            params.append(user_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE id = ?"
            
            try:
                cur.execute(query, params)
                db.commit()
                return jsonify({"message": "Student details updated successfully"}), 200
            except sqlite3.IntegrityError as ie:
                if "email" in str(ie).lower():
                    return jsonify({"error": "Email already exists"}), 409
                return jsonify({"error": "Integrity error"}), 409
            
        elif role == "teacher":
            # Update teacher details
            updates = []
            params = []
            
            if "name" in data:
                updates.append("name = ?")
                params.append(data["name"])
            if "email" in data:
                updates.append("email = ?")
                params.append(data["email"])
            if "subject" in data:
                updates.append("subject = ?")
                params.append(data["subject"])
            if "id_code" in data:
                updates.append("id_code = ?")
                params.append(data["id_code"])
            
            # Note: Class teacher status and assignment changes typically need special handling
            # For now, we'll allow updating if the user has permission
            
            if not updates:
                return jsonify({"error": "No valid fields to update"}), 400
            
            params.append(user_id)
            query = f"UPDATE teachers SET {', '.join(updates)} WHERE id = ?"
            
            try:
                cur.execute(query, params)
                db.commit()
                return jsonify({"message": "Teacher details updated successfully"}), 200
            except sqlite3.IntegrityError as ie:
                if "email" in str(ie).lower():
                    return jsonify({"error": "Email already exists"}), 409
                return jsonify({"error": "Integrity error"}), 409
        else:
            return jsonify({"error": "Invalid role"}), 400
        
    except Exception as e:
        logger.error(f"Error updating enrollment details: {type(e).__name__}")
        return jsonify({"error": "Failed to update enrollment details"}), 500
