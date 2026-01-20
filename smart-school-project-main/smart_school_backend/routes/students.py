from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import sqlite3
import os
from models.user import create_user

bp = Blueprint("students", __name__)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), "..", "database", "smart_school.db")
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# 1) GET ALL STUDENTS (FIX FOR STUDENTS PAGE)
# ============================================================
@bp.route("", methods=["GET"])
@jwt_required()
def get_students():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, id_code, class_name, section FROM students ORDER BY id DESC")
        rows = cur.fetchall()

        students = [dict(row) for row in rows]

        return jsonify({
            "students": students,
            "count": len(students)
        }), 200

    except Exception as e:
        print("ERROR GET_STUDENTS:", e)
        return jsonify({"error": "Failed to load students"}), 500


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
        email = data.get("email")
        class_name = data.get("class_name")
        section = data.get("section")
        password = data.get("password")

        if not name or not email:
            return jsonify({"error": "name and email required"}), 400

        conn = get_db()
        cur = conn.cursor()
        
        # Create student record
        if id_code:
            cur.execute("INSERT INTO students (name, email, id_code, class_name, section) VALUES (?, ?, ?, ?, ?)",
                        (name, email, id_code, class_name, section))
        else:
            cur.execute("INSERT INTO students (name, email, class_name, section) VALUES (?, ?, ?, ?)",
                        (name, email, class_name, section))
        conn.commit()
        student_id = cur.lastrowid

        # Create user account if password provided
        if password:
            try:
                user_id = create_user(name=name, email=email, password=password, role="student")
                return jsonify({"message": "Student created with login credentials", "id": student_id, "user_id": user_id}), 201
            except Exception as user_err:
                # Student created but user creation failed (maybe email exists)
                print(f"Warning: Student created (id={student_id}) but user creation failed:", user_err)
                return jsonify({"message": "Student created but login credentials could not be set (email may already exist)", "id": student_id}), 201
        else:
            return jsonify({"message": "Student created", "id": student_id}), 201
            
    except Exception as e:
        print("ERROR create_student:", e)
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
        cur.execute("SELECT id, name, email, id_code, class_name, section FROM students WHERE id=?", (student_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"student": dict(row)}), 200
    except Exception as e:
        print("ERROR get_student:", e)
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
        email = data.get("email")
        class_name = data.get("class_name")
        section = data.get("section")

        conn = get_db()
        cur = conn.cursor()
        if id_code is not None:
            cur.execute("UPDATE students SET name=?, email=?, id_code=?, class_name=?, section=? WHERE id=?",
                        (name, email, id_code, class_name, section, student_id))
        else:
            cur.execute("UPDATE students SET name=?, email=?, class_name=?, section=? WHERE id=?",
                        (name, email, class_name, section, student_id))
        conn.commit()
        return jsonify({"message": "Student updated"}), 200
    except Exception as e:
        print("ERROR update_student:", e)
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
        cur.execute("DELETE FROM student_attendance WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM students WHERE id=?", (student_id,))
        cur.execute("DELETE FROM face_embeddings WHERE person_id=? AND role='student'", (student_id,))
        conn.commit()
        return jsonify({"message": "Student deleted"}), 200
    except Exception as e:
        print("ERROR delete_student:", e)
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
    except:
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
    except:
        return jsonify({"count": 0, "data": []}), 200
