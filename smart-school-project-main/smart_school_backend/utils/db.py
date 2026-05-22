import sqlite3
import os
from flask import g

# Absolute path to the database inside backend/database/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # smart_school_backend/
DB_DIR = os.path.join(BASE_DIR, "database")                            # backend/database/
DB_PATH = os.path.join(DB_DIR, "smart_school.db")                   # backend/database/smart_school.db

DB_PATH = os.path.abspath(DB_PATH)

# PostgreSQL config
POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Ensure directory exists
os.makedirs(DB_DIR, exist_ok=True)


def get_db():
    if "db" not in g:
        if POSTGRES_URL:
            # Import psycopg2 only when PostgreSQL is configured
            import psycopg2
            g.db = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_URL,
            )
        else:
            g.db = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
