from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import sqlite3
import os
import sys
import logging

# Fix imports to work from any directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from utils.db import get_db
    from models.user import create_user
except ImportError:
    from smart_school_backend.utils.db import get_db
    from smart_school_backend.models.user import create_user

bp = Blueprint("students", __name__)
logger = logging.getLogger(__name__)

# Using get_db from smart_school_backend.utils.db


# ============================================================
# 1) GET ALL STUDENTS (FIX FOR STUDENTS PAGE)
# ============================================================
@bp.route("", methods=["GET"])
@jwt_required()
def get_students():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, id_code, roll_number, class_name, section FROM students ORDER BY id DESC")
        rows = cur.fetchall()

        students = [dict(row) for row in rows]

        return jsonify({
            "students": students,
            "count": len(students)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching students: {type(e).__name__}")
        return jsonify({"error": "Failed to load students"}), 500


# ----------------------------------------------------------
# GENERATE UNIQUE STUDENT ID
# GET /api/students/generate-id
# ----------------------------------------------------------
@bp.route("/generate-id", methods=["GET"])
@jwt_required()
def generate_student_id():
    """Generate a unique student ID with format ST1001"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id_code FROM students WHERE id_code LIKE 'ST%'")
        rows = cur.fetchall()
        
        max_num = 0
        for row in rows:
            try:
                num = int(row["id_code"][2:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
                
        new_id = f"ST{max_num + 1:04d}"  # Format: ST0001, ST0002, etc. (Can keep 4 digits or use 3)
        return jsonify({"id_code": new_id}), 200

    except Exception as e:
        logger.error(f"Error generating student ID: {type(e).__name__}")
        return jsonify({"error": "Failed to generate ID"}), 500


# ----------------------------------------------------------
# CREATE STUDENT
# POST /api/students
# ----------------------------------------------------------
@bp.route("", methods=["POST"])
@jwt_required()
def create_student():
    try:
        data = request.get_json() or {}
        name = data.get("name")
        id_code = data.get("id_code")
        roll_number = data.get("roll_number")
        email = data.get("email")
        class_name = data.get("class_name")
        section = data.get("section")
        password = data.get("password")

        if not name or not email:
            return jsonify({"error": "name and email required"}), 400

        conn = get_db()
        cur = conn.cursor()
        
        # FORCE CLEANUP: If there is a user account but NO profile, delete it immediately.
        # This handles cases where a previous registration was partially successful.
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            cur.execute("SELECT id FROM students WHERE email = ?", (email,))
            if not cur.fetchone():
                cur.execute("SELECT id FROM teachers WHERE email = ?", (email,))
                if not cur.fetchone():
                    logger.warning(f"Forced cleanup of orphan user: {email}")
                    cur.execute("DELETE FROM users WHERE email = ?", (email,))
                    conn.commit()

        # Check if student already exists
        cur.execute("SELECT id FROM students WHERE email = ?", (email,))
        if cur.fetchone():
            return jsonify({"error": "Student with this email already exists in the system."}), 409
            
        # Create student record
        if id_code:
            cur.execute("INSERT INTO students (name, email, id_code, roll_number, class_name, section) VALUES (?, ?, ?, ?, ?, ?)",
                        (name, email, id_code, roll_number, class_name, section))
        else:
            cur.execute("INSERT INTO students (name, email, roll_number, class_name, section) VALUES (?, ?, ?, ?, ?)",
                        (name, email, roll_number, class_name, section))
        student_id = cur.lastrowid

        # Create user account if password provided
        if password:
            try:
                user_id = create_user(name=name, email=email, password=password, role="student")
                conn.commit()
                return jsonify({"message": "Student created with login credentials", "id": student_id, "user_id": user_id}), 201
            except Exception as user_err:
                # If student created but user creation failed, we should rollback student creation for consistency
                logger.error(f"User creation failed after student created: {type(user_err).__name__}")
                cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
                conn.commit()
                return jsonify({"error": f"Failed to create user account: {str(user_err)}"}), 500
        else:
            conn.commit()
            return jsonify({"message": "Student created", "id": student_id}), 201
            
    except Exception as e:
        logger.error(f"Error creating student: {type(e).__name__}")
        return jsonify({"error": "Failed to create student"}), 500


# ----------------------------------------------------------
# GET /api/students/<id>
# ----------------------------------------------------------
@bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, id_code, roll_number, class_name, section FROM students WHERE id=?", (student_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"student": dict(row)}), 200
    except Exception as e:
        logger.error(f"Error fetching student: {type(e).__name__}")
        return jsonify({"error": "Failed to load student"}), 500


# ----------------------------------------------------------
# UPDATE /api/students/<id>
# ----------------------------------------------------------
@bp.route("/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    try:
        data = request.get_json() or {}
        name = data.get("name")
        id_code = data.get("id_code")
        roll_number = data.get("roll_number")
        email = data.get("email")
        class_name = data.get("class_name")
        section = data.get("section")
        password = data.get("password")

        conn = get_db()
        cur = conn.cursor()
        
        # Get old email to sync with users table
        cur.execute("SELECT email FROM students WHERE id=?", (student_id,))
        old_data = cur.fetchone()
        old_email = old_data["email"] if old_data else None

        # Update student table
        if id_code is not None:
            cur.execute("UPDATE students SET name=?, email=?, id_code=?, roll_number=?, class_name=?, section=? WHERE id=?",
                        (name, email, id_code, roll_number, class_name, section, student_id))
        else:
            cur.execute("UPDATE students SET name=?, email=?, roll_number=?, class_name=?, section=? WHERE id=?",
                        (name, email, roll_number, class_name, section, student_id))
        
        # Sync with users table
        if old_email:
            from models.user import update_user_profile
            update_user_profile(old_email, name=name, new_email=email, password=password)

        conn.commit()
        return jsonify({"message": "Student updated"}), 200
    except Exception as e:
        logger.error(f"Error updating student: {type(e).__name__} - {e}")
        return jsonify({"error": "Failed to update student"}), 500


# ----------------------------------------------------------
# DELETE /api/students/<id>
# ----------------------------------------------------------
@bp.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        # Get student email first for user cleanup
        cur.execute("SELECT email FROM students WHERE id=?", (student_id,))
        student = cur.fetchone()
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        email = student["email"]

        # Manually delete dependent records to handle databases without ON DELETE CASCADE
        cur.execute("DELETE FROM student_attendance WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM face_embeddings WHERE student_id=? AND role='student'", (student_id,))

        cur.execute("DELETE FROM students WHERE id=?", (student_id,))
        
        if email:
            try:
                # Use the database session we already have
                from models.user import delete_user_by_email
                delete_user_by_email(email)
                logger.info(f"Successfully deleted associated user for email: {email}")
            except Exception as user_err:
                logger.warning(f"Failed to delete student user account for {email}: {user_err}")
                
        conn.commit()
        return jsonify({"message": "Student and associated user account permanently deleted"}), 200
            
    except Exception as e:
        logger.error(f"Error deleting student: {type(e).__name__}")
        return jsonify({"error": "Failed to delete student"}), 500


# ============================================================
# 2) GET STUDENT COUNT  (Dashboard)
# ============================================================
@bp.route("/count", methods=["GET"])
@jwt_required()
def get_student_count():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM students")
        row = cur.fetchone()
        return jsonify({"count": row["total"]}), 200
    except Exception as e:
        logger.error(f"Error getting student count: {type(e).__name__}")
        return jsonify({"count": 0}), 200


# ============================================================
# 3) GET CLASS-WISE COUNT (Dashboard)
# ============================================================
@bp.route("/class-count", methods=["GET"])
@jwt_required()
def class_count():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT class_name, COUNT(*) AS count
            FROM students
            GROUP BY class_name
            ORDER BY class_name
        """)
        rows = cur.fetchall()
        data = [dict(r) for r in rows]
        return jsonify({"count": len(data), "data": data}), 200
    except Exception as e:
        logger.error(f"Error getting class count: {type(e).__name__}")
        return jsonify({"count": 0, "data": []}), 200
