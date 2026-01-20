# smart_school_backend/routes/teachers.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import sqlite3
import os
from flask import current_app
from models.user import create_user

bp = Blueprint("teachers", __name__)

# ----------------------------------------------------------
# DB helper
# ----------------------------------------------------------
def get_db():
    try:
        from smart_school_backend.utils.db import get_db as gdb
        return gdb()
    except Exception:
        db_path = os.path.join(current_app.root_path, "..", "database", "smart_school.db")
        db_path = os.path.abspath(db_path)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


# ----------------------------------------------------------
# GET /api/teachers
# ----------------------------------------------------------
@bp.route("", methods=["GET"])
@jwt_required()
def get_all_teachers():
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT id, name, email, id_code, subject, is_class_teacher, assigned_class, assigned_section FROM teachers ORDER BY id DESC")
        rows = cur.fetchall()

        teachers = []
        for r in rows:
            teachers.append({
                "id": r["id"],
                "name": r["name"],
                "email": r["email"],
                "subject": r["subject"],
                "is_class_teacher": bool(r["is_class_teacher"]),
                "assigned_class": r["assigned_class"],
                "assigned_section": r["assigned_section"]
            })

        return jsonify({"teachers": teachers}), 200

    except Exception as e:
        print("ERROR get_all_teachers:", e)
        return jsonify({"error": "Failed to fetch teachers"}), 500


# ----------------------------------------------------------
# GET /api/teachers/count
# ----------------------------------------------------------
@bp.route("/count", methods=["GET"])
@jwt_required()
def teacher_count():
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT COUNT(*) AS total FROM teachers")
        row = cur.fetchone()

        return jsonify({"count": row["total"]}), 200

    except Exception as e:
        print("ERROR teacher_count:", e)
        return jsonify({"count": 0}), 200


# ----------------------------------------------------------
# GENERATE UNIQUE TEACHER ID
# GET /api/teachers/generate-id
# ----------------------------------------------------------
@bp.route("/generate-id", methods=["GET"])
@jwt_required()
def generate_teacher_id():
    """Generate a unique teacher ID with retry mechanism"""
    try:
        import random
        import time
        
        db = get_db()
        cur = db.cursor()
        
        # Try up to 10 times to generate unique ID
        max_attempts = 10
        for attempt in range(max_attempts):
            n = random.randint(1000, 9999)
            new_id = f"T{n}"
            
            # Check if ID exists
            cur.execute("SELECT id FROM teachers WHERE id_code = ?", (new_id,))
            if not cur.fetchone():
                print(f"[ID_GEN] Generated unique ID: {new_id} (attempt {attempt + 1})")
                return jsonify({"id_code": new_id}), 200
            
            # If collision, sleep briefly then retry
            if attempt < max_attempts - 1:
                time.sleep(0.01 * (attempt + 1))
        
        # If we get here, couldn't generate unique ID
        print(f"[ID_GEN] FAILED to generate unique ID after {max_attempts} attempts")
        return jsonify({"error": "Could not generate unique teacher ID. Too many collisions."}), 500
    except Exception as e:
        print("ERROR generate_teacher_id:", e)
        return jsonify({"error": "Failed to generate ID"}), 500


