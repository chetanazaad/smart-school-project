from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3
import numpy as np
from smart_school_backend.face_engine.encoder import generate_embedding
from smart_school_backend.utils.db import get_db

recognition_bp = Blueprint("recognition", __name__)

@recognition_bp.route("/recognize", methods=["POST"])
@jwt_required()
def recognize_face():
    """
    Recognize a face from image
    
    Authorization:
    - Admin: Can recognize any face
    - Class Teacher: Can recognize themselves and their students only
    - Regular Teacher: Can recognize themselves only
    """
    print("\n--- NEW FACE RECOGNITION REQUEST ---")
    try:
        print("[Recognition] Step 1: Parsing JSON request data...")
        data = request.get_json()
        image_base64 = data.get("image_base64")
        print("[Recognition] Step 1 SUCCESS. JSON data parsed.")

        if not image_base64:
            print("[Recognition] ERROR: Image data not provided in request.")
            return jsonify({"error": "Image is required"}), 400

        # Get current user for authorization
        print("[Recognition] Step 2: Verifying user identity and role...")
        try:
            current_identity = get_jwt_identity()
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT role FROM users WHERE email = ?", (current_identity,))
            user_row = cur.fetchone()
            current_user_role = user_row["role"] if user_row else None
            print(f"[Recognition] Step 2 SUCCESS. User: {current_identity}, Role: {current_user_role}")
        except Exception as e:
            print(f"[Recognition] ERROR in Step 2: Could not get current user. Error: {e}")
            current_user_role = None

        try:
            print("[Recognition] Step 3: Generating embedding for the new face...")
            embedding = generate_embedding(image_base64)
            if embedding is None:
                print("[Recognition] Step 3 FAILED. No face detected or embedding could not be generated.")
                return jsonify({"match": False, "message": "No face detected"}), 200
            print(f"[Recognition] Step 3 SUCCESS. New embedding generated. Shape: {embedding.shape}")

            print("[Recognition] Step 4: Fetching all known face embeddings from the database...")
            conn = get_db()
            cur = conn.cursor()

            rows = cur.execute("""
                SELECT person_id, role, embedding
                FROM face_embeddings
            """).fetchall()
            print(f"[Recognition] Step 4 SUCCESS. Fetched {len(rows)} embeddings from DB.")

            best_match = None
            min_distance = 0.6  # threshold
            print(f"[Recognition] Step 5: Comparing new face with known faces (threshold: {min_distance})...")

            for i, row in enumerate(rows):
                person_id_debug = row["person_id"]
                embedding_blob = row["embedding"]
                
                print(f"\n[Recognition] Comparing with entry #{i+1}: person_id={person_id_debug}")

                if embedding_blob is None:
                    print(f"  -> Skipping person_id {person_id_debug} due to NULL embedding.")
                    continue

                if len(embedding_blob) != 512:
                    print(f"  -> Skipping person_id {person_id_debug} due to invalid embedding length: {len(embedding_blob)} (expected 512).")
                    continue
                
                print(f"  -> DB embedding blob length: {len(embedding_blob)} bytes.")
                db_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                
                print(f"  -> New embedding shape: {embedding.shape}, DB embedding shape: {db_embedding.shape}")
                dist = np.linalg.norm(embedding - db_embedding)
                print(f"  -> Calculated distance: {dist:.4f}")

                if dist < min_distance:
                    print(f"  -> NEW BEST MATCH! Previous min_distance: {min_distance:.4f}, new_distance: {dist:.4f}")
                    min_distance = dist
                    best_match = row
                else:
                    print(f"  -> No match (distance >= threshold).")

            print("[Recognition] Step 5 FINISHED comparison loop.")

            if not best_match:
                print("[Recognition] No face match found after checking all DB entries.")
                return jsonify({"match": False}), 200

            person_id = best_match["person_id"]
            role = best_match["role"]
            print(f"[Recognition] Step 6: Match found! Person ID: {person_id}, Role: {role}, Distance: {min_distance:.4f}")

            try:
                person_id_int = int(person_id)
            except (ValueError, TypeError):
                print(f"[Recognition] ERROR: Invalid person_id '{person_id}' could not be converted to int.")
                return jsonify({"match": False, "message": "Invalid person ID"}), 200
            
            print("[Recognition] Step 7: Performing authorization check...")
            # Authorization check
            if current_user_role != "admin":
                print(f"[Recognition] Non-admin user ({current_user_role}). Performing specific checks...")
                if current_user_role == "teacher":
                    cur.execute("SELECT id, is_class_teacher, assigned_class, assigned_section FROM teachers WHERE email = ?", (current_identity,))
                    teacher = cur.fetchone()
                    
                    if role == "teacher":
                        if teacher is None or teacher["id"] != person_id_int:
                            print(f"[Recognition] AUTH FAIL: Teacher {current_identity} tried to recognize another teacher (ID: {person_id_int}).")
                            return jsonify({"error": "You can only recognize yourself"}), 403
                    elif role == "student":
                        if not teacher or not teacher["is_class_teacher"]:
                            print(f"[Recognition] AUTH FAIL: Teacher {current_identity} is not a class teacher.")
                            return jsonify({"error": "Only class teachers can recognize students"}), 403
                        
                        cur.execute("SELECT id FROM students WHERE id = ? AND class_name = ? AND section = ?", (person_id_int, teacher["assigned_class"], teacher["assigned_section"]))
                        if not cur.fetchone():
                            print(f"[Recognition] AUTH FAIL: Student {person_id_int} is not in class teacher {current_identity}'s class.")
                            return jsonify({"error": "This student is not in your class"}), 403
                    else:
                        print(f"[Recognition] AUTH FAIL: Invalid role '{role}' for recognition by a teacher.")
                        return jsonify({"error": "Invalid role"}), 400
                else:
                    print(f"[Recognition] AUTH FAIL: User role '{current_user_role}' is not authorized.")
                    return jsonify({"error": "Unauthorized"}), 403
            print("[Recognition] Step 7 SUCCESS. Authorization passed.")

            print(f"[Recognition] Step 8: Fetching user details for matched person (ID: {person_id_int}, Role: {role})...")
            if role == "student":
                user = cur.execute("SELECT id, name FROM students WHERE id = ?", (person_id_int,)).fetchone()
            elif role == "teacher":
                user = cur.execute("SELECT id, name FROM teachers WHERE id = ?", (person_id_int,)).fetchone()
            else:
                print(f"[Recognition] ERROR: Unknown role '{role}' found for matched person.")
                return jsonify({"match": False, "message": "Unknown role"}), 200

            if user is None:
                print(f"[Recognition] ERROR: User with ID {person_id_int} and role {role} not found in respective table.")
                return jsonify({"match": False, "message": "User not found"}), 200

            print(f"[Recognition] Step 8 SUCCESS. Found user: {user['name']}.")
            
            print(f"[Recognition] Step 9: Returning final successful match result.")
            print("--- RECOGNITION REQUEST FINISHED SUCCESSFULLY ---\n")
            return jsonify({
                "match": True,
                "id": user["id"],
                "name": user["name"],
                "role": role,
                "distance": float(min_distance)
            })

        except Exception as inner_e:
            print(f"\n[Recognition] UNEXPECTED INNER ERROR: {inner_e}")
            import traceback
            traceback.print_exc()
            print("--- RECOGNITION REQUEST FAILED (INNER EXCEPTION) ---\n")
            return jsonify({"error": "Recognition processing failed"}), 500

    except Exception as outer_e:
        print(f"\n[Recognition] UNEXPECTED OUTER ERROR: {outer_e}")
        import traceback
        traceback.print_exc()
        print("--- RECOGNITION REQUEST FAILED (OUTER EXCEPTION) ---\n")
        return jsonify({"error": "Recognition failed"}), 500
