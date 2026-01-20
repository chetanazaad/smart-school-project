#!/usr/bin/env python3
"""Clean all records from database while preserving schema"""

import sqlite3
import os

db_path = 'database/smart_school.db'

if not os.path.exists(db_path):
    print('Database not found')
    exit(1)

db = sqlite3.connect(db_path)
cur = db.cursor()

print('Cleaning database...')

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

for table in tables:
    table_name = table[0]
    if table_name != 'sqlite_sequence':
        print(f'  Clearing table: {table_name}')
        cur.execute(f'DELETE FROM {table_name}')

db.commit()

# Show final state
print('\n=== DATABASE CLEANED ===')
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
for table in tables:
    if table[0] != 'sqlite_sequence':
        table_name = table[0]
        cur.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cur.fetchone()[0]
        print(f'  {table_name}: {count} records')

db.close()
print('\n✅ Database cleaned successfully!')
