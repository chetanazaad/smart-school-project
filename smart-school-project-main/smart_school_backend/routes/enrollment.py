from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
import json
import os
import sqlite3

from smart_school_backend.utils.db import get_db
from smart_school_backend.face_engine.encoder import generate_embedding
from smart_school_backend.models.face_recognition import store_face_embedding, load_all_embeddings

enrollment_bp = Blueprint("enrollment", __name__)

def get_current_user_role():
    """Get current user's role from JWT"""
    try:
        from smart_school_backend.utils.db import get_db as gdb
        db = gdb()
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
        data = request.json

        image = data.get("image")
        user_id = data.get("user_id")
        role = data.get("role")

        if not image or not user_id or not role:
            return jsonify({"error": "Missing required fields"}), 400

        # Get current user's role and email for authorization
        try:
            current_identity = get_jwt_identity()
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT role FROM users WHERE email = ?", (current_identity,))
            user_row = cur.fetchone()
            current_user_role = user_row["role"] if user_row else None
            print(f"[FACE ENROLL] JWT Identity: {current_identity}, Role: {current_user_role}")
        except Exception as e:
            print(f"[FACE ENROLL] Error getting user role: {e}")
            current_user_role = None

        # Authorization check
        if current_user_role == "admin":
            # Admin can enroll anyone
            print(f"[FACE ENROLL] Admin authorization passed")
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
            print(f"[FACE ENROLL] Unauthorized - Role: {current_user_role}")
            return jsonify({"error": "Unauthorized", "details": f"Role {current_user_role} cannot enroll faces"}), 403

        embedding = generate_embedding(image)
        if embedding is None:
            return jsonify({"error": "No face detected"}), 400

        # Check for existing faces
        existing_embeddings = load_all_embeddings()
        for existing in existing_embeddings:
            dist = np.linalg.norm(embedding - existing["embedding"])
            if dist < 0.6:
                return jsonify({
                    "error": "This face is already enrolled.",
                    "existing_user": {
                        "person_id": existing["person_id"],
                        "role": existing["role"],
                        "name": existing["name"]
                    }
                }), 409

        conn = get_db()
        cur = conn.cursor()

        user_data = None
        if role == 'student':
            cur.execute("SELECT name, email, class_name, section FROM students WHERE id = ?", (user_id,))
            user_data = cur.fetchone()
        elif role == 'teacher':
            cur.execute("SELECT name, email, subject FROM teachers WHERE id = ?", (user_id,))
            user_data = cur.fetchone()

        if not user_data:
            return jsonify({"error": f"User with id {user_id} and role {role} not found"}), 404

        name = user_data['name']
        email = user_data['email']
        
        if role == 'student':
            class_name = user_data['class_name']
            section = user_data['section']
        else:
            class_name = None
            section = None

        # Use the imported function to store the embedding
        store_face_embedding(role, user_id, name, email, class_name, section, embedding)

        print(f"Successfully enrolled face for person_id: {user_id}, role: {role}")
        return jsonify({
            "status": "success",
            "message": "Face enrolled successfully",
            "person_id": user_id,
            "role": role
        })

    except Exception as e:
        print("Enroll error:", e)
        import traceback
        traceback.print_exc()
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
                SELECT id, name, email, id_code, class_name, section FROM students WHERE id = ?
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
                       assigned_class, assigned_section FROM teachers WHERE id = ?
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
        print("Get enrollment details error:", e)
        import traceback
        traceback.print_exc()
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
        print("Update enrollment details error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to update enrollment details"}), 500
