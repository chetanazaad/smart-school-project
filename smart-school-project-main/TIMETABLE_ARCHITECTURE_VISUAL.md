# TIMETABLE SYSTEM - VISUAL ARCHITECTURE

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADMIN DASHBOARD                              │
│                                                                   │
│  [Add Timetable Entry]                                           │
│  - Class: 10, Section: A                                         │
│  - Subject: Math, Teacher: Ratan                                 │
│  - Day: Monday, Time: 09:00-09:40                                │
│                                                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │ POST /api/timetable/add
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API                                 │
│                  (Flask + SQLite)                                │
│                                                                   │
│  Route: POST /api/timetable/add                                  │
│  ├─ Validate all fields                                          │
│  ├─ Insert into timetable table                                  │
│  └─ Return success + ID                                          │
│                                                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TIMETABLE TABLE (SQLite)                        │
│                                                                   │
│  id | class_name | section | subject | teacher_name | day | ... │
│  ─────────────────────────────────────────────────────────────── │
│  1  | 10         | A       | Math    | Ratan        | Mon | ... │
│  2  | 10         | A       | English | Priya        | Mon | ... │
│  3  | 10         | B       | Math    | Ratan        | Mon | ... │
│  4  | 9          | A       | Math    | Ratan        | Tue | ... │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Student Dashboard Flow

```
┌────────────────────────────────────────────────────────────┐
│                  STUDENT DASHBOARD                         │
│                                                             │
│  Welcome, John Doe                                          │
│  [View My Timetable]                                        │
│                                                             │
└──────────────────┬───────────────────────────────────────┘
                   │ GET /api/timetable/student/1/week
                   ▼
        ┌──────────────────────────┐
        │    BACKEND LOGIC         │
        │                          │
        │ 1. Get student (ID=1)    │
        │    ↓                     │
        │    name: John Doe        │
        │    class: 10             │
        │    section: A            │
        │                          │
        │ 2. Query timetable       │
        │    WHERE class = 10      │
        │    AND section = A       │
        │    ↓                     │
        │    [4 rows found]        │
        │                          │
        │ 3. Sort by day, time     │
        │    ↓                     │
        │    Monday entries first  │
        │    Then Tuesday, etc.    │
        │                          │
        └──────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│              DISPLAYED TO STUDENT                          │
│                                                             │
│  Class: 10A - Weekly Timetable                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ Day       │ Subject    │ Teacher  │ Time     │          │
│  ├──────────────────────────────────────────────┤          │
│  │ Monday    │ Math       │ Ratan    │ 09:00-40 │          │
│  │ Monday    │ English    │ Priya    │ 09:40-20 │          │
│  │ Monday    │ Science    │ Kumar    │ 10:20-00 │          │
│  │ Tuesday   │ Math       │ Ratan    │ 09:00-40 │          │
│  │ Tuesday   │ PE         │ Sports   │ 09:40-20 │          │
│  │ ...       │ ...        │ ...      │ ...      │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Teacher Dashboard Flow

```
┌────────────────────────────────────────────────────────────┐
│                 TEACHER DASHBOARD                          │
│                                                             │
│  Welcome, Ratan                                             │
│  [View My Schedule]                                         │
│                                                             │
└──────────────────┬───────────────────────────────────────┘
                   │ GET /api/timetable/teacher/1/week
                   ▼
        ┌──────────────────────────┐
        │    BACKEND LOGIC         │
        │                          │
        │ 1. Get teacher (ID=1)    │
        │    ↓                     │
        │    name: Ratan           │
        │                          │
        │ 2. Query timetable       │
        │    WHERE teacher = Ratan │
        │    ↓                     │
        │    [6 rows found]        │
        │                          │
        │ 3. Sort by day, time     │
        │    ↓                     │
        │    Monday entries first  │
        │    Then Tuesday, etc.    │
        │                          │
        └──────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│              DISPLAYED TO TEACHER                          │