# ----------------------------------------------------------
# CREATE TEACHER
# POST /api/teachers
# ----------------------------------------------------------
@bp.route("", methods=["POST"])
@jwt_required()
def create_teacher():
    try:
        data = request.get_json() or {}
        id_code = data.get("id_code")
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        password = data.get("password")
        is_class_teacher = data.get("is_class_teacher", 0)
        assigned_class = data.get("assigned_class")
        assigned_section = data.get("assigned_section")

        print(f"[CREATE_TEACHER] Attempt: name={name}, email={email}, id_code={id_code}")

        if not name or not email:
            return jsonify({"error": "name and email required"}), 400

        # If marking as class teacher, class and section must be provided
        if is_class_teacher and (not assigned_class or not assigned_section):
            return jsonify({"error": "Class and section required for class teachers"}), 400

        db = get_db()
        cur = db.cursor()
        
        # Check if teacher with this email already exists
        cur.execute("SELECT id FROM teachers WHERE email = ?", (email,))
        if cur.fetchone():
            print(f"[CREATE_TEACHER] ERROR: Teacher with email {email} already exists")
            return jsonify({"error": "Teacher with this email already exists"}), 409
        
        # Check if user with this email already exists (if password provided)
        if password:
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                print(f"[CREATE_TEACHER] ERROR: User with email {email} already exists")
                return jsonify({"error": "User account with this email already exists"}), 409
        
        # Create teacher record
        if id_code:
            cur.execute(
                "INSERT INTO teachers (name, email, id_code, subject, is_class_teacher, assigned_class, assigned_section) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, email, id_code, subject, int(is_class_teacher), assigned_class, assigned_section)
            )
        else:
            cur.execute(
                "INSERT INTO teachers (name, email, subject, is_class_teacher, assigned_class, assigned_section) VALUES (?, ?, ?, ?, ?, ?)",
                (name, email, subject, int(is_class_teacher), assigned_class, assigned_section)
            )
        db.commit()
        teacher_id = cur.lastrowid

        # Create user account if password provided
        if password:
            try:
                user_id = create_user(name=name, email=email, password=password, role="teacher")
                return jsonify({"message": "Teacher created with login credentials", "id": teacher_id, "user_id": user_id, "is_class_teacher": bool(is_class_teacher)}), 201
            except Exception as user_err:
                # Teacher created but user creation failed - rollback teacher creation
                print(f"ERROR: User creation failed after teacher created: {user_err}")
                cur.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                db.commit()
                return jsonify({"error": "Failed to create user account. Teacher creation rolled back."}), 500
        else:
            return jsonify({"message": "Teacher created", "id": teacher_id, "is_class_teacher": bool(is_class_teacher)}), 201
            
    except Exception as e:
        print("ERROR create_teacher:", e)
        return jsonify({"error": "Failed to create teacher"}), 500


# ----------------------------------------------------------
# GET /api/teachers/<id>
# ----------------------------------------------------------
@bp.route("/<int:teacher_id>", methods=["GET"])
@jwt_required()
def get_teacher(teacher_id):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, name, email, id_code, subject, is_class_teacher, assigned_class, assigned_section FROM teachers WHERE id=?", (teacher_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        
        teacher_data = dict(row)
        teacher_data["is_class_teacher"] = bool(teacher_data["is_class_teacher"])
        
        return jsonify({"teacher": teacher_data}), 200
    except Exception as e:
        print("ERROR get_teacher:", e)
        return jsonify({"error": "Failed to load teacher"}), 500


# ----------------------------------------------------------
# UPDATE /api/teachers/<id>
# ----------------------------------------------------------
@bp.route("/<int:teacher_id>", methods=["PUT"])
@jwt_required()
def update_teacher(teacher_id):
    try:
        data = request.get_json() or {}
        id_code = data.get("id_code")
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        is_class_teacher = data.get("is_class_teacher")
        assigned_class = data.get("assigned_class")
        assigned_section = data.get("assigned_section")

        db = get_db()
        cur = db.cursor()
        
        # If updating class teacher status and marking as true, require class/section
        if is_class_teacher and (not assigned_class or not assigned_section):
            return jsonify({"error": "Class and section required for class teachers"}), 400
        
        # Build update query
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name=?")
            params.append(name)
        if email is not None:
            update_fields.append("email=?")
            params.append(email)
        if subject is not None:
            update_fields.append("subject=?")
            params.append(subject)
        if id_code is not None:
            update_fields.append("id_code=?")
            params.append(id_code)
        if is_class_teacher is not None:
            update_fields.append("is_class_teacher=?")
            params.append(int(is_class_teacher))
        if assigned_class is not None:
            update_fields.append("assigned_class=?")
            params.append(assigned_class)
        if assigned_section is not None:
            update_fields.append("assigned_section=?")
            params.append(assigned_section)
        
        if not update_fields:
            return jsonify({"message": "No updates provided"}), 200
        
        params.append(teacher_id)
        query = "UPDATE teachers SET " + ", ".join(update_fields) + " WHERE id=?"
        cur.execute(query, params)
        db.commit()
        
        return jsonify({"message": "Teacher updated"}), 200
    except Exception as e:
        print("ERROR update_teacher:", e)
        return jsonify({"error": "Failed to update teacher"}), 500


