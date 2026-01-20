# smart_school_backend/models/user.py

from utils.db import get_db   # ✅ FIXED import
from werkzeug.security import generate_password_hash, check_password_hash

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
