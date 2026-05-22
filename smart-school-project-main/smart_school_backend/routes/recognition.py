from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3
import numpy as np
import logging
try:
    from smart_school_backend.utils.db import get_db
except ImportError:
    from utils.db import get_db

try:
    from smart_school_backend.routes.student_attendance import (
        _mark_student_attendance_helper,
    )
except ImportError:
    from routes.student_attendance import (
        _mark_student_attendance_helper,
    )

# NOTE: face_engine.encoder is imported lazily in functions to avoid TensorFlow dependency
recognition_bp = Blueprint("recognition", __name__)
logger = logging.getLogger(__name__)

@recognition_bp.route("/recognize", methods=["POST"])
@jwt_required()
def recognize_face():
    """
    Recognize a face from image
    
    Authorization:
    - Admin: Can recognize any face
    - Class Teacher: Can recognize themselves and their students only
    - Regular Teacher: Can recognize themselves only
    """
    try:
        data = request.get_json() or {}
        image_base64 = data.get("image_base64")

        if not image_base64:
            return jsonify({"error": "Image is required"}), 400

        # Get current user for authorization
        current_identity = get_jwt_identity()
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT role FROM users WHERE email = ?", (current_identity,))
        user_row = cur.fetchone()
        current_user_role = user_row["role"] if user_row else None

        # Lazy import to avoid TensorFlow dependency at startup
        from smart_school_backend.face_engine.encoder import generate_embedding
        
        embedding = generate_embedding(image_base64)
        if embedding is None:
            return jsonify({"match": False, "message": "No face detected"}), 200

        conn = get_db()
        cur = conn.cursor()

        # Query uses student_id/teacher_id instead of person_id
        rows = cur.execute("""
            SELECT role, student_id, teacher_id, embedding
            FROM face_embeddings
        """).fetchall()

        best_match = None
        min_distance = 0.68  # threshold for cosine distance

        for i, row in enumerate(rows):
            # Get the correct person_id based on role
            if row["role"] == "student":
                person_id = row["student_id"]
            else:
                person_id = row["teacher_id"]
            
            embedding_blob = row["embedding"]
            
            if embedding_blob is None:
                continue
            
            db_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            
            # Normalize embeddings for cosine similarity calculation
            embedding_norm = embedding / np.linalg.norm(embedding)
            db_embedding_norm = db_embedding / np.linalg.norm(db_embedding)
            
            # Calculate cosine similarity and distance
            similarity = np.dot(embedding_norm, db_embedding_norm)
            dist = 1 - similarity

            if dist < min_distance:
                min_distance = dist
                best_match = {
                    "role": row["role"],
                    "person_id": person_id,
                    "embedding": embedding_blob
                }

        if not best_match:
            return jsonify({"match": False}), 200

        person_id = best_match["person_id"]
        role = best_match["role"]

        # The person_id is the database primary key (integer)
        # Authorization check
        if current_user_role != "admin":
            if current_user_role == "teacher":
                cur.execute("SELECT id, id_code, is_class_teacher, assigned_class, assigned_section FROM teachers WHERE email = ?", (current_identity,))
                teacher = cur.fetchone()
                
                if role == "teacher":
                    if teacher is None or teacher["id"] != person_id:
                        return jsonify({"error": "You can only recognize yourself"}), 403
                elif role == "student":
                    if not teacher or not teacher["is_class_teacher"]:
                        return jsonify({"error": "Only class teachers can recognize students"}), 403
                    
                    cur.execute("SELECT id FROM students WHERE id = ? AND class_name = ? AND section = ?", (person_id, teacher["assigned_class"], teacher["assigned_section"]))
                    if not cur.fetchone():
                        return jsonify({"error": "This student is not in your class"}), 403
                else:
                    return jsonify({"error": "Invalid role"}), 400
            else:
                return jsonify({"error": "Unauthorized"}), 403

        # Fetch user details for matched person
        if role == "student":
            user = cur.execute("SELECT id, name FROM students WHERE id = ?", (person_id,)).fetchone()
        elif role == "teacher":
            user = cur.execute("SELECT id, name FROM teachers WHERE id = ?", (person_id,)).fetchone()
        else:
            return jsonify({"match": False, "message": "Unknown role"}), 200

        if user is None:
            return jsonify({"match": False, "message": "User not found"}), 200

        # Automatically mark attendance
        if role == "student":
            logger.info(f"Recognition success: Student {user['name']} (ID: {user['id']})")
            success, message = _mark_student_attendance_helper(user["id"])
            if not success:
                logger.warning(f"Auto student attendance failed: {message}")
        elif role == "teacher":
            logger.info(f"Recognition success: Teacher {user['name']} (ID: {user['id']})")
            # Lazy import to avoid circular dependency
            try:
                try:
                    from smart_school_backend.routes.teacher_attendance import _mark_teacher_attendance_helper
                except ImportError:
                    from routes.teacher_attendance import _mark_teacher_attendance_helper
                
                success, message = _mark_teacher_attendance_helper(user["id"])
                if not success:
                    logger.warning(f"Auto teacher attendance failed: {message}")
            except ImportError as ie:
                logger.error(f"Could not import teacher attendance helper: {ie}")

        return jsonify({
            "match": True,
            "id": user["id"],
            "name": user["name"],
            "role": role,
            "distance": float(min_distance)
        })

    except Exception as e:
        logger.error(f"Recognition error: {type(e).__name__}")
        return jsonify({"error": "Recognition failed due to an unexpected server error"}), 500
