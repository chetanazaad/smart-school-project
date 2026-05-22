import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

# Fix imports to work from any directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # smart_school_backend/
sys.path.insert(0, BASE_DIR)

try:
    from models.teacher import create_teacher_table
except ImportError:
    from smart_school_backend.models.teacher import create_teacher_table

# Correct database directory path - inside database folder
DB_PATH = os.path.join(BASE_DIR, "database", "smart_school.db")

def init_db(verbose=False, fresh=False):
    if verbose:
        print("📌 Initializing Smart School Database…")
        print(f"📁 Database Path: {DB_PATH}")

    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # If fresh=True, delete existing database to start fresh
    if fresh and os.path.exists(DB_PATH):
        if verbose:
            print("🗑️  Removing old database...")
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop all tables if fresh start (to ensure clean database)
    if fresh:
        if verbose:
            print("🗑️  Dropping existing tables for fresh start...")
        cur.execute("DROP TABLE IF EXISTS face_embeddings")
        cur.execute("DROP TABLE IF EXISTS student_attendance")
        cur.execute("DROP TABLE IF EXISTS teacher_attendance")
        cur.execute("DROP TABLE IF EXISTS students")
        cur.execute("DROP TABLE IF EXISTS teachers")
        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("DROP TABLE IF EXISTS parents")
        cur.execute("DROP TABLE IF EXISTS timetable")
        conn.commit()
        if verbose:
            print("✔ All existing tables dropped")

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
        roll_number TEXT,
        class_name TEXT,
        section TEXT
    )
    """)

    # ----------------------------------------------------
    # TEACHERS TABLE - Managed by smart_school_backend.models.teacher
    # ----------------------------------------------------
    create_teacher_table(fresh=fresh)

    # ----------------------------------------------------
    # FACE EMBEDDINGS TABLE
    # ----------------------------------------------------
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
        CHECK ((role = 'student' AND student_id IS NOT NULL AND teacher_id IS NULL) OR
               (role = 'teacher' AND teacher_id IS NOT NULL AND student_id IS NULL))
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

    if verbose:
        print("✔ All tables created successfully")

    # ----------------------------------------------------
    # ADDITIONAL INDEXES FOR PERFORMANCE OPTIMIZATION (Task #28)
    # ----------------------------------------------------
    
    # Users table indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_role 
        ON users(role)
    """)

    # Students table indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_students_class_name 
        ON students(class_name)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_students_id_code 
        ON students(id_code)
    """)

    # Timetable indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_timetable_class 
        ON timetable(class_name, section)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_timetable_teacher 
        ON timetable(teacher_name, day)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_timetable_day 
        ON timetable(day, start_time)
    """)

    # Face embeddings indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_face_embeddings_role_student 
        ON face_embeddings(role, student_id)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_face_embeddings_role_teacher 
        ON face_embeddings(role, teacher_id)
    """)

    # Teacher attendance indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_teacher_attendance_teacher_date 
        ON teacher_attendance(teacher_id, date)
    """)

    if verbose:
        print("✔ Database indexes created successfully")

    # ----------------------------------------------------
    # Create Default Admin
    # ----------------------------------------------------
    hashed_pw = generate_password_hash("admin123")

    cur.execute("""
        INSERT OR IGNORE INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, ("Admin", "admin@school.com", hashed_pw, "admin"))

    if verbose:
        print("✔ Default admin created")
        print("   Email: admin@school.com")
        print("   Password: admin123")

    conn.commit()
    conn.close()
    if verbose:
        print("🎉 Database setup completed successfully!")


if __name__ == "__main__":
    init_db()