│                                                             │
│  Ratan's Teaching Schedule                                  │
│  ┌──────────────────────────────────────────────┐          │
│  │ Day       │ Class │ Subject    │ Time      │          │
│  ├──────────────────────────────────────────────┤          │
│  │ Monday    │ 10A   │ Math       │ 09:00-40  │          │
│  │ Monday    │ 10B   │ Math       │ 10:00-40  │          │
│  │ Monday    │ 9A    │ Math       │ 14:00-40  │          │
│  │ Tuesday   │ 10A   │ Math       │ 09:00-40  │          │
│  │ Tuesday   │ 10B   │ Math       │ 10:00-40  │          │
│  │ ...       │ ...   │ ...        │ ...       │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## API Call Flow Diagram

```
                    FRONTEND
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    [Admin]        [Student]       [Teacher]
       │              │              │
       │ POST /add     │ GET /week    │ GET /week
       │ (add entry)   │ /student     │ /teacher
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
                  BACKEND API
                 (timetable.py)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    add_timetable  get_student   get_teacher
    ()              _timetable()  _timetable()
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
                   DATABASE
                  (timetable)
                      │
                ┌─────┴─────┐
                ▼           ▼
            INSERT      SELECT
            (add)       (fetch)
```

---

## Data Flow: Adding Timetable

```
Admin Input:
┌─────────────────────────────────────┐
│ class_name: "10"                    │
│ section: "A"                        │
│ subject: "Math"                     │
│ teacher_name: "Ratan"               │
│ day: "Monday"                       │
│ start_time: "09:00"                 │
│ end_time: "09:40"                   │
└─────────────────────────────────────┘
            │
            ▼
    [POST /api/timetable/add]
            │
            ▼
    Backend Validation:
    ├─ All fields present? ✓
    ├─ Correct format? ✓
    ├─ Valid day name? ✓
    └─ Valid time format? ✓
            │
            ▼
    Insert into Database:
    INSERT INTO timetable
    (class_name, section, subject, teacher_name, day, start_time, end_time)
    VALUES (...)
            │
            ▼
    Response (201):
    {
        "message": "Timetable entry added successfully",
        "id": 1
    }
```

---

## Data Flow: Student Viewing Timetable

```
Student Request:
[GET /api/timetable/student/1/week]
            │
            ▼
Step 1: Fetch Student Data
    SELECT name, class_name, section
    FROM students WHERE id = 1
            │
            ├─ name: "John Doe"
            ├─ class_name: "10"
            └─ section: "A"
            │
            ▼
Step 2: Fetch Student's Classes
    SELECT * FROM timetable
    WHERE class_name = "10"
    AND section = "A"
    ORDER BY day, start_time
            │
            ├─ ID 1: Math, Ratan, Mon 09:00-40
            ├─ ID 2: English, Priya, Mon 09:40-20
            ├─ ID 3: Science, Kumar, Mon 10:20-00
            ├─ ID 4: Math, Ratan, Tue 09:00-40
            ├─ ID 5: PE, Sports, Tue 09:40-20
            └─ ...
            │
            ▼
Step 3: Format Response (200):
{
    "student_name": "John Doe",
    "class_name": "10",
    "section": "A",
    "timetable": [
        {
            "day": "Monday",
            "subject": "Math",
            "teacher_name": "Ratan",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        ...
    ]
}
            │
            ▼
    Frontend Display
```

---

## Data Flow: Teacher Viewing Schedule

```
Teacher Request:
[GET /api/timetable/teacher/1/week]
            │
            ▼
Step 1: Fetch Teacher Data
    SELECT name FROM teachers WHERE id = 1
            │
            └─ name: "Ratan"
            │
            ▼
Step 2: Fetch Teacher's Classes
    SELECT * FROM timetable
    WHERE teacher_name = "Ratan"
    ORDER BY day, start_time
            │
            ├─ ID 1: 10A, Math, Mon 09:00-40
            ├─ ID 3: 10B, Math, Mon 10:00-40
            ├─ ID 4: 9A, Math, Tue 09:00-40
            └─ ...
            │
            ▼
Step 3: Format Response (200):
{
    "teacher_name": "Ratan",
    "timetable": [
        {
            "day": "Monday",
            "class_name": "10",
            "section": "A",
            "subject": "Math",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        ...
    ]
}
            │
            ▼
    Frontend Display
```

