#!/usr/bin/env python3
"""Check face_embeddings table schema"""

import sqlite3

db = sqlite3.connect('database/smart_school.db')
cur = db.cursor()

# Check actual schema
cur.execute("PRAGMA table_info(face_embeddings)")
columns = cur.fetchall()

print('=== FACE_EMBEDDINGS TABLE SCHEMA ===')
for col in columns:
    print(f'  {col[1]:20} {col[2]}')

db.close()