# ----------------------------------------------------------
# DELETE /api/teachers/<id>
# ----------------------------------------------------------
@bp.route("/<int:teacher_id>", methods=["DELETE"])
@jwt_required()
def delete_teacher(teacher_id):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
        cur.execute("DELETE FROM face_embeddings WHERE person_id=? AND role='teacher'", (teacher_id,))
        db.commit()
        return jsonify({"message": "Teacher deleted"}), 200
    except Exception as e:
        print("ERROR delete_teacher:", e)
        return jsonify({"error": "Failed to delete teacher"}), 500


# ----------------------------------------------------------
# GET /api/teachers/<id>/dashboard
# Class teacher dashboard with students and timetable
# ----------------------------------------------------------
@bp.route("/<int:teacher_id>/dashboard", methods=["GET"])
@jwt_required()
def teacher_dashboard(teacher_id):
    """
    Get class teacher dashboard with:
    - Teacher info
    - Enrolled students in their class
    - Class timetable
    - Teacher timetable
    """
    try:
        db = get_db()
        cur = db.cursor()
        
        # Get teacher info
        cur.execute("""
            SELECT id, name, email, subject, is_class_teacher, assigned_class, assigned_section 
            FROM teachers WHERE id=?
        """, (teacher_id,))
        teacher = cur.fetchone()
        
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404
        
        if not teacher["is_class_teacher"]:
            return jsonify({"error": "Only class teachers can access this dashboard"}), 403
        
        teacher_data = dict(teacher)
        teacher_data["is_class_teacher"] = bool(teacher_data["is_class_teacher"])
        
        # Get enrolled students in teacher's class
        cur.execute("""
            SELECT id, name, email, id_code, class_name, section
            FROM students 
            WHERE class_name = ? AND section = ?
            ORDER BY name
        """, (teacher["assigned_class"], teacher["assigned_section"]))
        students = [dict(row) for row in cur.fetchall()]
        
        # Get class timetable
        cur.execute("""
            SELECT id, day, subject, teacher_name, start_time, end_time
            FROM timetable
            WHERE class_name = ? AND section = ?
            ORDER BY CASE 
                WHEN day='Monday' THEN 1
                WHEN day='Tuesday' THEN 2
                WHEN day='Wednesday' THEN 3
                WHEN day='Thursday' THEN 4
                WHEN day='Friday' THEN 5
                WHEN day='Saturday' THEN 6
                WHEN day='Sunday' THEN 7
            END, start_time
        """, (teacher["assigned_class"], teacher["assigned_section"]))
        class_timetable = [dict(row) for row in cur.fetchall()]
        
        # Get teacher's personal timetable
        cur.execute("""
            SELECT id, day, class_name, section, subject, start_time, end_time
            FROM timetable
            WHERE teacher_name = ?
            ORDER BY CASE 
                WHEN day='Monday' THEN 1
                WHEN day='Tuesday' THEN 2
                WHEN day='Wednesday' THEN 3
                WHEN day='Thursday' THEN 4
                WHEN day='Friday' THEN 5
                WHEN day='Saturday' THEN 6
                WHEN day='Sunday' THEN 7
            END, start_time
        """, (teacher["name"],))
        teacher_timetable = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            "teacher": teacher_data,
            "enrolled_students": students,
            "class_timetable": class_timetable,
            "teacher_timetable": teacher_timetable
        }), 200
        
    except Exception as e:
        print("ERROR teacher_dashboard:", e)
        return jsonify({"error": "Failed to fetch dashboard"}), 500


