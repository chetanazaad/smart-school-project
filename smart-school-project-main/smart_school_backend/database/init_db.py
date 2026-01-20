import sqlite3
import os
from werkzeug.security import generate_password_hash

# Correct database directory path relative to backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_school.db")

def init_db():
    print("📌 Initializing Smart School Database…")
    print(f"📁 Database Path: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ----------------------------------------------------
    # USERS TABLE
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # ----------------------------------------------------
    # STUDENTS TABLE
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        id_code TEXT,
        class_name TEXT,
        section TEXT
    )
    """)

    # ----------------------------------------------------
    # TEACHERS TABLE
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        id_code TEXT,
        subject TEXT
    )
    """)

    # ----------------------------------------------------
    # FACE EMBEDDINGS TABLE
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS face_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        person_id TEXT NOT NULL UNIQUE,
        name TEXT,
        email TEXT,
        class_name TEXT,
        section TEXT,
        created_at TEXT,
        embedding BLOB NOT NULL
    )
    """)

    # ----------------------------------------------------
    # FIXED STUDENT ATTENDANCE TABLE
    # (MATCHES student_attendance.py)
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_attendance (
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

    # Indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_attendance_date 
        ON student_attendance(date)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_attendance_student 
        ON student_attendance(student_id, date)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_attendance_class 
        ON student_attendance(class_name, date)
    """)

    # ----------------------------------------------------
    # TEACHER ATTENDANCE (Updated with constraints)
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        UNIQUE(teacher_id, date)
    )
    """)

    # ----------------------------------------------------
    # TIMETABLE TABLE
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        section TEXT NOT NULL,
        subject TEXT NOT NULL,
        teacher_name TEXT NOT NULL,
        day TEXT NOT NULL,
        start_time TEXT,
        end_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ----------------------------------------------------
    # PARENTS TABLE
    # ----------------------------------------------------
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

    print("✔ All tables created successfully")

    # ----------------------------------------------------
    # Create Default Admin
    # ----------------------------------------------------
    hashed_pw = generate_password_hash("admin123")

    cur.execute("""
        INSERT OR IGNORE INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, ("Admin", "admin@school.com", hashed_pw, "admin"))

    print("✔ Default admin created")
    print("   Email: admin@school.com")
    print("   Password: admin123")

    conn.commit()
    conn.close()
    print("🎉 Database setup completed successfully!")


if __name__ == "__main__":
    init_db()
