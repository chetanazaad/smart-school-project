from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
import logging

bp = Blueprint("users", __name__)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# GET /api/users
# ----------------------------------------------------------
@bp.route("/", methods=["GET"])
@jwt_required()
def get_all_users():
    """Returns all user accounts from the users table."""
    try:
        db = get_db()
        cur = db.cursor()
        
        # We also want to know if they are orphans (no matching student/teacher)
        cur.execute("""
            SELECT 
                u.id, u.email, u.role, u.name, u.created_at,
                (SELECT COUNT(*) FROM students s WHERE s.email = u.email) as student_count,
                (SELECT COUNT(*) FROM teachers t WHERE t.email = u.email) as teacher_count
            FROM users u
        """)
        
        rows = cur.fetchall()
        users = []
        for r in rows:
            user_role = r["role"]
            is_orphan = False
            if user_role == "student" and r["student_count"] == 0:
                is_orphan = True
            elif user_role == "teacher" and r["teacher_count"] == 0:
                is_orphan = True
            # Admin accounts are never orphans in this context
            
            users.append({
                "id": r["id"],
                "email": r["email"],
                "role": r["role"],
                "name": r["name"],
                "created_at": r["created_at"],
                "is_orphan": is_orphan
            })
            
        return jsonify({"users": users}), 200
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500

# ----------------------------------------------------------
# DELETE /api/users/<id>
# ----------------------------------------------------------
@bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Directly delete a user account."""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Don't allow deleting the user'es own account if they are the one logged in? 
        # For now, just protect the main admin maybe? Or just trust the admin.
        
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        
        if cur.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({"message": "User account deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({"error": "Failed to delete user"}), 500
