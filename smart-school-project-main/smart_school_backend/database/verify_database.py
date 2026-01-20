#!/usr/bin/env python3
"""Quick verification script to check database tables"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smart_school.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("\n" + "="*60)
print("DATABASE VERIFICATION")
print("="*60 + "\n")

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()

print(f"✓ Total Tables: {len(tables)}\n")

for table_name in tables:
    table = table_name[0]
    cur.execute(f"PRAGMA table_info({table})")
    columns = cur.fetchall()
    print(f"📋 Table: {table}")
    print(f"   Columns: {len(columns)}")
    for col in columns:
        col_name, col_type = col[1], col[2]
        print(f"      - {col_name} ({col_type})")
    
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"   Rows: {count}\n")

print("="*60)
print("✓ Database is ready for use!")
print("="*60 + "\n")

conn.close()
