#!/usr/bin/env python3
"""
SINGLE COMPREHENSIVE DATABASE SETUP SCRIPT
==========================================

This is the ONLY file needed to:
1. DELETE the existing smart_school.db
2. CREATE a fresh database from scratch
3. Create all tables with complete schema
4. Add default admin user
5. Populate sample data (optional)

Usage:
    python setup_database.py

Options:
    python setup_database.py --reset         # Delete and recreate
    python setup_database.py --create-only   # Create without sample data
    python setup_database.py --help          # Show help
"""

import sqlite3
import os
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the database directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_school.db")

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

# ============================================================================
# DATABASE CLEANUP
# ============================================================================

def delete_existing_database():
    """Delete the existing database file if it exists"""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print_success(f"Deleted existing database: {DB_PATH}")
            return True
        except Exception as e:
            print_error(f"Failed to delete database: {str(e)}")
            return False
    else:
        print_info(f"No existing database found at {DB_PATH}")
        return True

# ============================================================================
# DATABASE CREATION
# ============================================================================

def create_users_table(cur):
    """Create users table"""
    cur.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student'))
    )
    """)
    print_success("Created table: users")

def create_students_table(cur):
    """Create students table"""
    cur.execute("""
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        id_code TEXT UNIQUE NOT NULL,
        class_name TEXT NOT NULL,
        section TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print_success("Created table: students")

