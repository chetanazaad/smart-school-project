# smart_school_backend/routes/attendance.py

from flask import Blueprint, request, jsonify, current_app

try:
    from smart_school_backend.utils.db import get_db
except ImportError:
    from utils.db import get_db

from flask_jwt_extended import jwt_required
from datetime import date as date_module

bp = Blueprint("attendance", __name__)
attendance_view_bp = Blueprint("attendance_view", __name__)


# -------------------------------------------------------------------
# MANUAL STUDENT ATTENDANCE (basic)
# -------------------------------------------------------------------

@bp.route("/mark", methods=["POST"])
@jwt_required()
def mark_attendance():
    """
    Manual attendance marking.
    Supports two payload shapes:
      - { "student_id": 1, "date": "YYYY-MM-DD", "status": "present" }
      - { "id": 10001, "type": "student" }   (admin shorthand: marks today as present)
    """
    data = request.get_json() or {}
    db = get_db()
    cur = db.cursor()

    # Admin shorthand: { id, type }
    if data.get("id") and data.get("type"):
        pid = data.get("id")
        ptype = data.get("type")
        from datetime import date as date_module
        today = date_module.today().isoformat()

        try:
            from datetime import datetime
            if ptype == "student":
                # Check by ID, id_code, or email
                user_data = None
                if str(pid).isdigit():
                    cur.execute("SELECT id, class_name FROM students WHERE id=?", (int(pid),))
                    user_data = cur.fetchone()
                if not user_data:
                    cur.execute("SELECT id, class_name FROM students WHERE id_code=?", (str(pid),))
                    user_data = cur.fetchone()
                if not user_data:
                    cur.execute("SELECT id, class_name FROM students WHERE email=?", (str(pid),))
                    user_data = cur.fetchone()

                if not user_data:
                    return jsonify({"error": "Student not found"}), 404

                sid = user_data["id"]
                class_name = user_data["class_name"]

                # idempotent insert
                cur.execute(
                    "SELECT id FROM student_attendance WHERE student_id = ? AND date = ?",
                    (sid, today),
                )
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO student_attendance (student_id, class_name, date, status, marked_at) VALUES (?, ?, ?, 'present', ?)",
                        (sid, class_name, today, datetime.utcnow().isoformat()),
                    )
                    db.commit()

                return jsonify({"success": True, "marked": {"id": sid, "date": today}}), 200

            elif ptype == "teacher":
                user_data = None
                if str(pid).isdigit():
                    cur.execute("SELECT id FROM teachers WHERE id=?", (int(pid),))
                    user_data = cur.fetchone()
                if not user_data:
                    cur.execute("SELECT id FROM teachers WHERE id_code=?", (str(pid),))
                    user_data = cur.fetchone()
                if not user_data:
                    cur.execute("SELECT id FROM teachers WHERE email=?", (str(pid),))
                    user_data = cur.fetchone()

                if not user_data:
                    return jsonify({"error": "Teacher not found"}), 404

                tid = user_data["id"]

                cur.execute(
                    "SELECT id FROM teacher_attendance WHERE teacher_id = ? AND date = ?",
                    (tid, today),
                )
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO teacher_attendance (teacher_id, date, status, marked_at) VALUES (?, ?, 'present', ?)",
                        (tid, today, datetime.utcnow().isoformat()),
                    )
                    db.commit()

                return jsonify({"success": True, "marked": {"id": tid, "date": today}}), 200

        except Exception as e:
            current_app.logger.error("mark_attendance shorthand failed: %s", e)
            return jsonify({"error": "Failed to mark attendance"}), 500

    # Legacy / explicit payload
    student_id = data.get("student_id")
    date = data.get("date")
    status = data.get("status", "present")

    if not student_id or not date:
        return jsonify({"error": "student_id and date are required"}), 400

    # Upsert pattern: if already exists for that date, update; else insert
    try:
        cur.execute(
            """
            INSERT INTO student_attendance (student_id, date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status
            """,
            (student_id, date, status),
        )
    except Exception:
        # If ON CONFLICT is not supported for your table definition,
        # fall back to manual update.
        try:
            cur.execute(
                "UPDATE student_attendance SET status=? WHERE student_id=? AND date=?",
                (status, student_id, date),
            )
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO student_attendance (student_id, date, status) VALUES (?, ?, ?)",
                    (student_id, date, status),
                )
        except Exception as e:
            current_app.logger.error("mark_attendance failed: %s", e)
            return jsonify({"error": "Failed to save attendance"}), 500

    db.commit()
    return jsonify({"message": "Attendance marked successfully"}), 200


# -------------------------------------------------------------------
# DASHBOARD → RECENT ATTENDANCE TIMELINE
# -------------------------------------------------------------------

