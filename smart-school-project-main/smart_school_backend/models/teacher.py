# models/teacher.py
import sys
import os

# Fix imports to work from any directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # smart_school_backend/
sys.path.insert(0, BASE_DIR)

try:
    from utils.db import get_db
except ImportError:
    from smart_school_backend.utils.db import get_db


def create_teacher_table(fresh=False):
    """Create teachers table - uses direct connection, not Flask context"""
    import sqlite3
    
    # Use the correct path - inside database folder
    db_path = os.path.join(BASE_DIR, "database", "smart_school.db")
    
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Drop table if fresh start requested
    if fresh:
        cursor.execute("DROP TABLE IF EXISTS teachers")
        db.commit()

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP
        );
    """)

    db.commit()

    # Ensure new columns exist on older databases (only if not fresh)
    if not fresh:
        try:
            cursor.execute("PRAGMA table_info(teachers)")
            cols = [r[1] for r in cursor.fetchall()]
        except Exception as e:
            print(f"Error checking table info for teachers: {e}")
            cols = []

        if cols:
            if "id_code" not in cols:
                try:
                    cursor.execute("ALTER TABLE teachers ADD COLUMN id_code TEXT")
                    db.commit()
                    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_teachers_id_code ON teachers(id_code)")
                    db.commit()
                    print("Migration: Successfully added id_code column to teachers table.")
                except Exception as e:
                    print(f"Error migrating teachers table (id_code): {e}")

            if "is_class_teacher" not in cols:
                try:
                    cursor.execute("ALTER TABLE teachers ADD COLUMN is_class_teacher INTEGER DEFAULT 0")
                    db.commit()
                    print("Migration: Successfully added is_class_teacher column to teachers table.")
                except Exception as e:
                    print(f"Error migrating teachers table (is_class_teacher): {e}")

            if "assigned_class" not in cols:
                try:
                    cursor.execute("ALTER TABLE teachers ADD COLUMN assigned_class TEXT")
                    db.commit()
                    print("Migration: Successfully added assigned_class column to teachers table.")
                except Exception as e:
                    print(f"Error migrating teachers table (assigned_class): {e}")

            if "assigned_section" not in cols:
                try:
                    cursor.execute("ALTER TABLE teachers ADD COLUMN assigned_section TEXT")
                    db.commit()
                    print("Migration: Successfully added assigned_section column to teachers table.")
                except Exception as e:
                    print(f"Error migrating teachers table (assigned_section): {e}")

            if "last_seen" not in cols:
                try:
                    cursor.execute("ALTER TABLE teachers ADD COLUMN last_seen TIMESTAMP")
                    db.commit()
                    print("Migration: Successfully added last_seen column to teachers table.")
                except Exception as e:
                    print(f"Error migrating teachers table (last_seen): {e}")
    
    db.close()
