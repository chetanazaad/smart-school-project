from flask import Blueprint, jsonify
import logging
from smart_school_backend.utils.db import get_db

face_bp = Blueprint("face", __name__)
logger = logging.getLogger(__name__)

@face_bp.route("/enrolled-ids", methods=["GET"])
def get_enrolled_ids():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT student_id, teacher_id, role FROM face_embeddings")
        rows = cur.fetchall()
        enrolled_ids = []
        for row in rows:
            if row["role"] == "student":
                enrolled_ids.append(row["student_id"])
            else:
                enrolled_ids.append(row["teacher_id"])
        return jsonify({"enrolled_ids": enrolled_ids})
    except Exception as e:
        logger.error(f"Error fetching enrolled IDs: {type(e).__name__}")
        return jsonify({"error": "Failed to fetch enrolled IDs"}), 500


@face_bp.route("/enrollment-stats", methods=["GET"])
def get_enrollment_stats():
    """
    Get enrollment statistics for students and teachers.
    Returns lists of enrolled students and teachers with their details.
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Get enrolled students with their details
        cur.execute("""
            SELECT s.id, s.name, s.email, s.class_name, s.id_code, fe.id as embedding_id
            FROM students s
            INNER JOIN face_embeddings fe ON fe.student_id = s.id AND fe.role = 'student'
        """)
        enrolled_students = [dict(row) for row in cur.fetchall()]
        
        # Get enrolled teachers with their details
        cur.execute("""
            SELECT t.id, t.name, t.email, t.subject, t.id_code, fe.id as embedding_id
            FROM teachers t
            INNER JOIN face_embeddings fe ON fe.teacher_id = t.id AND fe.role = 'teacher'
        """)
        enrolled_teachers = [dict(row) for row in cur.fetchall()]
        
        # Get all students count
        cur.execute("SELECT COUNT(*) as count FROM students")
        total_students = cur.fetchone()["count"]
        
        # Get all teachers count
        cur.execute("SELECT COUNT(*) as count FROM teachers")
        total_teachers = cur.fetchone()["count"]
        
        return jsonify({
            "enrolled_students": enrolled_students,
            "enrolled_teachers": enrolled_teachers,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "students_enrolled_count": len(enrolled_students),
            "teachers_enrolled_count": len(enrolled_teachers),
            "students_not_enrolled": total_students - len(enrolled_students),
            "teachers_not_enrolled": total_teachers - len(enrolled_teachers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching enrollment stats: {type(e).__name__}")
        return jsonify({"error": "Failed to fetch enrollment stats"}), 500
