# smart_school_backend/routes/timetable.py

from flask import Blueprint, request, jsonify, current_app
from smart_school_backend.utils.db import get_db
from flask_jwt_extended import jwt_required
from datetime import datetime, date as date_module

bp = Blueprint("timetable", __name__)

# ------------------------------
# Get Timetable of a Class
# ------------------------------
@bp.route("/<class_name>/<section>", methods=["GET"])
@jwt_required()
def get_timetable(class_name, section):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id, class_name, section, subject, teacher_name, day, start_time, end_time "
        "FROM timetable WHERE class_name = ? AND section = ?",
        (class_name, section),
    )
    rows = cursor.fetchall()

    timetable = [
        {
            "id": r[0],
            "class_name": r[1],
            "section": r[2],
            "subject": r[3],
            "teacher_name": r[4],
            "day": r[5],
            "start_time": r[6],
            "end_time": r[7],
        }
        for r in rows
    ]

    return jsonify({"timetable": timetable}), 200


# ------------------------------
# Get Current Class for Student (Substitute Video Feature)
# ------------------------------
@bp.route("/student/<int:student_id>/current-class", methods=["GET"])
@jwt_required()
def get_student_current_class(student_id):
    db = get_db()
    cursor = db.cursor()
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time_str = now.strftime("%H:%M")
    
    try:
        # Get student's class and section
        cursor.execute("SELECT class_name, section FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student or not student["class_name"]:
            return jsonify({"has_class": False, "message": "No class assigned to student"}), 200
            
        class_name = student["class_name"]
        section = student["section"]
        
        # Check timetable for current class
        cursor.execute(
            """
            SELECT subject, teacher_name, start_time, end_time
            FROM timetable
            WHERE class_name = ? AND section = ? AND day = ?
            AND start_time <= ? AND end_time >= ?
            """,
            (class_name, section, current_day, current_time_str, current_time_str),
        )
        timetable_entry = cursor.fetchone()
        
        if not timetable_entry:
            return jsonify({"has_class": False, "message": "No class scheduled at this time"}), 200
            
        teacher_name = timetable_entry["teacher_name"]
        subject = timetable_entry["subject"]
        
        # Find teacher by name
        cursor.execute("SELECT id FROM teachers WHERE name = ?", (teacher_name,))
        teacher = cursor.fetchone()
        
        teacher_present = False
        if teacher:
            today_str = now.strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT status FROM teacher_attendance WHERE teacher_id = ? AND date = ?",
                (teacher["id"], today_str),
            )
            attendance = cursor.fetchone()
            if attendance and attendance["status"] == "present":
                teacher_present = True

        SUBJECT_VIDEOS = {
            "Math": "https://www.youtube.com/embed/gZaOd1V0_3w",
            "Mathematics": "https://www.youtube.com/embed/gZaOd1V0_3w",
            "Physics": "https://www.youtube.com/embed/b1t41Q3xRM8",
            "Chemistry": "https://www.youtube.com/embed/7D51KSyvjBg",
            "Biology": "https://www.youtube.com/embed/31n63L317l8",
            "English": "https://www.youtube.com/embed/9a62O4PZg-U",
            "History": "https://www.youtube.com/embed/yvD9T-Q1oT8",
            "Geography": "https://www.youtube.com/embed/sSUnkC7bTsc",
            "Computer Science": "https://www.youtube.com/embed/zojyEvNW_vI",
            "Science": "https://www.youtube.com/embed/7D51KSyvjBg"
        }
        
        video_url = SUBJECT_VIDEOS.get(subject, "https://www.youtube.com/embed/zojyEvNW_vI")
        
        return jsonify({
            "has_class": True,
            "subject": subject,
            "teacher_name": teacher_name,
            "teacher_present": teacher_present,
            "start_time": timetable_entry["start_time"],
            "end_time": timetable_entry["end_time"],
            "video_url": video_url
        }), 200
        
    except Exception as e:
        current_app.logger.error("get_student_current_class failed: %s", e)
        return jsonify({"has_class": False, "error": "Failed to fetch current class"}), 500