---

## Request/Response Examples

### Example 1: Admin Adding Math Class

REQUEST:
```
POST /api/timetable/add HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJ0eXAiOi...
Content-Type: application/json

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

RESPONSE (201 Created):
```
{
    "message": "Timetable entry added successfully",
    "id": 1
}
```

DATABASE:
```
timetable table gets new row:
id=1, class_name=10, section=A, subject=Math, teacher_name=Ratan, day=Monday, ...
```

---

### Example 2: Student John Views Timetable

REQUEST:
```
GET /api/timetable/student/1/week HTTP/1.1
Host: localhost:5000
Authorization: Bearer studentToken123...
```

RESPONSE (200 OK):
```
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
        ...
    ]
}
```

---

### Example 3: Teacher Ratan Views Schedule

REQUEST:
```
GET /api/timetable/teacher/1/week HTTP/1.1
Host: localhost:5000
Authorization: Bearer teacherToken456...
```

RESPONSE (200 OK):
```
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
            "id": 3,
            "day": "Monday",
            "class_name": "10",
            "section": "B",
            "subject": "Math",
            "start_time": "10:00",
            "end_time": "10:40"
        },
        ...
    ]
}
```

---

## Relationship Diagram

```
┌──────────────┐
│  STUDENTS    │
├──────────────┤
│ id (PK)      │
│ name         │
│ email        │
│ class_name   │◄─────┐
│ section      │      │
└──────────────┘      │
                      │
                  ┌───────────────────────┐
                  │    TIMETABLE (JOIN)   │
                  ├───────────────────────┤
                  │ class_name            │
                  │ section               │
                  │ subject               │
                  │ day                   │
                  │ start_time            │
                  │ end_time              │
                  └───────────────────────┘
                      │
                      └────────┬──────────┐
                               │          │
┌──────────────┐        ┌──────────────┐ │
│  TEACHERS    │        │   TEACHERS   │ │
├──────────────┤        ├──────────────┤ │
│ id (PK)      │        │ id (PK)      │ │
│ name         │◄───────│ name         │◄┘
│ email        │        │ email        │
│ subject      │        │ subject      │
└──────────────┘        └──────────────┘
```

---

## Day/Time Sorting Logic

```
Sorting Order:
1. First, sort by DAY (importance 1st)
   Monday (1)
   Tuesday (2)
   Wednesday (3)
   Thursday (4)
   Friday (5)
   Saturday (6)
   Sunday (7)

2. Then, sort by START_TIME (importance 2nd)
   09:00
   09:40
   10:20
   10:40
   14:00
   14:40
   15:20

Result:
Monday 09:00-09:40
Monday 09:40-10:20
Monday 10:20-11:00
Tuesday 09:00-09:40
Tuesday 09:40-10:20
...
```

---

## Status Summary

```
┌─────────────────────────────────────────────────────────────┐
│                   IMPLEMENTATION STATUS                     │
├─────────────────────────────────────────────────────────────┤
│ ✅ Fixed import path                                         │
│ ✅ Admin can add timetable entries                           │
│ ✅ Students can view their weekly schedule                   │
│ ✅ Teachers can view their teaching schedule                 │
│ ✅ All endpoints have error handling                         │
│ ✅ All endpoints require JWT authentication                  │
│ ✅ Results sorted by day and time                            │
│ ✅ Documentation complete                                    │
│ ✅ Test script provided                                      │
│ ✅ API examples provided                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND                                │
│  Admin Panel | Student Dashboard | Teacher Dashboard        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │ HTTP Requests (JSON)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FLASK BACKEND                             │
│  timetable.py (routes)                                      │
│  - add_timetable()                                          │
│  - get_student_timetable()                                  │
│  - get_teacher_timetable()                                  │
│  - get_timetable()                                          │
│  - delete_timetable_entry()                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │ SQL Queries
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLITE DATABASE                            │
│  timetable (table)                                          │
│  students (table)                                           │
│  teachers (table)                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
