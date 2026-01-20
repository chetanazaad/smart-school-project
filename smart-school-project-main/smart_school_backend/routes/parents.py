# smart_school_backend/routes/parents.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import sqlite3
import os
from models.user import create_user

bp = Blueprint("parents", __name__)

# ----------------------------------------------------------
# DB helper
# ----------------------------------------------------------
def get_db():
    try:
        from smart_school_backend.utils.db import get_db as gdb
        return gdb()
    except Exception:
        from flask import current_app
        db_path = os.path.join(current_app.root_path, "..", "database", "smart_school.db")
        db_path = os.path.abspath(db_path)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


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
        print("ERROR get_all_parents:", e)
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
                print(f"Warning: Parent created (id={parent_id}) but user creation failed:", user_err)
                return jsonify({"message": "Parent created but login credentials could not be set (email may already exist)", "id": parent_id}), 201
        else:
            return jsonify({"message": "Parent created", "id": parent_id}), 201

    except Exception as e:
        print("ERROR create_parent:", e)
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
        print("ERROR get_parent:", e)
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
        print("ERROR delete_parent:", e)
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
        print("ERROR parent_count:", e)
        return jsonify({"count": 0}), 200
