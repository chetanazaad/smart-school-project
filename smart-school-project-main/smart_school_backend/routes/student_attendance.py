# smart_school_backend/routes/student_attendance.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, date as date_module

try:
    from smart_school_backend.utils.db import get_db
except ImportError:
    from utils.db import get_db

# Correct blueprint name
student_attendance_bp = Blueprint("student_attendance", __name__)


def _mark_student_attendance_helper(student_id, status="present"):
    """Helper function to mark student attendance. Can be called from other modules."""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    marked_at_ts = now.strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("SELECT class_name FROM students WHERE id = ?", (student_id,))
        row = cur.fetchone()
        if not row or not row["class_name"]:
            current_app.logger.error(
                f"Could not mark attendance for student_id {student_id}: class_name not found."
            )
            return False, "class_name for student not found"
        class_name = row["class_name"]
    except Exception as e:
        current_app.logger.error(
            f"DB error when fetching class_name for student_id {student_id}: {e}"
        )
        return False, "Database error fetching class name"

    try:
        cur.execute(
            """
            INSERT INTO student_attendance (student_id, class_name, date, status, marked_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, date)
            DO UPDATE SET status=excluded.status, marked_at=excluded.marked_at
            """,
            (student_id, class_name, date, status, marked_at_ts),
        )
        db.commit()
        current_app.logger.info(
            f"Successfully marked attendance for student_id {student_id} with status '{status}'"
        )
        return True, "Attendance saved"
    except Exception as e:
        current_app.logger.error(f"mark_student_attendance_helper error: {e}")
        db.rollback()
        return False, "Failed to save attendance"


# -------------------------------------------------------------------
# RECORD ATTENDANCE FOR A STUDENT
# -------------------------------------------------------------------
@student_attendance_bp.route("/mark", methods=["POST"])
def mark_student_attendance():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    status = data.get("status", "present")

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    success, message = _mark_student_attendance_helper(student_id, status)

    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500


# -------------------------------------------------------------------
# GET ALL ATTENDANCE FOR A SPECIFIC STUDENT
# -------------------------------------------------------------------
@student_attendance_bp.route("/student/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_attendance(student_id):
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            """
            SELECT date, status, marked_at
            FROM student_attendance
            WHERE student_id=?
            ORDER BY date DESC
            """,
            (student_id,),
        )
        rows = cur.fetchall()
    except Exception as e:
        current_app.logger.error("get_student_attendance error: %s", e)
        return jsonify({"attendance": [], "records": []}), 200

    attendance_list = []
    for row in rows:
        marked_at = row[2] or ""
        time_part = marked_at.split("T")[1].split(".")[0] if "T" in marked_at else (marked_at.split(" ")[1] if (marked_at and len(marked_at.split(" "))>1) else "")
        attendance_list.append({
            "date": row[0],
            "status": row[1],
            "time": time_part
        })

    return jsonify({"attendance": attendance_list, "records": attendance_list}), 200


# -------------------------------------------------------------------
# STUDENT DASHBOARD → ATTENDANCE STATISTICS
# -------------------------------------------------------------------
@student_attendance_bp.route("/<int:student_id>/stats", methods=["GET"])
@jwt_required()
def student_stats(student_id):
    """
    Get overall attendance stats for a student.
    GET /api/student-attendance/{id}/stats

    Returns:
    {
        "total_days": 20,
        "present_days": 18,
        "percentage": 90
    }
    """
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "SELECT COUNT(*) FROM student_attendance WHERE student_id=?",
            (student_id,),
        )
        total_days = cur.fetchone()[0] or 0

        cur.execute(
            "SELECT COUNT(*) FROM student_attendance WHERE student_id=? AND status='present'",
            (student_id,),
        )
        present_days = cur.fetchone()[0] or 0

        percentage = round((present_days / total_days * 100)) if total_days > 0 else 0

    except Exception as e:
        current_app.logger.warning("student_stats failed: %s", e)
        total_days = 0
        present_days = 0
        percentage = 0

    return jsonify({
        "total_days": total_days,
        "present_days": present_days,
        "percentage": percentage
    }), 200


# -------------------------------------------------------------------
# STUDENT DASHBOARD → TODAY'S STATUS
# -------------------------------------------------------------------
@student_attendance_bp.route("/<int:student_id>/today", methods=["GET"])
@jwt_required()
def student_today(student_id):
    """
    Get student's attendance status for today.
    GET /api/student-attendance/{id}/today

    Returns: { "status": "present" | "absent" | "Not Marked" }
    """
    today = date_module.today().strftime("%Y-%m-%d")
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "SELECT status FROM student_attendance WHERE student_id=? AND date=?",
            (student_id, today),
        )
        row = cur.fetchone()
        status = row[0] if row else "Not Marked"
    except Exception as e:
        current_app.logger.warning("student_today failed: %s", e)
        status = "Not Marked"

    return jsonify({"status": status}), 200


