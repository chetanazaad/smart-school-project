# smart_school_backend/models/user.py

from utils.db import get_db   # ✅ FIXED import
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os

# Password strength requirements
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))

def validate_password_strength(password):
    """
    Validate password meets minimum strength requirements.
    Returns (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, None

# Create users table
def create_user_table():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    db.commit()


# Fetch user by email
def get_user_by_email(email):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    row = cur.fetchone()

    return dict(row) if row else None


# Create new user (admin, teacher, student, parent)
def create_user(name, email, password, role):
    db = get_db()
    cur = db.cursor()

    hashed_pw = generate_password_hash(password)

    cur.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, hashed_pw, role))

    db.commit()

    return cur.lastrowid


# Fetch user by ID
def get_user_by_id(user_id):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()

    return dict(row) if row else None


# Validate login
def validate_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return None

    if check_password_hash(user["password"], password):
        return user

    return None


# Update user email
def update_user_email(user_id, new_email):
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE users
        SET email = ?
        WHERE id = ?
    """, (new_email, user_id))

    db.commit()
    return True


# Update user password
def update_user_password(user_id, new_password):
    db = get_db()
    cur = db.cursor()

    hashed_pw = generate_password_hash(new_password)

    cur.execute("""
        UPDATE users
        SET password = ?
        WHERE id = ?
    """, (hashed_pw, user_id))

    db.commit()
    return True

# Update user profile details
def update_user_profile(old_email, name=None, new_email=None, password=None):
    db = get_db()
    cur = db.cursor()
    
    update_fields = []
    params = []
    
    if name:
        update_fields.append("name=?")
        params.append(name)
    if new_email:
        update_fields.append("email=?")
        params.append(new_email)
    if password:
        hashed_pw = generate_password_hash(password)
        update_fields.append("password=?")
        params.append(hashed_pw)
        
    if not update_fields:
        return False
        
    params.append(old_email)
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE email=?"
    cur.execute(query, params)
    db.commit()
    return cur.rowcount > 0

# Delete user by email
def delete_user_by_email(email):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM users WHERE email=?", (email,))
    db.commit()
    return cur.rowcount > 0
