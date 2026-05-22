# smart_school_backend/routes/automatic_attendance.py

"""
Automatic Attendance Marking API
Uses face_recognition embeddings to auto-mark student/teacher attendance.

URLs (after app.py prefix):
- POST /api/auto-attendance/mark-student
- POST /api/auto-attendance/mark-teacher
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from io import BytesIO
import base64
import json
import logging

import numpy as np
from PIL import Image
try:
    from models.face_recognition import load_all_embeddings
except ImportError:
    from smart_school_backend.models.face_recognition import load_all_embeddings

# Lazy import: face_engine imported in functions to avoid TensorFlow at startup
# from smart_school_backend.face_engine.encoder import generate_embedding

# DB helper
try:
    from smart_school_backend.utils.db import get_db
except ImportError:
    from utils.db import get_db

bp = Blueprint("automatic_attendance", __name__)
logger = logging.getLogger(__name__)


# ---------------------------------------
# Shared Helpers
# ---------------------------------------

def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode base64 (optional data URL) → RGB numpy array."""
    if not image_data:
        raise ValueError("No image data provided")

    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return np.array(image)


def extract_single_embedding(image_array: np.ndarray):
    """Return a single face embedding using the DeepFace encoder, or raise ValueError."""
    # Convert numpy RGB image to base64 data URL expected by encoder
    try:
        from io import BytesIO
        import base64
        # Lazy import to avoid TensorFlow dependency at startup
        from smart_school_backend.face_engine.encoder import generate_embedding

        pil = Image.fromarray(image_array.astype('uint8'), 'RGB')
        buf = BytesIO()
        pil.save(buf, format='JPEG')
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        emb = generate_embedding(b64)
        if emb is None:
            raise ValueError("No face detected in image")
        return emb
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Embedding generation failed: {e}")


def check_already_marked(entity_id: int, entity_type: str) -> bool:
    """
    Check if attendance already marked today.
    - entity_type: 'student' or 'teacher'
    """
    conn = get_db()
    today = date.today().isoformat()

    if entity_type == "student":
        row = conn.execute(
            "SELECT id FROM student_attendance WHERE student_id = ? AND date = ? LIMIT 1",
            (entity_id, today),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM teacher_attendance WHERE teacher_id = ? AND date = ? LIMIT 1",
            (entity_id, today),
        ).fetchone()

    return row is not None


# ---------------------------------------
# Matching helpers
# ---------------------------------------

def _find_match_from_embeddings(captured_embedding: np.ndarray, stored_list: list, tolerance: float):
    """
    Match a captured embedding (numpy array) against stored embeddings list.
    `stored_list` is a list of dicts from `load_all_embeddings()`.
    Returns best match dict or None.
    """
    if not stored_list:
        return None

    # Normalize captured
    cap = np.array(captured_embedding, dtype=np.float32)
    cap_norm = cap / np.linalg.norm(cap)

    best = None
    best_dist = float('inf')

    for entry in stored_list:
        db_emb = np.array(entry['embedding'], dtype=np.float32)
        if db_emb.size == 0:
            continue
        db_norm = db_emb / np.linalg.norm(db_emb)
        similarity = np.dot(cap_norm, db_norm)
        dist = 1.0 - float(similarity)
        if dist < best_dist and dist <= tolerance:
            best_dist = dist
            best = {
                'person_id': entry.get('person_id'),
                'role': entry.get('role'),
                'name': entry.get('name'),
                'email': entry.get('email'),
                'class_name': entry.get('class_name'),
                'section': entry.get('section'),
                'distance': float(dist),
            }

    return best


def find_matching_student(captured_embedding, tolerance=0.68, class_name=None, section=None):
    # Load all embeddings and filter by role=student and optionally class/section
    all_emb = load_all_embeddings()
    students = [e for e in all_emb if e.get('role') == 'student']
    if class_name:
        students = [s for s in students if s.get('class_name') == class_name and s.get('section') == section]
    return _find_match_from_embeddings(captured_embedding, students, tolerance)


def find_matching_teacher(captured_embedding, tolerance=0.68):
    all_emb = load_all_embeddings()
    teachers = [e for e in all_emb if e.get('role') == 'teacher']
    return _find_match_from_embeddings(captured_embedding, teachers, tolerance)


# ---------------------------------------
# Routes: Mark Student Attendance
# ---------------------------------------