# -------------------------------------------------------------------
# STUDENT DASHBOARD → RECENT ATTENDANCE LOGS
# -------------------------------------------------------------------
@student_attendance_bp.route("/<int:student_id>/logs", methods=["GET"])
@jwt_required()
def student_logs(student_id):
    """
    Get recent attendance logs for a student.
    GET /api/student-attendance/{id}/logs?limit=5

    Returns: { "data": [{"date": "...", "status": "..."}, ...] }
    """
    limit = request.args.get("limit", default=5, type=int)
    db = get_db()
    cur = db.cursor()

    logs = []

    try:
        cur.execute(
            """
            SELECT date, status, marked_at
            FROM student_attendance
            WHERE student_id=?
            ORDER BY date DESC
            LIMIT ?
            """,
            (student_id, limit),
        )
        rows = cur.fetchall()

        for row in rows:
            marked_at = row[2] or ""
            time_part = marked_at.split("T")[1].split(".")[0] if "T" in marked_at else (marked_at.split(" ")[1] if (marked_at and len(marked_at.split(" "))>1) else "")
            logs.append({"date": row[0], "status": row[1], "time": time_part})

    except Exception as e:
        current_app.logger.warning("student_logs failed: %s", e)
        logs = []

    return jsonify({"data": logs}), 200


# -------------------------------------------------------------------
# STUDENT ATTENDANCE VIEW → OVERALL STATISTICS
# -------------------------------------------------------------------
@student_attendance_bp.route("/stats/overview", methods=["GET"])
@jwt_required()
def student_attendance_overview():
    """
    Get overall attendance statistics (used by StudentAttendanceView page).
    GET /api/student-attendance/stats/overview

    Returns summary stats for all students.
    """
    db = get_db()
    cur = db.cursor()

    try:
        # Total attendance records
        cur.execute("SELECT COUNT(*) FROM student_attendance")
        total_records = cur.fetchone()[0] or 0

        # Present records
        cur.execute("SELECT COUNT(*) FROM student_attendance WHERE status='present'")
        present_count = cur.fetchone()[0] or 0

        # Absent records
        cur.execute("SELECT COUNT(*) FROM student_attendance WHERE status='absent'")
        absent_count = cur.fetchone()[0] or 0

        percentage = round((present_count / total_records * 100)) if total_records > 0 else 0

    except Exception as e:
        current_app.logger.warning("student_attendance_overview failed: %s", e)
        total_records = 0
        present_count = 0
        absent_count = 0
        percentage = 0

    return jsonify({
        "total_records": total_records,
        "present": present_count,
        "absent": absent_count,
        "percentage": percentage
    }), 200


# -------------------------------------------------------------------
# ADMIN DASHBOARD → GET ATTENDANCE BY DATE AND CLASS
# -------------------------------------------------------------------
@student_attendance_bp.route("/by-date", methods=["GET"])
@jwt_required()
def get_attendance_by_date():
    """
    Get attendance for a specific date and class.
    GET /api/student-attendance/by-date?date=YYYY-MM-DD&class_name=ClassName
    """
    date_str = request.args.get("date")
    class_name = request.args.get("class_name")
    
    if not date_str or not class_name:
        return jsonify({"error": "date and class_name are required"}), 400
        
    db = get_db()
    cur = db.cursor()
    
    try:
        cur.execute(
            """
            SELECT student_id, status 
            FROM student_attendance 
            WHERE date = ? AND class_name = ?
            """, 
            (date_str, class_name)
        )
        rows = cur.fetchall()
        attendance = [{"student_id": row[0], "status": row[1]} for row in rows]
        
        return jsonify({"attendance": attendance}), 200
    except Exception as e:
        current_app.logger.error("get_attendance_by_date failed: %s", e)
        return jsonify({"error": "Failed to fetch attendance"}), 500


# -------------------------------------------------------------------
# ADMIN DASHBOARD → BULK MARK ATTENDANCE
# -------------------------------------------------------------------
@student_attendance_bp.route("/bulk-mark", methods=["POST"])
@jwt_required()
def bulk_mark_attendance():
    """
    Mark attendance for multiple students at once.
    POST /api/student-attendance/bulk-mark
    Payload: {
        "attendance": [
            {"student_id": 1, "class_name": "Class 1", "date": "YYYY-MM-DD", "status": "present", "notes": ""},
            ...
        ]
    }
    """
    data = request.get_json() or {}
    attendance_list = data.get("attendance", [])
    
    if not attendance_list:
        return jsonify({"error": "attendance list is required"}), 400
        
    db = get_db()
    cur = db.cursor()
    success_count = 0
    failed_count = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        for record in attendance_list:
            student_id = record.get("student_id")
            class_name = record.get("class_name")
            date_str = record.get("date")
            status = record.get("status", "absent")
            notes = record.get("notes")
            
            if not all([student_id, class_name, date_str]):
                failed_count += 1
                continue
                
            cur.execute(
                """
                INSERT INTO student_attendance (student_id, class_name, date, status, marked_at, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, date)
                DO UPDATE SET status=excluded.status, marked_at=excluded.marked_at, notes=excluded.notes
                """,
                (student_id, class_name, date_str, status, now, notes)
            )
            success_count += 1
            
        db.commit()
        return jsonify({
            "message": "Bulk attendance processed",
            "results": {"success": success_count, "failed": failed_count}
        }), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error("bulk_mark_attendance failed: %s", e)
        return jsonify({"error": "Failed to process bulk attendance"}), 500