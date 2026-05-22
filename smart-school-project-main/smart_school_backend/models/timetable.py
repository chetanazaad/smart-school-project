# models/timetable.py
from smart_school_backend.utils.db import get_db

def create_timetable_table():
    """
    Create the timetable table if it doesn't exist.
    Fields:
      id (PK)
      class_name (text) - e.g. "10A"
      day (text) - e.g. "Monday"
      period (integer) - period number
      subject (text)
      teacher_id (integer) - FK to teachers table (optional)
      start_time (text) - "09:00"
      end_time (text) - "09:40"
      created_at (timestamp)
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        day TEXT NOT NULL,
        period INTEGER NOT NULL,
        subject TEXT NOT NULL,
        teacher_id INTEGER,
        start_time TEXT,
        end_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    db.commit()

def get_timetable(class_name=None, day=None):
    db = get_db()
    q = "SELECT * FROM timetable"
    params = []
    clauses = []
    if class_name:
        clauses.append("class_name = ?")
        params.append(class_name)
    if day:
        clauses.append("day = ?")
        params.append(day)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY day, period"
    cur = db.execute(q, params)
    return cur.fetchall()

def add_timetable_entry(entry):
    """
    entry: dict with keys class_name, day, period, subject, teacher_id (optional), start_time (optional), end_time (optional)
    """
    db = get_db()
    db.execute("""
      INSERT INTO timetable (class_name, day, period, subject, teacher_id, start_time, end_time)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (entry.get("class_name"), entry.get("day"), entry.get("period"),
          entry.get("subject"), entry.get("teacher_id"), entry.get("start_time"), entry.get("end_time")))
    db.commit()

def update_timetable_entry(entry_id, data):
    db = get_db()
    db.execute("""
      UPDATE timetable
      SET class_name = ?, day = ?, period = ?, subject = ?, teacher_id = ?, start_time = ?, end_time = ?
      WHERE id = ?
    """, (data.get("class_name"), data.get("day"), data.get("period"),
          data.get("subject"), data.get("teacher_id"), data.get("start_time"),
          data.get("end_time"), entry_id))
    db.commit()

def delete_timetable_entry(entry_id):
    db = get_db()
    db.execute("DELETE FROM timetable WHERE id = ?", (entry_id,))
    db.commit()