@attendance_view_bp.route("/all", methods=["GET"])
@jwt_required()
def recent_attendance():
    """
    Endpoint used by Admin Dashboard:
      GET /api/attendance-view/all?limit=5

    We TRY to fetch recent attendance records from DB. If anything
    goes wrong (no table, schema mismatch, etc.), we **log and
    return an empty list** so that the dashboard still works and
    does NOT auto-logout.
    """
    limit = request.args.get("limit", default=5, type=int)

    db = get_db()
    cur = db.cursor()

    records = []

    try:
        # Combine recent student and teacher attendance into a single feed.
        # We now select id_code directly from the joined tables.
        cur.execute(
            """
            SELECT sa.marked_at as marked_at, s.name as name, 'student' as role, sa.student_id as id, sa.class_name as class_name, sa.status as status, s.id_code as id_code
            FROM student_attendance sa
            JOIN students s ON s.id = sa.student_id
            UNION ALL
            SELECT ta.marked_at as marked_at, t.name as name, 'teacher' as role, ta.teacher_id as id, NULL as class_name, ta.status as status, t.id_code as id_code
            FROM teacher_attendance ta
            JOIN teachers t ON t.id = ta.teacher_id
            ORDER BY marked_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()

        for row in rows:
            marked_at = row["marked_at"] or ""
            date_part = marked_at.split("T")[0] if "T" in marked_at else (marked_at.split(" ")[0] if marked_at else "")
            time_part = marked_at.split("T")[1].split(".")[0] if "T" in marked_at else (marked_at.split(" ")[1] if len(marked_at.split(" "))>1 else "")

            # Use the actual id_code from database
            full_id = row["id_code"]
            pid = row["id"]

            records.append(
                {
                    "date": date_part,
                    "time": time_part,
                    "name": row["name"],
                    "type": row["role"],
                    "id": pid,
                    "full_id": full_id,
                    "class_name": row["class_name"],
                    "status": row["status"],
                }
            )

    except Exception as e:
        # IMPORTANT: swallow errors and just return empty data
        current_app.logger.warning(
            "recent_attendance query failed, returning empty list: %s", e
        )
        records = []

    return jsonify({"records": records}), 200


# -------------------------------------------------------------------
# ADMIN DASHBOARD → TODAY'S ATTENDANCE COUNT
# -------------------------------------------------------------------

@bp.route("/today", methods=["GET"])
@jwt_required()
def today_attendance_count():
    """
    Get count of students marked present today.
    GET /api/attendance/today  →  { "count": 5 }
    """
    from datetime import date as date_module
    
    today = date_module.today().strftime("%Y-%m-%d")
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "SELECT COUNT(*) FROM student_attendance WHERE date = ? AND status = 'present'",
            (today,),
        )
        count = cur.fetchone()[0] or 0
    except Exception as e:
        current_app.logger.warning("today_attendance_count failed: %s", e)
        count = 0

    return jsonify({"count": count}), 200


# -------------------------------------------------------------------
# ADMIN DASHBOARD → TODAY'S TEACHERS PRESENT COUNT
# -------------------------------------------------------------------
@bp.route("/teachers/today", methods=["GET"])
@jwt_required()
def teachers_today_count():
    """
    Get count of teachers marked present today.
    GET /api/attendance/teachers/today  →  { "count": 3 }
    """
    from datetime import date as date_module

    today = date_module.today().strftime("%Y-%m-%d")
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "SELECT COUNT(*) FROM teacher_attendance WHERE date = ? AND status = 'present'",
            (today,),
        )
        count = cur.fetchone()[0] or 0
    except Exception as e:
        current_app.logger.warning("teachers_today_count failed: %s", e)
        count = 0

    return jsonify({"count": count}), 200


# -------------------------------------------------------------------
# ADMIN DASHBOARD → TEACHER ATTENDANCE RECORDS
# -------------------------------------------------------------------
@bp.route("/teachers/records", methods=["GET"])
@jwt_required()
def get_teacher_attendance_records_admin():
    """
    Endpoint for Admin Dashboard to fetch detailed historical teacher attendance records.
    Allows filtering by teacher_id, start_date, and end_date.
    GET /api/attendance/teachers/records?teacher_id=<id>&start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>
    """
    teacher_id = request.args.get("teacher_id", type=int)
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    db = get_db()
    cur = db.cursor()
    records = []

    try:
        query = """
            SELECT ta.id, ta.date, ta.status, ta.marked_at, t.name as teacher_name, t.id as teacher_id
            FROM teacher_attendance ta
            JOIN teachers t ON t.id = ta.teacher_id
        """
        params = []
        conditions = []

        if teacher_id:
            conditions.append("ta.teacher_id = ?")
            params.append(teacher_id)
        if start_date_str:
            conditions.append("ta.date >= ?")
            params.append(start_date_str)
        if end_date_str:
            conditions.append("ta.date <= ?")
            params.append(end_date_str)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY ta.date DESC, t.name ASC"

        cur.execute(query, params)
        rows = cur.fetchall()

        for row in rows:
            records.append(dict(row))

    except Exception as e:
        current_app.logger.error("get_teacher_attendance_records_admin failed: %s", e)
        return jsonify({"error": "Failed to fetch teacher attendance records"}), 500

    return jsonify({"records": records, "count": len(records)}), 200


# -------------------------------------------------------------------
# ADMIN DASHBOARD → TEACHER'S RECENT ATTENDANCE VIEW
# -------------------------------------------------------------------

@attendance_view_bp.route("/teacher/<int:teacher_id>", methods=["GET"])
@jwt_required()
def teacher_recent_attendance(teacher_id):
    """
    Endpoint used by Teacher Dashboard:
      GET /api/attendance-view/teacher/{id}?limit=5

    Returns recent attendance records for that teacher's students.
    """
    limit = request.args.get("limit", default=5, type=int)

    db = get_db()
    cur = db.cursor()
    records = []

    try:
        # Get teacher class info
        cur.execute("SELECT is_class_teacher, assigned_class, assigned_section FROM teachers WHERE id=?", (teacher_id,))
        teacher = cur.fetchone()
        
        if not teacher:
            return jsonify({"records": [], "data": []}), 200

        # Fetch recent student attendance
        # If class teacher, only show their students. Otherwise show all (or could filter by subjects)
        if teacher["is_class_teacher"] and teacher["assigned_class"]:
            cur.execute(
                """
                SELECT sa.marked_at,
                       s.name,
                       s.class_name,
                       sa.status
                FROM student_attendance AS sa
                JOIN students AS s ON s.id = sa.student_id
                WHERE s.class_name = ? AND s.section = ?
                ORDER BY sa.marked_at DESC
                LIMIT ?
                """,
                (teacher["assigned_class"], teacher["assigned_section"], limit),
            )
        else:
            # For regular teachers, maybe show all recent? 
            # Or restricted to students they teach? For now, let's keep it simple.
            cur.execute(
                """
                SELECT sa.marked_at,
                       s.name,
                       s.class_name,
                       sa.status
                FROM student_attendance AS sa
                JOIN students AS s ON s.id = sa.student_id
                ORDER BY sa.marked_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        rows = cur.fetchall()

        for row in rows:
            marked_at = row[0] or ""
            time_part = marked_at.split("T")[1].split(".")[0] if "T" in marked_at else (marked_at.split(" ")[1] if (marked_at and len(marked_at.split(" "))>1) else "")
            
            records.append(
                {
                    "date": marked_at.split("T")[0] if "T" in marked_at else (marked_at.split(" ")[0] if marked_at else ""),
                    "time": time_part,
                    "name": row[1],
                    "class_name": row[2],
                    "status": row[3],
                }
            )

    except Exception as e:
        current_app.logger.warning(
            "teacher_recent_attendance failed, returning empty list: %s", e
        )
        records = []

    return jsonify({"records": records, "data": records}), 200


# -------------------------------------------------------------------
# TEACHER DASHBOARD → TODAY'S STUDENT ATTENDANCE COUNT
# -------------------------------------------------------------------

@bp.route("/teacher/<int:teacher_id>/today", methods=["GET"])
@jwt_required()
def teacher_attendance_today_count(teacher_id):
    """
    Get count of students marked present today (for teacher dashboard).
    Wait - this should probably return students for THAT teacher's class.
    But for now we just fixed the table query.
    """
    from datetime import date as date_module
    
    today = date_module.today().strftime("%Y-%m-%d")
    db = get_db()
    cur = db.cursor()

    try:
        # Get teacher class info
        cur.execute("SELECT is_class_teacher, assigned_class, assigned_section FROM teachers WHERE id=?", (teacher_id,))
        teacher = cur.fetchone()
        
        if not teacher:
            return jsonify({"present": 0}), 200

        if teacher["is_class_teacher"] and teacher["assigned_class"]:
            # Count only their students
            cur.execute(
                """
                SELECT COUNT(*) FROM student_attendance sa
                JOIN students s ON s.id = sa.student_id
                WHERE sa.date = ? AND sa.status = 'present'
                AND s.class_name = ? AND s.section = ?
                """,
                (today, teacher["assigned_class"], teacher["assigned_section"]),
            )
        else:
            # Regular teacher or missing class info - fallback to global or 0
            cur.execute(
                "SELECT COUNT(*) FROM student_attendance WHERE date = ? AND status = 'present'",
                (today,),
            )
        present = cur.fetchone()[0] or 0
    except Exception as e:
        current_app.logger.warning("teacher_attendance_today_count failed: %s", e)
        present = 0

    return jsonify({"present": present}), 200

