# smart_school_backend/face_engine/store.py

import numpy as np
try:
    from smart_school_backend.utils.db import get_db
except ImportError:
    from utils.db import get_db


def save_embedding(person_id, role: str, embedding, name=None, class_name=None, section=None, subject=None, clear_existing=False):
    """
    Save / update face embedding for a given person + role.
    If clear_existing is True, old embeddings for this person are removed.
    """
    db = get_db()
    cur = db.cursor()

    if clear_existing:
        # Remove existing embeddings for this person+role
        if role == 'student':
            cur.execute(
                "DELETE FROM face_embeddings WHERE student_id = ? AND role = ?",
                (person_id, role),
            )
        else:
            cur.execute(
                "DELETE FROM face_embeddings WHERE teacher_id = ? AND role = ?",
                (person_id, role),
            )


    emb_bytes = embedding.astype("float32").tobytes()

    # Insert with metadata to satisfy NOT NULL constraints on schema
    if role == 'student':
        cur.execute(
            "INSERT INTO face_embeddings (student_id, role, name, class_name, section, embedding) VALUES (?, ?, ?, ?, ?, ?)",
            (person_id, role, name or "", class_name or None, section or None, emb_bytes),
        )
    else:
        cur.execute(
            "INSERT INTO face_embeddings (teacher_id, role, name, class_name, section, embedding) VALUES (?, ?, ?, ?, ?, ?)",
            (person_id, role, name or "", class_name or None, section or None, emb_bytes),
        )

    db.commit()


def load_all_embeddings():
    """
    Load all stored embeddings.
    Returns list of dicts: {person_id, role, embedding(np.array)}.
    """
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT student_id, teacher_id, role, name, class_name, section, embedding FROM face_embeddings")
    rows = cur.fetchall()

    people = []
    for row in rows:
        student_id = row[0]
        teacher_id = row[1]
        role = row[2]
        name = row[3]
        class_name = row[4]
        section = row[5]
        emb_blob = row[6]
        
        person_id = student_id if role == 'student' else teacher_id
        emb = np.frombuffer(emb_blob, dtype="float32")
        people.append(
            {
                "person_id": person_id,
                "role": role,
                "name": name,
                "class_name": class_name,
                "section": section,
                "embedding": emb,
            }
        )

    return people