# ------------------------------
# Add Timetable Entry (Admin Dashboard)
# ------------------------------
@bp.route("/add", methods=["POST"])
@jwt_required()
def add_timetable():
    """
    Add a timetable entry. Used by admin dashboard.
    
    POST /api/timetable/add
    
    Request body: {
        "class_name": "10",
        "section": "A",
        "subject": "Math",
        "teacher_name": "Ratan",
        "day": "Monday",
        "start_time": "09:00",
        "end_time": "09:40"
    }
    """
    data = request.json

    required = ["class_name", "section", "subject", "teacher_name", "day", "start_time", "end_time"]

    if not all(k in data and data[k] for k in required):
        return jsonify({"error": "All fields are required: " + ", ".join(required)}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO timetable (class_name, section, subject, teacher_name, day, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["class_name"],
                data["section"],
                data["subject"],
                data["teacher_name"],
                data["day"],
                data["start_time"],
                data["end_time"],
            ),
        )

        db.commit()
        return jsonify({"message": "Timetable entry added successfully", "id": cursor.lastrowid}), 201
    except Exception as e:
        current_app.logger.error("add_timetable failed: %s", e)
        return jsonify({"error": "Failed to add timetable entry"}), 500


# ------------------------------
# Delete a timetable entry
# ------------------------------
@bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_timetable_entry(entry_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM timetable WHERE id = ?", (entry_id,))
    db.commit()

    return jsonify({"message": "Timetable entry removed successfully"}), 200


# -------------------------------------------------------------------
# TEACHER DASHBOARD → TIMETABLE FOR TODAY
# -------------------------------------------------------------------
@bp.route("/teacher/<int:teacher_id>/today", methods=["GET"])
@jwt_required()
def teacher_timetable_today(teacher_id):
    """
    Get count of classes a teacher has today.
    GET /api/timetable/teacher/{id}/today

    Returns: { "count": 5 }
    """
    # Map day of week to name
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    today_name = days[date_module.today().weekday()]

    db = get_db()
    cursor = db.cursor()

    try:
        # Get teacher name
        cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            return jsonify({"count": 0}), 200
            
        teacher_name = teacher[0]

        # Count classes for this teacher today
        cursor.execute(
            "SELECT COUNT(*) FROM timetable WHERE day = ? AND teacher_name = ?",
            (today_name, teacher_name),
        )
        count = cursor.fetchone()[0] or 0
    except Exception as e:
        current_app.logger.warning("teacher_timetable_today failed: %s", e)
        count = 0

    return jsonify({"count": count}), 200


# -------------------------------------------------------------------
# TEACHER DASHBOARD → TODAY'S ATTENDANCE (PLACEHOLDER)
# -------------------------------------------------------------------
@bp.route("/teacher/<int:teacher_id>/attendance/today", methods=["GET"])
@jwt_required()
def teacher_attendance_today(teacher_id):
    """
    Get count of students present from the teacher's classes today.
    GET /api/attendance/teacher/{id}/today

    Returns: { "present": 5 }
    """
    from datetime import date as date_module
    
    today = date_module.today().strftime("%Y-%m-%d")
    db = get_db()
    cursor = db.cursor()

    try:
        # Get teacher class info
        cursor.execute("SELECT is_class_teacher, assigned_class, assigned_section FROM teachers WHERE id=?", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            return jsonify({"present": 0}), 200

        if teacher["is_class_teacher"] and teacher["assigned_class"]:
            # Count only their students
            cursor.execute(
                """
                SELECT COUNT(*) FROM student_attendance sa
                JOIN students s ON s.id = sa.student_id
                WHERE sa.date = ? AND sa.status = 'present'
                AND s.class_name = ? AND s.section = ?
                """,
                (today, teacher["assigned_class"], teacher["assigned_section"]),
            )
        else:
            # Regular teacher or missing class info
            cursor.execute(
                "SELECT COUNT(*) FROM student_attendance WHERE date = ? AND status = 'present'",
                (today,),
            )
        present = cursor.fetchone()[0] or 0
    except Exception as e:
        current_app.logger.warning("teacher_attendance_today failed: %s", e)
        present = 0

    return jsonify({"present": present}), 200


# -------------------------------------------------------------------
# STUDENT DASHBOARD → GET TIMETABLE FOR THE WEEK
# -------------------------------------------------------------------
@bp.route("/student/<int:student_id>/week", methods=["GET"])
@jwt_required()
def get_student_timetable(student_id):
    """
    Get timetable for a student for the entire week.
    The student's class and section are retrieved from the students table.
    Returns timetable entries sorted by day and time.
    
    GET /api/timetable/student/{student_id}/week
    
    Returns: {
        "student_name": "John",
        "class_name": "10",
        "section": "A",
        "timetable": [
            {
                "day": "Monday",
                "subject": "Math",
                "teacher_name": "Ratan",
                "start_time": "09:00",
                "end_time": "09:40"
            },
            ...
        ]
    }
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get student's class and section
        cursor.execute(
            "SELECT name, class_name, section FROM students WHERE id = ?",
            (student_id,)
        )
        student = cursor.fetchone()
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        student_name, class_name, section = student
        
        # Get timetable for this student's class
        cursor.execute(
            """SELECT id, day, subject, teacher_name, start_time, end_time
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
               END, start_time""",
            (class_name, section)
        )
        
        rows = cursor.fetchall()
        
        timetable = [
            {
                "id": r[0],
                "day": r[1],
                "subject": r[2],
                "teacher_name": r[3],
                "start_time": r[4],
                "end_time": r[5]
            }
            for r in rows
        ]
        
        return jsonify({
            "student_name": student_name,
            "class_name": class_name,
            "section": section,
            "timetable": timetable
        }), 200
        
    except Exception as e:
        current_app.logger.error("get_student_timetable failed: %s", e)
        return jsonify({"error": "Failed to fetch timetable"}), 500


# -------------------------------------------------------------------
# TEACHER DASHBOARD → GET TIMETABLE FOR THE WEEK
# -------------------------------------------------------------------
@bp.route("/teacher/<int:teacher_id>/week", methods=["GET"])
@jwt_required()
def get_teacher_timetable(teacher_id):
    """
    Get timetable for a teacher for the entire week.
    Returns all classes taught by this teacher, sorted by day and time.
    
    GET /api/timetable/teacher/{teacher_id}/week
    
    Returns: {
        "teacher_name": "Ratan",
        "timetable": [
            {
                "day": "Monday",
                "class_name": "10",
                "section": "A",
                "subject": "Math",
                "start_time": "09:00",
                "end_time": "09:40"
            },
            ...
        ]
    }
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get teacher name
        cursor.execute(
            "SELECT name FROM teachers WHERE id = ?",
            (teacher_id,)
        )
        teacher = cursor.fetchone()
        
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404
        
        teacher_name = teacher[0]
        
        # Get timetable for this teacher
        # Match by teacher_name since the timetable stores teacher_name, not teacher_id
        cursor.execute(
            """SELECT id, day, class_name, section, subject, start_time, end_time
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
               END, start_time""",
            (teacher_name,)
        )
        
        rows = cursor.fetchall()
        
        timetable = [
            {
                "id": r[0],
                "day": r[1],
                "class_name": r[2],
                "section": r[3],
                "subject": r[4],
                "start_time": r[5],
                "end_time": r[6]
            }
            for r in rows
        ]
        
        return jsonify({
            "teacher_name": teacher_name,
            "timetable": timetable
        }), 200
        
    except Exception as e:
        current_app.logger.error("get_teacher_timetable failed: %s", e)
        return jsonify({"error": "Failed to fetch timetable"}), 500
