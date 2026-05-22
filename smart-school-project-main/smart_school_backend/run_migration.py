import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "smart_school.db")

def migrate():
    print(f"Migrating {DB_PATH}")
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    # Disable foreign keys temporarily
    cur.execute("PRAGMA foreign_keys = OFF")
    
    # Let's ensure teachers table has the expected columns
    try:
        cur.execute("PRAGMA table_info(teachers)")
        cols = [r[1] for r in cur.fetchall()]
        if "id_code" not in cols:
            cur.execute("ALTER TABLE teachers ADD COLUMN id_code TEXT UNIQUE")
            print("Added id_code to teachers")
        if "is_class_teacher" not in cols:
            cur.execute("ALTER TABLE teachers ADD COLUMN is_class_teacher INTEGER DEFAULT 0")
            print("Added is_class_teacher to teachers")
        if "assigned_class" not in cols:
            cur.execute("ALTER TABLE teachers ADD COLUMN assigned_class TEXT")
            print("Added assigned_class to teachers")
        if "assigned_section" not in cols:
            cur.execute("ALTER TABLE teachers ADD COLUMN assigned_section TEXT")
            print("Added assigned_section to teachers")
        if "last_seen" not in cols:
            cur.execute("ALTER TABLE teachers ADD COLUMN last_seen TIMESTAMP")
            print("Added last_seen to teachers")
    except Exception as e:
        print(f"Error checking/updating teachers table: {e}")

    try:
        # Check if student_attendance table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_attendance'")
        if cur.fetchone():
            cur.execute("ALTER TABLE student_attendance RENAME TO student_attendance_old")
            cur.execute("""
            CREATE TABLE student_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                date DATE NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'leave')),
                marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                marked_by INTEGER,
                notes TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY(marked_by) REFERENCES users(id),
                UNIQUE(student_id, date)
            )
            """)
            cur.execute("INSERT INTO student_attendance SELECT * FROM student_attendance_old")
            cur.execute("DROP TABLE student_attendance_old")
            print("Migrated student_attendance table with ON DELETE CASCADE.")
            
            # Recreate indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_student_attendance_date ON student_attendance(date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_student_attendance_student ON student_attendance(student_id, date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_student_attendance_class ON student_attendance(class_name, date)")
    except Exception as e:
        print(f"Error migrating student_attendance: {e}")

    try:
        # Check if face_embeddings table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='face_embeddings'")
        if cur.fetchone():
            cur.execute("ALTER TABLE face_embeddings RENAME TO face_embeddings_old")
            cur.execute("""
            CREATE TABLE face_embeddings (
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
            cur.execute("INSERT INTO face_embeddings SELECT * FROM face_embeddings_old")
            cur.execute("DROP TABLE face_embeddings_old")
            print("Migrated face_embeddings table with ON DELETE CASCADE.")
            
            # Recreate indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_face_embeddings_role_student ON face_embeddings(role, student_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_face_embeddings_role_teacher ON face_embeddings(role, teacher_id)")
    except Exception as e:
        print(f"Error migrating face_embeddings: {e}")

    try:
        # Fix teacher_attendance table as well to add ON DELETE CASCADE just in case
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teacher_attendance'")
        if cur.fetchone():
            cur.execute("ALTER TABLE teacher_attendance RENAME TO teacher_attendance_old")
            cur.execute("""
            CREATE TABLE teacher_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                UNIQUE(teacher_id, date)
            )
            """)
            cur.execute("INSERT INTO teacher_attendance SELECT * FROM teacher_attendance_old")
            cur.execute("DROP TABLE teacher_attendance_old")
            print("Migrated teacher_attendance table with ON DELETE CASCADE.")
            
            cur.execute("CREATE INDEX IF NOT EXISTS idx_teacher_attendance_teacher_date ON teacher_attendance(teacher_id, date)")
    except Exception as e:
        print(f"Error migrating teacher_attendance: {e}")


    cur.execute("PRAGMA foreign_keys = ON")
    db.commit()
    db.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
