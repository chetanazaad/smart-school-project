import sqlite3
import os
import numpy as np
import sys

# =========================
# DATABASE PATH RESOLUTION
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "smart_school.db")

# Fix sys.path for imports
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Use the same get_db function from utils to avoid connection conflicts
try:
    from utils.db import get_db
except ImportError:
    from smart_school_backend.utils.db import get_db


def get_connection():
    """
    Returns a new SQLite connection to smart_school.db
    Uses check_same_thread=False to allow multi-threaded access
    """
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ========================================================
# 1. CREATE face_embeddings TABLE
# ========================================================

def create_face_embeddings_table():
    """
    Creates face_embeddings table if it does not exist.
    This is now primarily for reference, as init_db.py is the source of truth.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS face_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
        student_id INTEGER,
        teacher_id INTEGER,
        name TEXT,
        email TEXT,
        class_name TEXT,
        section TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        embedding BLOB NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        UNIQUE(role, student_id, teacher_id),
        CHECK ((role = 'student' AND student_id IS NOT NULL AND teacher_id IS NULL) OR
               (role = 'teacher' AND teacher_id IS NOT NULL AND student_id IS NULL))
    )
    """)

    conn.commit()
    conn.close()
    print("✔ face_embeddings table verified/created.")


# ========================================================
# 2. STORE OR UPDATE FACE EMBEDDING
# ========================================================

def store_face_embedding(role, person_id, name, email, class_name, section, embedding, clear_existing=False):
    """
    Saves face embeddings in DB.
    If clear_existing is True, previous embeddings for this person are deleted.
    """
    conn = get_connection()
    cur = conn.cursor()

    embedding_blob = embedding.astype(np.float32).tobytes()

    if clear_existing:
        if role == 'student':
            cur.execute("DELETE FROM face_embeddings WHERE role = 'student' AND student_id = ?", (person_id,))
        elif role == 'teacher':
            cur.execute("DELETE FROM face_embeddings WHERE role = 'teacher' AND teacher_id = ?", (person_id,))

    if role == 'student':
        cur.execute("""
            INSERT INTO face_embeddings (role, student_id, name, email, class_name, section, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (role, person_id, name, email, class_name, section, embedding_blob))
    elif role == 'teacher':
        cur.execute("""
            INSERT INTO face_embeddings (role, teacher_id, name, email, class_name, section, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (role, person_id, name, email, class_name, section, embedding_blob))
    else:
        conn.close()
        raise ValueError("Role must be either 'student' or 'teacher'")


    conn.commit()
    conn.close()


# ========================================================
# 3. LOAD STORED EMBEDDINGS
# ========================================================

def load_all_embeddings():
    """
    Loads all embeddings from DB and returns:
    [
        {
            "role": "student" or "teacher",
            "person_id": ID,
            "name": "Cheta",
            ...
            "embedding": numpy.ndarray
        }
    ]
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT role, student_id, teacher_id, name, email, class_name, section, embedding
        FROM face_embeddings
    """)

    rows = cur.fetchall()
    conn.close()

    embeddings = []
    for role, student_id, teacher_id, name, email, class_name, section, emb_blob in rows:
        emb_array = np.frombuffer(emb_blob, dtype=np.float32)

        person_id = student_id if role == 'student' else teacher_id

        embeddings.append({
            "role": role,
            "person_id": person_id,
            "name": name,
            "email": email,
            "class_name": class_name,
            "section": section,
            "embedding": emb_array
        })

    return embeddings
