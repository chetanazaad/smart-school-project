# models/teacher.py
from smart_school_backend.utils.db import get_db


def create_teacher_table():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            id_code TEXT UNIQUE,
            subject TEXT NOT NULL,
            is_class_teacher INTEGER DEFAULT 0,
            assigned_class TEXT,
            assigned_section TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    db.commit()

    # Ensure new columns exist on older databases
    try:
        cursor.execute("PRAGMA table_info(teachers)")
        cols = [r[1] for r in cursor.fetchall()]
        if "id_code" not in cols:
            cursor.execute("ALTER TABLE teachers ADD COLUMN id_code TEXT UNIQUE")
            db.commit()
        if "is_class_teacher" not in cols:
            cursor.execute("ALTER TABLE teachers ADD COLUMN is_class_teacher INTEGER DEFAULT 0")
            db.commit()
        if "assigned_class" not in cols:
            cursor.execute("ALTER TABLE teachers ADD COLUMN assigned_class TEXT")
            db.commit()
        if "assigned_section" not in cols:
            cursor.execute("ALTER TABLE teachers ADD COLUMN assigned_section TEXT")
            db.commit()
    except Exception:
        pass
