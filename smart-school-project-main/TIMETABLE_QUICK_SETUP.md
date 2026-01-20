# Timetable System - Quick Setup Guide

## Overview
The timetable system allows:
- **Admin Dashboard**: Add/manage timetable entries for classes
- **Students**: View their weekly class timetable based on their class and section
- **Teachers**: View their weekly teaching schedule

## API Endpoints

### 1. Add Timetable Entry (Admin Dashboard)
**Endpoint**: `POST /api/timetable/add`

**Authentication**: Required (JWT token)

**Request Body**:
```json
{
    "class_name": "10",
    "section": "A",
    "subject": "Math",
    "teacher_name": "Ratan",
    "day": "Monday",
    "start_time": "09:00",
    "end_time": "09:40"
}
```

**Response** (201 Created):
```json
{
    "message": "Timetable entry added successfully",
    "id": 1
}
```

**Required Fields**:
- `class_name`: Class number (e.g., "10", "9", "8")
- `section`: Section letter (e.g., "A", "B", "C")
- `subject`: Subject name (e.g., "Math", "English", "Science")
- `teacher_name`: Teacher's name (e.g., "Ratan", "Priya")
- `day`: Day of the week (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
- `start_time`: Start time in HH:MM format (e.g., "09:00")
- `end_time`: End time in HH:MM format (e.g., "09:40")

---

### 2. Get Student Timetable (Student Dashboard)
**Endpoint**: `GET /api/timetable/student/<student_id>/week`

**Authentication**: Required (JWT token)

**Example**: `GET /api/timetable/student/1/week`

**Response** (200 OK):
```json
{
    "student_name": "John Doe",
    "class_name": "10",
    "section": "A",
    "timetable": [
        {
            "id": 1,
            "day": "Monday",
            "subject": "Math",
            "teacher_name": "Ratan",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "id": 2,
            "day": "Monday",
            "subject": "English",
            "teacher_name": "Priya",
            "start_time": "09:40",
            "end_time": "10:20"
        },
        {
            "id": 3,
            "day": "Tuesday",
            "subject": "Science",
            "teacher_name": "Kumar",
            "start_time": "09:00",
            "end_time": "09:40"
        }
    ]
}
```

**What it does**:
- Retrieves the student's class and section from the database
- Returns all timetable entries for that class/section
- Sorted by day of the week and start time

---

### 3. Get Teacher Timetable (Teacher Dashboard)
**Endpoint**: `GET /api/timetable/teacher/<teacher_id>/week`

**Authentication**: Required (JWT token)

**Example**: `GET /api/timetable/teacher/1/week`

**Response** (200 OK):
```json
{
    "teacher_name": "Ratan",
    "timetable": [
        {
            "id": 1,
            "day": "Monday",
            "class_name": "10",
            "section": "A",
            "subject": "Math",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "id": 4,
            "day": "Monday",
            "class_name": "10",
            "section": "B",
            "subject": "Math",
            "start_time": "10:00",
            "end_time": "10:40"
        },
        {
            "id": 5,
            "day": "Tuesday",
            "class_name": "9",
            "section": "A",
            "subject": "Math",
            "start_time": "09:00",
            "end_time": "09:40"
        }
    ]
}
```

**What it does**:
- Retrieves all classes taught by the teacher (matched by teacher name)
- Returns timetable entries for all their classes
- Sorted by day of the week and start time

---

### 4. Get Timetable by Class (Generic Endpoint)
**Endpoint**: `GET /api/timetable/<class_name>/<section>`

**Authentication**: Required (JWT token)

**Example**: `GET /api/timetable/10/A`

**Response** (200 OK):
```json
{
    "timetable": [
        {
            "id": 1,
            "class_name": "10",
            "section": "A",
            "subject": "Math",
            "teacher_name": "Ratan",
            "day": "Monday",
            "start_time": "09:00",
            "end_time": "09:40"
        }
    ]
}
```

---

### 5. Delete Timetable Entry
**Endpoint**: `DELETE /api/timetable/<entry_id>`

**Authentication**: Required (JWT token)

**Example**: `DELETE /api/timetable/1`

**Response** (200 OK):
```json
{
    "message": "Timetable entry removed successfully"
}
```

---

## Setup Instructions

### Step 1: Ensure Database Table Exists
The timetable table should already exist. If not, run:
```python
python smart_school_backend/database/init_db.py
```

### Step 2: Add Sample Timetable Data (Using Admin Dashboard)
Use the POST endpoint to add timetable entries:

```bash
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_name": "10",
    "section": "A",
    "subject": "Math",
    "teacher_name": "Ratan",
    "day": "Monday",
    "start_time": "09:00",
    "end_time": "09:40"
  }'
```

### Step 3: View Student Timetable
Once timetable entries are added, students can view their schedule:

```bash
curl -X GET http://localhost:5000/api/timetable/student/1/week \
  -H "Authorization: Bearer STUDENT_JWT_TOKEN"
```

### Step 4: View Teacher Timetable
Teachers can view their teaching schedule:

```bash
curl -X GET http://localhost:5000/api/timetable/teacher/1/week \
  -H "Authorization: Bearer TEACHER_JWT_TOKEN"
```

---

## Important Notes

1. **Student Records Required**: Students must exist in the `students` table with their `class_name` and `section` populated.

2. **Teacher Matching**: The timetable system matches teachers by name. Ensure teacher names in timetable entries exactly match the names in the `teachers` table.

3. **Day Format**: Days must be exact case-sensitive matches: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

4. **Time Format**: Times must be in 24-hour HH:MM format (e.g., "09:00", "14:30")

5. **Authentication**: All endpoints require JWT authentication. Include the JWT token in the Authorization header.

---

## Example Workflow

### 1. Add Multiple Timetable Entries

```bash
# Math class for Class 10A on Monday
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_name": "10",
    "section": "A",
    "subject": "Math",
    "teacher_name": "Ratan",
    "day": "Monday",
    "start_time": "09:00",
    "end_time": "09:40"
  }'

# English class for Class 10A on Monday
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_name": "10",
    "section": "A",
    "subject": "English",
    "teacher_name": "Priya",
    "day": "Monday",
    "start_time": "09:40",
    "end_time": "10:20"
  }'
```

### 2. Student Views Their Timetable
When a student logs in and requests their timetable, they'll see all classes for their class/section:

```bash
curl -X GET http://localhost:5000/api/timetable/student/5/week \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

Response shows all classes scheduled for class 10A throughout the week.

### 3. Teacher Views Their Schedule
When a teacher logs in and requests their timetable:

```bash
curl -X GET http://localhost:5000/api/timetable/teacher/2/week \
  -H "Authorization: Bearer TEACHER_TOKEN"
```

Response shows all classes taught by that teacher throughout the week.

---

## Troubleshooting

### Issue: "Student not found" (404)
- Ensure the student exists in the database
- Verify `student_id` is correct

### Issue: "Teacher not found" (404)
- Ensure the teacher exists in the database
- Verify `teacher_id` is correct

### Issue: "All fields are required" (400)
- Ensure all required fields are provided in the POST request
- Check for empty values

### Issue: Empty timetable for student/teacher
- Add timetable entries first using the POST endpoint
- Ensure class_name and section match exactly (case-sensitive)
- Ensure teacher_name in timetable matches the teacher's name exactly

---

## Database Schema

```sql
CREATE TABLE timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL,
    subject TEXT NOT NULL,
    teacher_name TEXT NOT NULL,
    day TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Frontend Integration

The frontend can now:

1. **Admin Panel**: Add/edit/delete timetable entries
2. **Student Dashboard**: Display their weekly schedule with all subjects and teachers
3. **Teacher Dashboard**: Display their teaching schedule across all classes

This allows students like "John Doe" from class 10A to see their complete weekly timetable, and teachers like "Ratan" to see all their classes for the week.
