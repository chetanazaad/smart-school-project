# create_admin.py
import os
import sys

# ============================================================
# FIX PYTHON PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # smart_school_backend/
ROOT_DIR = os.path.dirname(BASE_DIR)                    # project root

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from werkzeug.security import generate_password_hash
from smart_school_backend.app import app
from smart_school_backend.utils.db import get_db
from smart_school_backend.database.init_db import init_db

def create_admin():
    print("Executing create_admin (v3 - fixed)...")
    with app.app_context():
        init_db()  # ensure tables exist
        
        print("... getting db connection in create_admin.")
        conn = get_db()
        cursor = conn.cursor()

        name = "Super Admin"
        email = "admin@school.com"
        password = "admin123"
        role = "admin"  # lowercase to match frontend

        hashed_pw = generate_password_hash(password)

        try:
            # Check if admin already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()
            if existing:
                print("INFO: Admin user already exists. Updating password and role...")
                cursor.execute(
                    "UPDATE users SET password = ?, role = ? WHERE email = ?",
                    (hashed_pw, role, email)
                )
                conn.commit()
                print("✅ Admin user updated successfully")
                print("Login Email: admin@school.com")
                print("Password: admin123")
                return

            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, hashed_pw, role)
            )
            conn.commit()
            print("✅ Admin user created successfully")
            print("Login Email: admin@school.com")
            print("Password: admin123")
        except Exception as e:
            # This is the only place an error should happen now
            print(f"❌ A database error occurred: {e}")

if __name__ == "__main__":
    create_admin()