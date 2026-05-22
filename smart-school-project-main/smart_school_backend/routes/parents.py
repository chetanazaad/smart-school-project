# smart_school_backend/routes/parents.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import sqlite3
import os
import logging
try:
    from utils.db import get_db
    from models.user import create_user
except ImportError:
    from smart_school_backend.utils.db import get_db
    from smart_school_backend.models.user import create_user

bp = Blueprint("parents", __name__)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# DB helper
# ----------------------------------------------------------
# Using get_db from smart_school_backend.utils.db


# ----------------------------------------------------------
# CREATE PARENTS TABLE (if not exists)
# ----------------------------------------------------------
def create_parents_table():
    db = get_db()
    cur = db.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_code TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


# Note: Table creation is handled by init_db.py at startup
# Do not call create_parents_table() here - it would fail during import


# ----------------------------------------------------------
# GENERATE UNIQUE PARENT ID
# GET /api/parents/generate-id
# ----------------------------------------------------------
@bp.route("/generate-id", methods=["GET"])
@jwt_required()
def generate_parent_id():
    """Generate a unique parent ID with format P1001"""
    try:
        import random
        import time
        
        db = get_db()
        cur = db.cursor()
        
        # Try up to 10 times to generate unique ID with P prefix
        max_attempts = 10
        for attempt in range(max_attempts):
            n = random.randint(1000, 9999)
            new_id = f"P{n}"  # Format: P1001, P2543, etc.
            
            # Check if ID exists
            cur.execute("SELECT id FROM parents WHERE id_code = ?", (new_id,))
            if not cur.fetchone():
                return jsonify({"id_code": new_id}), 200
            
            # If collision, sleep briefly then retry
            if attempt < max_attempts - 1:
                time.sleep(0.01 * (attempt + 1))
        
        # If we get here, couldn't generate unique ID
        logger.error("Failed to generate unique parent ID after max attempts")
        return jsonify({"error": "Could not generate unique parent ID. Too many collisions."}), 500
    except Exception as e:
        logger.error(f"Error generating parent ID: {type(e).__name__}")
        return jsonify({"error": "Failed to generate ID"}), 500


# ----------------------------------------------------------
# GET ALL PARENTS
# GET /api/parents
# ----------------------------------------------------------
@bp.route("", methods=["GET"])
@jwt_required()
def get_all_parents():
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT id, id_code, name, email, phone FROM parents ORDER BY id DESC")
        rows = cur.fetchall()

        parents = []
        for r in rows:
            parents.append({
                "id": r["id"],
                "id_code": r["id_code"],
                "name": r["name"],
                "email": r["email"],
                "phone": r["phone"],
            })

        return jsonify({"parents": parents}), 200

    except Exception as e:
        logger.error(f"Error fetching parents: {type(e).__name__}")
        return jsonify({"error": "Failed to fetch parents"}), 500


# ----------------------------------------------------------
# CREATE PARENT
# POST /api/parents
# ----------------------------------------------------------
@bp.route("", methods=["POST"])
@jwt_required()
def create_parent():
    try:
        data = request.get_json() or {}
        id_code = data.get("id_code")
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        if not name or not email:
            return jsonify({"error": "name and email required"}), 400

        db = get_db()
        cur = db.cursor()

        # Check if parent with this email already exists
        cur.execute("SELECT id FROM parents WHERE email = ?", (email,))
        if cur.fetchone():
            return jsonify({"error": "Parent with this email already exists"}), 409
            
        # Self-Healing: Check if user account is an ORPHAN
        cur.execute("SELECT id, role FROM users WHERE email = ?", (email,))
        user_row = cur.fetchone()
        if user_row:
            # Verify if this user actually belongs to any profile
            cur.execute("SELECT id FROM students WHERE email = ?", (email,))
            in_students = cur.fetchone()
            cur.execute("SELECT id FROM teachers WHERE email = ?", (email,))
            in_teachers = cur.fetchone()
            cur.execute("SELECT id FROM parents WHERE email = ?", (email,))
            in_parents = cur.fetchone()

            if not in_students and not in_teachers and not in_parents:
                logger.warning(f"Found orphaned user account for {email}. Cleaning up for new parent.")
                cur.execute("DELETE FROM users WHERE email = ?", (email,))
                db.commit() # Commit deletion immediately
            else:
                return jsonify({"error": f"User account with this email already exists as a {user_row['role']}. Please use a different email or delete the existing {user_row['role']} first."}), 409

        # Create parent record
        cur.execute(
            "INSERT INTO parents (id_code, name, email, phone) VALUES (?, ?, ?, ?)",
            (id_code, name, email, phone)
        )
        db.commit()
        parent_id = cur.lastrowid

        # Create user account if password provided
        if password:
            try:
                user_id = create_user(name=name, email=email, password=password, role="parent")
                return jsonify({"message": "Parent created with login credentials", "id": parent_id, "user_id": user_id}), 201
            except Exception as user_err:
                # Parent created but user creation failed (maybe email exists)
                logger.warning(f"Parent created but user creation failed: {type(user_err).__name__}")
                return jsonify({"message": "Parent created but login credentials could not be set (email may already exist)", "id": parent_id}), 201
        else:
            return jsonify({"message": "Parent created", "id": parent_id}), 201

    except Exception as e:
        logger.error(f"Error creating parent: {type(e).__name__}")
        return jsonify({"error": "Failed to create parent"}), 500


# ----------------------------------------------------------
# GET PARENT BY ID
# GET /api/parents/<id>
# ----------------------------------------------------------
@bp.route("/<int:parent_id>", methods=["GET"])
@jwt_required()
def get_parent(parent_id):
    try:
        db = get_db()
        cur = db.cursor()
        
        cur.execute("SELECT id, id_code, name, email, phone FROM parents WHERE id=?", (parent_id,))
        row = cur.fetchone()
        
        if not row:
            return jsonify({"error": "Parent not found"}), 404
        
        return jsonify({"parent": dict(row)}), 200
    
    except Exception as e:
        logger.error(f"Error fetching parent: {type(e).__name__}")
        return jsonify({"error": "Failed to fetch parent"}), 500


# ----------------------------------------------------------
# DELETE PARENT
# DELETE /api/parents/<id>
# ----------------------------------------------------------
@bp.route("/<int:parent_id>", methods=["DELETE"])
@jwt_required()
def delete_parent(parent_id):
    try:
        db = get_db()
        cur = db.cursor()
        
        cur.execute("DELETE FROM parents WHERE id=?", (parent_id,))
        db.commit()
        
        return jsonify({"message": "Parent deleted"}), 200
    
    except Exception as e:
        logger.error(f"Error deleting parent: {type(e).__name__}")
        return jsonify({"error": "Failed to delete parent"}), 500


# ----------------------------------------------------------
# GET PARENTS COUNT
# GET /api/parents/count
# ----------------------------------------------------------
@bp.route("/count", methods=["GET"])
@jwt_required()
def parent_count():
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT COUNT(*) AS total FROM parents")
        row = cur.fetchone()

        return jsonify({"count": row["total"]}), 200

    except Exception as e:
        logger.error(f"Error getting parent count: {type(e).__name__}")
        return jsonify({"count": 0}), 200