def create_teachers_table(cur):
    """Create teachers table with class teacher support"""
    cur.execute("""
    CREATE TABLE teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        id_code TEXT UNIQUE NOT NULL,
        subject TEXT NOT NULL,
        is_class_teacher INTEGER DEFAULT 0,
        assigned_class TEXT,
        assigned_section TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print_success("Created table: teachers (with class teacher fields)")

def create_face_embeddings_table(cur):
    """Create face embeddings table"""
    cur.execute("""
    CREATE TABLE face_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
        person_id INTEGER NOT NULL,
        name TEXT,
        email TEXT,
        class_name TEXT,
        section TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        embedding BLOB NOT NULL,
        UNIQUE(person_id, role)
    )
    """)
    print_success("Created table: face_embeddings")

def create_student_attendance_table(cur):
    """Create student attendance table"""
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
    
    # Create indexes for performance
    cur.execute("""
        CREATE INDEX idx_student_attendance_date 
        ON student_attendance(date)
    """)
    
    cur.execute("""
        CREATE INDEX idx_student_attendance_student 
        ON student_attendance(student_id, date)
    """)
    
    cur.execute("""
        CREATE INDEX idx_student_attendance_class 
        ON student_attendance(class_name, date)
    """)
    
    print_success("Created table: student_attendance (with indexes)")

def create_teacher_attendance_table(cur):
    """Create teacher attendance table"""
    cur.execute("""
    CREATE TABLE teacher_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'leave')),
        marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        UNIQUE(teacher_id, date)
    )
    """)
    print_success("Created table: teacher_attendance")

def create_timetable_table(cur):
    """Create timetable table"""
    cur.execute("""
    CREATE TABLE timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        section TEXT NOT NULL,
        subject TEXT NOT NULL,
        teacher_name TEXT NOT NULL,
        day TEXT NOT NULL CHECK(day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print_success("Created table: timetable")

def create_parents_table(cur):
    """Create parents table"""
    cur.execute("""
    CREATE TABLE parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print_success("Created table: parents")

def create_all_tables(conn):
    """Create all database tables"""
    cur = conn.cursor()
    
    print_info("Creating all tables...")
    
    create_users_table(cur)
    create_students_table(cur)
    create_teachers_table(cur)
    create_face_embeddings_table(cur)
    create_student_attendance_table(cur)
    create_teacher_attendance_table(cur)
    create_timetable_table(cur)
    create_parents_table(cur)
    
    conn.commit()
    print_success("All tables created successfully")

# ============================================================================
# DEFAULT DATA
# ============================================================================

def create_default_admin(conn):
    """Create default admin user"""
    cur = conn.cursor()
    
    admin_email = "admin@school.com"
    admin_password = "admin123"
    hashed_pw = generate_password_hash(admin_password)
    
    try:
        cur.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, ("Admin User", admin_email, hashed_pw, "admin"))
        
        conn.commit()
        print_success("Default admin user created")
        print_info(f"  Email: {admin_email}")
        print_info(f"  Password: {admin_password}")
    except sqlite3.IntegrityError:
        print_warning("Admin user already exists")

def create_sample_data(conn):
    """Create sample data for testing"""
    cur = conn.cursor()
    
    try:
        # Sample students
        students_data = [
            ("Alice Johnson", "alice@school.com", "S001", "Class 10A", "Section A"),
            ("Bob Smith", "bob@school.com", "S002", "Class 10A", "Section A"),
            ("Charlie Brown", "charlie@school.com", "S003", "Class 10A", "Section B"),
        ]
        
        for name, email, id_code, class_name, section in students_data:
            try:
                cur.execute("""
                    INSERT INTO students (name, email, id_code, class_name, section)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, id_code, class_name, section))
            except sqlite3.IntegrityError:
                pass
        
        # Sample teachers
        teachers_data = [
            ("John Doe", "john@school.com", "T001", "Mathematics", 1, "Class 10A", "Section A"),
            ("Jane Smith", "jane@school.com", "T002", "English", 0, None, None),
            ("Mike Johnson", "mike@school.com", "T003", "Science", 0, None, None),
        ]
        
        for name, email, id_code, subject, is_class_teacher, assigned_class, assigned_section in teachers_data:
            try:
                cur.execute("""
                    INSERT INTO teachers (name, email, id_code, subject, is_class_teacher, assigned_class, assigned_section)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, email, id_code, subject, is_class_teacher, assigned_class, assigned_section))
            except sqlite3.IntegrityError:
                pass
        
        # Sample timetable
        timetable_data = [
            ("Class 10A", "Section A", "Mathematics", "John Doe", "Monday", "09:00", "10:00"),
            ("Class 10A", "Section A", "English", "Jane Smith", "Monday", "10:00", "11:00"),
            ("Class 10A", "Section A", "Science", "Mike Johnson", "Tuesday", "09:00", "10:00"),
        ]
        
        for class_name, section, subject, teacher_name, day, start_time, end_time in timetable_data:
            try:
                cur.execute("""
                    INSERT INTO timetable (class_name, section, subject, teacher_name, day, start_time, end_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (class_name, section, subject, teacher_name, day, start_time, end_time))
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        print_success("Sample data created")
    except Exception as e:
        print_warning(f"Could not create sample data: {str(e)}")

# ============================================================================
# MAIN SETUP FUNCTION
# ============================================================================

def setup_database(include_sample_data=True):
    """Main database setup function"""
    print_header("SMART SCHOOL DATABASE SETUP")
    print_info(f"Database path: {DB_PATH}\n")
    
    # Step 1: Delete existing database
    print_info("Step 1: Cleaning up existing database...")
    if not delete_existing_database():
        print_error("Failed to delete existing database")
        return False
    
    # Step 2: Create new database
    print_info("\nStep 2: Creating new database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        print_success("Database file created")
    except Exception as e:
        print_error(f"Failed to create database: {str(e)}")
        return False
    
    # Step 3: Create all tables
    print_info("\nStep 3: Creating all tables...")
    try:
        create_all_tables(conn)
    except Exception as e:
        print_error(f"Failed to create tables: {str(e)}")
        conn.close()
        return False
    
    # Step 4: Add default admin
    print_info("\nStep 4: Creating default admin user...")
    try:
        create_default_admin(conn)
    except Exception as e:
        print_error(f"Failed to create admin: {str(e)}")
    
    # Step 5: Add sample data (optional)
    if include_sample_data:
        print_info("\nStep 5: Creating sample data...")
        try:
            create_sample_data(conn)
        except Exception as e:
            print_error(f"Failed to create sample data: {str(e)}")
    
    conn.close()
    
    # Final confirmation
    print_header("DATABASE SETUP COMPLETE")
    print_success(f"Database created successfully at: {DB_PATH}")
    print_info(f"File size: {os.path.getsize(DB_PATH)} bytes")
    print_info("\nYou can now run: python app.py")
    
    return True

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def show_help():
    """Show help message"""
    print("""
    SMART SCHOOL DATABASE SETUP
    
    Usage:
        python setup_database.py [OPTIONS]
    
    Options:
        --reset         Delete and recreate database (default)
        --create-only   Create without sample data
        --help          Show this help message
    
    Examples:
        python setup_database.py                 # Full reset with sample data
        python setup_database.py --create-only   # Create empty database
        python setup_database.py --help          # Show help
    """)

def main():
    """Main entry point"""
    include_sample_data = True
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h', 'help']:
            show_help()
            return
        elif arg == '--create-only':
            include_sample_data = False
        elif arg == '--reset':
            include_sample_data = True
        else:
            print_error(f"Unknown option: {arg}")
            show_help()
            return
    
    # Run setup
    success = setup_database(include_sample_data=include_sample_data)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