@bp.route("/mark-student", methods=["POST"])
@jwt_required()
def mark_student_attendance():
    """
    Mark **student** attendance automatically from one photo.

    JSON:
    {
      "image": "base64",
      "tolerance": 0.5   // optional
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        image_data = data.get("image")
        tolerance = float(data.get("tolerance", 0.5))

        if not image_data:
            return jsonify({"error": "No image provided"}), 400

        image_array = decode_base64_image(image_data)
        captured_embedding = extract_single_embedding(image_array)

        match = find_matching_student(captured_embedding.tolist(), tolerance)
        if not match:
            return jsonify({
                "success": False,
                "error": "Face not recognized. Please try again or check camera.",
            }), 200

        # `match['person_id']` may be an id_code or numeric id stored as string.
        person_id_str = str(match.get("person_id"))
        # Try to resolve to numeric student id in DB
        cur = get_db().cursor()
        student = None
        if person_id_str.isdigit():
            student = cur.execute("SELECT id, name, class_name FROM students WHERE id = ?", (int(person_id_str),)).fetchone()
        if not student:
            student = cur.execute("SELECT id, name, class_name FROM students WHERE id_code = ?", (person_id_str,)).fetchone()
        if not student:
            return jsonify({"success": False, "error": "Matched person not found in students table"}), 200
        student_id = student['id']
        student_class = student.get('class_name', 'Unknown')  # Get class_name for attendance
        confidence = 1.0 - float(match.get('distance', 1.0))
        if check_already_marked(student_id, "student"):
            return jsonify({
                "success": False,
                "already_marked": True,
                "student_id": student_id,
                "student_name": match["name"],
                "error": f"Attendance already marked today for {match['name']}",
            }), 200

        conn = get_db()
        today = date.today().isoformat()
        now_time = datetime.now().strftime("%H:%M:%S")

        try:
            conn.execute(
                """
                INSERT INTO student_attendance (student_id, class_name, date, status, marked_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (student_id, student_class, today, "present", now_time),
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": f"Database error: {e}"}), 500

        return jsonify({
            "success": True,
            "message": f"Attendance marked for {match['name']}",
            "student_id": student_id,
            "student_name": student['name'],
            "status": "present",
            "date": today,
            "time": now_time,
            "confidence": confidence,
        }), 200

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Auto student attendance error: {type(e).__name__}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


# ---------------------------------------
# Routes: Mark Teacher Attendance
# ---------------------------------------

@bp.route("/mark-teacher", methods=["POST"])
@jwt_required()
def mark_teacher_attendance():
    """
    Mark **teacher** attendance automatically from one photo.

    JSON:
    {
      "image": "base64",
      "tolerance": 0.5
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        image_data = data.get("image")
        tolerance = float(data.get("tolerance", 0.5))

        if not image_data:
            return jsonify({"error": "No image provided"}), 400

        image_array = decode_base64_image(image_data)
        captured_embedding = extract_single_embedding(image_array)

        match = find_matching_teacher(captured_embedding.tolist(), tolerance)
        if not match:
            return jsonify({
                "success": False,
                "error": "Face not recognized. Please try again or check camera.",
            }), 200

        person_id_str = str(match.get("person_id"))
        cur = get_db().cursor()
        teacher = None
        if person_id_str.isdigit():
            teacher = cur.execute("SELECT id, name FROM teachers WHERE id = ?", (int(person_id_str),)).fetchone()
        if not teacher:
            teacher = cur.execute("SELECT id, name FROM teachers WHERE id_code = ?", (person_id_str,)).fetchone()
        if not teacher:
            return jsonify({"success": False, "error": "Matched person not found in teachers table"}), 200
        teacher_id = teacher['id']
        confidence = 1.0 - float(match.get('distance', 1.0))
        if check_already_marked(teacher_id, "teacher"):
            return jsonify({
                "success": False,
                "already_marked": True,
                "teacher_id": teacher_id,
                "teacher_name": match["name"],
                "error": f"Attendance already marked today for {match['name']}",
            }), 200

        conn = get_db()
        today = date.today().isoformat()
        now_time = datetime.now().strftime("%H:%M:%S")

        try:
            conn.execute(
                """
                INSERT INTO teacher_attendance (teacher_id, date, status, marked_at)
                VALUES (?, ?, ?, ?)
                """,
                (teacher_id, today, "present", now_time),
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": f"Database error: {e}"}), 500

        return jsonify({
            "success": True,
            "message": f"Attendance marked for {match['name']}",
            "teacher_id": teacher_id,
            "teacher_name": teacher['name'],
            "status": "present",
            "date": today,
            "time": now_time,
            "confidence": confidence,
        }), 200

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Auto teacher attendance error: {type(e).__name__}")
        return jsonify({"success": False, "error": "Internal server error"}), 500
