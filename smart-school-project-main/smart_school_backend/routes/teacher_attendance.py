import sqlite3
from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from smart_school_backend.utils.db import get_db
from datetime import datetime, date as date_module

bp = Blueprint("teacher_attendance", __name__)

def setup_teacher_attendance_table():
    if 'teacher_attendance_table_checked' not in g:
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teacher_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                marked_at TEXT,
                UNIQUE(teacher_id, date)
            )
        """)
        db.commit()
        g.teacher_attendance_table_checked = True

@bp.before_request
def before_request_handler():
    setup_teacher_attendance_table()

def _mark_teacher_attendance_helper(teacher_id, status="present"):
    """Helper function to mark teacher attendance. Can be called from other modules."""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    marked_at_ts = now.strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            """
            INSERT INTO teacher_attendance (teacher_id, date, status, marked_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(teacher_id, date) 
            DO UPDATE SET status=excluded.status, marked_at=excluded.marked_at
            """,
            (teacher_id, date, status, marked_at_ts),
        )

        # Also update the teacher's last_seen timestamp
        cur.execute(
            "UPDATE teachers SET last_seen = ? WHERE id = ?",
            (datetime.utcnow(), teacher_id)
        )
        
        db.commit()
        current_app.logger.info(f"Successfully marked teacher attendance for id {teacher_id}")
        return True, "Attendance saved"
    except Exception as e:
        current_app.logger.error(f"mark_teacher_attendance_helper error: {e}")
        db.rollback()
        return False, "Failed to save attendance"

@bp.route("/mark", methods=["POST"])
@jwt_required()
def mark_teacher_attendance():
    """
    Marks teacher attendance for today. It's idempotent, so it won't
    create duplicate entries for the same teacher on the same day.
    """
    data = request.get_json() or {}
    teacher_id = data.get("teacher_id")
    status = data.get("status", "present")

    if not teacher_id:
        return jsonify({"error": "teacher_id is required"}), 400

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    marked_at_ts = now.strftime("%Y-%m-%d %H:%M:%S")
    
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            """
            INSERT INTO teacher_attendance (teacher_id, date, status, marked_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(teacher_id, date) 
            DO UPDATE SET status=excluded.status, marked_at=excluded.marked_at
            """,
            (teacher_id, date, status, marked_at_ts),
        )

        # Also update the teacher's last_seen timestamp
        cur.execute(
            "UPDATE teachers SET last_seen = ? WHERE id = ?",
            (datetime.utcnow(), teacher_id)
        )
        
        db.commit()
        
        return jsonify({"message": "Attendance marked successfully"}), 200

    except Exception as e:
        current_app.logger.error("Failed to mark teacher attendance: %s", e)
        return jsonify({"error": "Server error while marking attendance"}), 500


@bp.route("/records", methods=["GET"])
@jwt_required()
def get_teacher_attendance_records():
    identity = get_jwt_identity()
    
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT id FROM teachers WHERE email=?", (identity,))
    teacher = cur.fetchone()
    
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404
        
    teacher_id = teacher["id"]

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT date, marked_at, status
        FROM teacher_attendance
        WHERE teacher_id=?
        ORDER BY date DESC
    """, (teacher_id,))

    rows = cur.fetchall()

    records = [dict(row) for row in rows]

    return jsonify(records), 200


# -------------------------------------------------------------------
# TEACHER DASHBOARD → TODAY'S ATTENDANCE COUNT
# -------------------------------------------------------------------
@bp.route("/<int:teacher_id>/today", methods=["GET"])
@jwt_required()
def teacher_attendance_count_today(teacher_id):
    """
    Get count of students marked present today (from student_attendance table).
    GET /api/attendance/teacher/{id}/today

    Returns: { "present": 5 }
    """
    today = date_module.today().strftime("%Y-%m-%d")
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "SELECT COUNT(*) FROM student_attendance WHERE date = ? AND status = 'present'",
            (today,),
        )
        present = cur.fetchone()[0] or 0
    except Exception as e:
        current_app.logger.warning("teacher_attendance_count_today failed: %s", e)
        present = 0

    return jsonify({"present": present}), 200


@bp.route("/all_records", methods=["GET"])
@jwt_required()
def get_all_teacher_attendance_records():
    """
    [ADMIN ONLY]
    Fetches all teacher attendance records, optionally filtered by date.
    """
    # Role check
    identity = get_jwt_identity()
    # A database call is used to get the role, assuming the JWT only contains the user email.
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT role FROM users WHERE email = ?", (identity,))
    user_role = cur.fetchone()

    if not user_role or user_role['role'] != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    # Get date filter from query params if available
    filter_date = request.args.get('date', None)

    if filter_date:
        query = """
            SELECT ta.date, ta.status, ta.marked_at, t.name as teacher_name, t.id as teacher_id
            FROM teacher_attendance ta
            JOIN teachers t ON ta.teacher_id = t.id
            WHERE ta.date = ?
            ORDER BY ta.marked_at DESC
        """
        cur.execute(query, (filter_date,))
    else:
        query = """
            SELECT ta.date, ta.status, ta.marked_at, t.name as teacher_name, t.id as teacher_id
            FROM teacher_attendance ta
            JOIN teachers t ON ta.teacher_id = t.id
            ORDER BY ta.marked_at DESC
        """
        cur.execute(query)

    rows = cur.fetchall()
    records = [dict(row) for row in rows]

    return jsonify(records), 200