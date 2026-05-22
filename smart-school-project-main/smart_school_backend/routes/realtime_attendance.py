# smart_school_backend/routes/realtime_attendance.py

"""
Real-Time Face Recognition Attendance System

Endpoint (after prefix):
- POST /api/realtime-attendance/process-frame

Takes a single frame (base64), detects faces, matches them, and
(optionally) marks attendance for recognized students.
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
import face_recognition

try:
    from smart_school_backend.utils.db import get_db
except ImportError:
    from utils.db import get_db

bp = Blueprint("realtime_attendance", __name__)
logger = logging.getLogger(__name__)


# ---------------------------------------
# Image / Detection helpers
# ---------------------------------------

def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode base64 (with or without data URL header) → RGB numpy array."""
    if not image_data:
        raise ValueError("No frame data provided")

    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    img_bytes = base64.b64decode(image_data)
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def process_frame_for_faces(image_data: str):
    """
    Downscale frame for speed, detect faces, return locations & encodings.
    Scales bounding boxes back to original size.
    """
    try:
        full_image = decode_base64_image(image_data)
        original_height, original_width = full_image.shape[:2]

        # Resize for faster processing
        scale_factor = 0.25
        small_image = np.ascontiguousarray(
            np.array(
                Image.fromarray(full_image).resize(
                    (int(original_width * scale_factor), int(original_height * scale_factor))
                )
            )
        )

        try:
            from smart_school_backend.utils.lock import face_lock
        except ImportError:
            from utils.lock import face_lock

        with face_lock:
            # Detect face locations & encodings
            face_locations = face_recognition.face_locations(small_image)
            face_encodings = face_recognition.face_encodings(small_image, face_locations)

        # Scale boxes back to original size
        scaled_locations = []
        for (top, right, bottom, left) in face_locations:
            scaled_locations.append(
                (
                    int(top / scale_factor),
                    int(right / scale_factor),
                    int(bottom / scale_factor),
                    int(left / scale_factor),
                )
            )

        return {
            "success": True,
            "face_locations": scaled_locations,
            "face_encodings": [enc.tolist() for enc in face_encodings],
            "original_dimensions": {"height": original_height, "width": original_width},
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_active_face_embeddings():
    """
    Fetch all active embeddings (currently **students only**; you can extend to teachers).
    Returns list of dict: { id, entity_id, embedding, name, type }
    """
    try:
        conn = get_db()
        c = conn.cursor()

        # Students
        c.execute(
            """
            SELECT fe.id, fe.student_id, fe.embedding, s.name, 'student' as type
            FROM face_embeddings fe
            JOIN students s ON fe.student_id = s.id
            """
        )

        embeddings = []
        for row in c.fetchall():
            embedding_data = np.frombuffer(row["embedding"], dtype=np.float32).tolist()
            embeddings.append(
                {
                    "id": row["id"],
                    "entity_id": row["student_id"],
                    "embedding": embedding_data,
                    "name": row["name"],
                    "type": row["type"],
                }
            )

        return embeddings
    except Exception as e:
        logger.error(f"Error getting embeddings: {type(e).__name__}")
        return []


def find_matching_face(captured_embedding, all_embeddings, tolerance=0.52):
    """Find best matching face ≤ tolerance."""
    if not all_embeddings:
        return None

    try:
        captured_np = np.array(captured_embedding)
        best_match = None
        best_distance = float("inf")

        try:
            from smart_school_backend.utils.lock import face_lock
        except ImportError:
            from utils.lock import face_lock

        with face_lock:
            for emb in all_embeddings:
                stored_np = np.array(emb["embedding"])
                distance = face_recognition.face_distance([stored_np], captured_np)[0]

                if distance < best_distance and distance <= tolerance:
                    best_distance = distance
                    best_match = {
                        "name": emb["name"],
                        "entity_id": emb["entity_id"],
                        "type": emb["type"],
                        "distance": float(distance),
                        "confidence": float(1 - distance),
                    }

        return best_match
    except Exception as e:
        logger.error(f"Error finding match: {type(e).__name__}")
        return None


def check_already_marked_today(student_id: int) -> bool:
    """Check if student attendance already marked today."""
    try:
        conn = get_db()
        c = conn.cursor()
        today = date.today().isoformat()

        c.execute(
            """
            SELECT id FROM student_attendance
            WHERE student_id = ? AND date = ?
            """,
            (student_id, today),
        )
        return c.fetchone() is not None
    except Exception:
        return False


def mark_attendance_record(student_id: int, status: str = "present") -> bool:
    """Insert attendance row for the student."""
    try:
        conn = get_db()
        c = conn.cursor()
        today = date.today().isoformat()

        c.execute(
            """
            INSERT INTO student_attendance (student_id, date, status)
            VALUES (?, ?, ?)
            """,
            (student_id, today, status),
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error marking attendance: {type(e).__name__}")
        return False


# ---------------------------------------
# Route: Process Frame
# ---------------------------------------

@bp.route("/process-frame", methods=["POST"])
@jwt_required()
def process_frame():
    """
    Process a video frame and return detection + recognition:

    Request JSON:
    {
      "frame": "base64_encoded_image",
      "tolerance": 0.52   // optional
    }

    Response:
    {
      "success": true,
      "faces": [
        {
          "box": [top, right, bottom, left],
          "name": "John Doe" | "Unknown",
          "color": "green" | "red",
          "confidence": 0.95,
          "marked": true/false,
          "already_marked": true/false
        }
      ],
      "frame_dimensions": { "height": ..., "width": ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        frame_data = data.get("frame")
        tolerance = float(data.get("tolerance", 0.52))

        if not frame_data:
            return jsonify({"error": "No frame data provided"}), 400

        frame_result = process_frame_for_faces(frame_data)
        if not frame_result["success"]:
            return jsonify(frame_result), 400

        face_locations = frame_result["face_locations"]
        face_encodings = frame_result["face_encodings"]

        all_embeddings = get_all_active_face_embeddings()

        faces = []
        for face_box, face_encoding in zip(face_locations, face_encodings):
            match = find_matching_face(face_encoding, all_embeddings, tolerance)

            if match:
                name = match["name"]
                color = "green"

                already_marked = check_already_marked_today(match["entity_id"])
                marked_now = False

                if not already_marked:
                    marked_now = mark_attendance_record(match["entity_id"])

                faces.append(
                    {
                        "box": face_box,
                        "name": name,
                        "color": color,
                        "confidence": match["confidence"],
                        "marked": bool(marked_now or already_marked),
                        "already_marked": bool(already_marked),
                    }
                )
            else:
                faces.append(
                    {
                        "box": face_box,
                        "name": "Unknown",
                        "color": "red",
                        "confidence": 0.0,
                        "marked": False,
                        "already_marked": False,
                    }
                )

        return jsonify(
            {
                "success": True,
                "faces": faces,
                "frame_dimensions": frame_result["original_dimensions"],
            }
        ), 200

    except Exception as e:
        logger.error(f"process_frame error: {type(e).__name__}")
        return jsonify({"error": str(e)}), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Simple health check for realtime attendance."""
    embeddings = get_all_active_face_embeddings()
    return jsonify({"status": "ok", "enrolled_faces": len(embeddings)}), 200
