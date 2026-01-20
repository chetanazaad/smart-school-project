#!/usr/bin/env python3
"""Add missing columns to teachers table"""

import sqlite3

db_path = 'database/smart_school.db'
db = sqlite3.connect(db_path)
cur = db.cursor()

print('Adding missing columns to teachers table...')

try:
    # Check if columns already exist
    cur.execute("PRAGMA table_info(teachers)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'is_class_teacher' not in columns:
        print('  Adding: is_class_teacher')
        cur.execute('ALTER TABLE teachers ADD COLUMN is_class_teacher INTEGER DEFAULT 0')
    
    if 'assigned_class' not in columns:
        print('  Adding: assigned_class')
        cur.execute('ALTER TABLE teachers ADD COLUMN assigned_class TEXT')
    
    if 'assigned_section' not in columns:
        print('  Adding: assigned_section')
        cur.execute('ALTER TABLE teachers ADD COLUMN assigned_section TEXT')
    
    db.commit()
    
    # Show updated schema
    print('\n=== UPDATED TEACHERS TABLE SCHEMA ===')
    cur.execute("PRAGMA table_info(teachers)")
    for col in cur.fetchall():
        print(f'  {col[1]:20} {col[2]}')
    
    print('\n✅ Migration completed successfully!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()

db.close()
