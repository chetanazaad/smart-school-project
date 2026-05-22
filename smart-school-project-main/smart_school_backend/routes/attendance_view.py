# routes/attendance_view.py
from flask import Blueprint, jsonify, request
from smart_school_backend.utils.db import get_db
import logging

attendance_view_bp = Blueprint("attendance_view", __name__)
logger = logging.getLogger(__name__)

@attendance_view_bp.route("/all", methods=["GET"])
def get_all_attendance():
    """
    Fetches a unified list of attendance records for both students and teachers.
    Can be filtered by role and date.
    """
    db = get_db()
    cur = db.cursor()
    
    role = request.args.get("role")  # "student" or "teacher"
    date = request.args.get("date")  # YYYY-MM-DD
    limit = request.args.get("limit", 20, type=int)

    queries = []
    params = []

    # Prepare student query if needed
    if not role or role == 'student':
        student_query = "SELECT s.id, s.name, 'student' as role, sa.date, sa.status, sa.marked_at as time FROM student_attendance sa JOIN students s ON sa.student_id = s.id"
        clauses = []
        if date:
            clauses.append("sa.date = ?")
            params.append(date)
        if clauses:
            student_query += " WHERE " + " AND ".join(clauses)
        queries.append(student_query)

    # Prepare teacher query if needed
    if not role or role == 'teacher':
        teacher_query = "SELECT t.id, t.name, 'teacher' as role, ta.date, ta.status, ta.marked_at as time FROM teacher_attendance ta JOIN teachers t ON ta.teacher_id = t.id"
        clauses = []
        if date:
            clauses.append("ta.date = ?")
            params.append(date)
        if clauses:
            teacher_query += " WHERE " + " AND ".join(clauses)
        queries.append(teacher_query)

    if not queries:
        return jsonify({"records": []}), 200

    # Combine queries with UNION ALL
    final_query = " UNION ALL ".join([f"({q})" for q in queries])
    
    # Add ordering and limit
    final_query += " ORDER BY time DESC"
    if limit:
        final_query += " LIMIT ?"
        params.append(limit)

    try:
        cur.execute(final_query, params)
        rows = cur.fetchall()
        
        data = [dict(row) for row in rows]
        
        return jsonify({"records": data}), 200
        
    except Exception as e:
        logger.error(f"Error fetching attendance: {type(e).__name__}")
        # Return an empty list if a table doesn't exist, etc.
        return jsonify({"records": [], "error": str(e)}), 200