# ----------------------------------------------------------
# GET /api/teachers/<id>/enrolled-students
# Get list of enrolled students for class teacher
# ----------------------------------------------------------
@bp.route("/<int:teacher_id>/enrolled-students", methods=["GET"])
@jwt_required()
def get_enrolled_students(teacher_id):
    """
    Get all students enrolled in the class teacher's class
    """
    try:
        db = get_db()
        cur = db.cursor()
        
        # Get teacher info (verify is class teacher)
        cur.execute("""
            SELECT id, is_class_teacher, assigned_class, assigned_section
            FROM teachers WHERE id=?
        """, (teacher_id,))
        teacher = cur.fetchone()
        
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404
        
        if not teacher["is_class_teacher"]:
            return jsonify({"error": "Only class teachers can view enrolled students"}), 403
        
        # Get students in teacher's class
        cur.execute("""
            SELECT id, name, email, id_code, class_name, section
            FROM students
            WHERE class_name = ? AND section = ?
            ORDER BY name
        """, (teacher["assigned_class"], teacher["assigned_section"]))
        students = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            "class": teacher["assigned_class"],
            "section": teacher["assigned_section"],
            "total_students": len(students),
            "students": students
        }), 200
        
    except Exception as e:
        print("ERROR get_enrolled_students:", e)
        return jsonify({"error": "Failed to fetch students"}), 500


# ----------------------------------------------------------
# GET /api/teachers/<id>/attendance
# Mark attendance (Regular teachers only - no enrollment UI)
# ----------------------------------------------------------
@bp.route("/<int:teacher_id>/attendance", methods=["GET"])
@jwt_required()
def get_teacher_attendance(teacher_id):
    """
    Get attendance marking page for regular teachers (non-class-teachers)
    Regular teachers can only mark their own attendance, not enroll students
    
    This endpoint is used by the frontend to display attendance-only interface
    without enrollment options
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        
        db = get_db()
        cur = db.cursor()
        
        # Get current user for authorization
        current_identity = get_jwt_identity()
        cur.execute("SELECT id, role FROM users WHERE email = ?", (current_identity,))
        current_user = cur.fetchone()
        
        if not current_user or current_user["role"] != "teacher":
            return jsonify({"error": "Only teachers can access this"}), 403
        
        # Get teacher info
        cur.execute("""
            SELECT id, name, email, subject, is_class_teacher
            FROM teachers WHERE id=?
        """, (teacher_id,))
        teacher = cur.fetchone()
        
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404
        
        # Users can only access their own attendance page
        if current_user["id"] != teacher_id and current_user["role"] != "admin":
            return jsonify({"error": "You can only mark your own attendance"}), 403
        
        # Regular teachers: is_class_teacher should be 0
        # Class teachers use the dashboard endpoint instead
        if teacher["is_class_teacher"]:
            return jsonify({
                "message": "Class teachers use /api/teachers/<id>/dashboard instead",
                "endpoint": "/api/teachers/<id>/dashboard"
            }), 400
        
        # Return teacher info for attendance marking
        return jsonify({
            "id": teacher["id"],
            "name": teacher["name"],
            "email": teacher["email"],
            "subject": teacher["subject"],
            "is_class_teacher": bool(teacher["is_class_teacher"]),
            "can_enroll": False,  # Regular teachers cannot enroll
            "attendance_only": True
        }), 200
        
    except Exception as e:
        print("ERROR get_teacher_attendance:", e)
        return jsonify({"error": "Failed to fetch attendance info"}), 500
