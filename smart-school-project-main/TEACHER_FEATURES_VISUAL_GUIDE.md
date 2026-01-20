# Teacher Role-Based System - Visual Guide

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART SCHOOL SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
           ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
           │ Frontend │   │ Backend │  │ Database│
           │   (UI)   │   │ (Flask) │  │(SQLite) │
           └─────────┘   └────┬────┘  └────┬────┘
                              │            │
                   ┌──────────┼────────────┘
                   │          │
              ┌────▼────┐ ┌───▼─────┐
              │   JWT    │ │  SQLite │
              │   Auth   │ │ Database│
              └──────────┘ └────┬────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
            ┌────▼───┐     ┌────▼───┐   ┌────▼────┐
            │ Teachers│     │Students│   │Timetable│
            │  Table  │     │ Table  │   │ Table   │
            └────┬───┘     └────┬───┘   └────┬────┘
                 │              │            │
         ┌───────▼──────────────▼────────────▼─────┐
         │    Face Embeddings Table                │
         │  (role, person_id, embedding, ...)    │
         └─────────────────────────────────────────┘
```

---

## 👥 User Role Hierarchy

```
                     ┌─────────────────┐
                     │  SYSTEM ADMIN   │
                     │  (Unrestricted) │
                     └────────┬────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
           ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
           │  CLASS  │   │ REGULAR  │  │STUDENT  │
           │ TEACHER │   │ TEACHER  │  │         │
           └────┬────┘   └────┬────┘  └─────────┘
                │              │
        ┌───────▼──────┐  ┌────▼──────┐
        │ ✅ Can enroll│  │❌ Cannot  │
        │    students  │  │   enroll  │
        │ ✅ Can access│  │❌ Cannot  │
        │    class data│  │  access   │
        └──────────────┘  │   class   │
                          └───────────┘
```

---

## 📊 Teacher Type Comparison

```
╔════════════════════╦═════════════════╦════════════════════╗
║   Feature          ║  CLASS TEACHER  ║ REGULAR TEACHER    ║
╠════════════════════╬═════════════════╬════════════════════╣
║ Dashboard          ║ Full with class ║ Attendance only    ║
║ Enroll self        ║ ✅ YES          ║ ✅ YES             ║
║ Enroll student     ║ ✅ YES (own)    ║ ❌ NO              ║
║ Recognize self     ║ ✅ YES          ║ ✅ YES             ║
║ Recognize student  ║ ✅ YES (own)    ║ ❌ NO              ║
║ View student list  ║ ✅ YES (own)    ║ ❌ NO              ║
║ View class data    ║ ✅ YES (own)    ║ ❌ NO              ║
║ Mark attendance    ║ ✅ YES          ║ ✅ YES             ║
║ Manage class       ║ ✅ YES          ║ ❌ NO              ║
║ is_class_teacher   ║ 1               ║ 0                  ║
║ assigned_class     ║ "Class 10A"     ║ NULL               ║
║ assigned_section   ║ "Section A"     ║ NULL               ║
╚════════════════════╩═════════════════╩════════════════════╝
```

---

## 🔐 Authorization Decision Tree

### Face Enrollment Flow

```
                    ┌──────────────────────┐
                    │  POST /enrollment    │
                    │  enroll (with JWT)   │
                    └──────────┬───────────┘
                               │
                      ┌────────▼────────┐
                      │  Verify JWT     │
                      │  Extract role   │
                      └────────┬────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Check user role    │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
       ┌────▼────┐        ┌────▼────┐      ┌────▼─────┐
       │  ADMIN  │        │ TEACHER │      │  STUDENT │
       │    ✅   │        │         │      │    ❌    │
       └─────────┘        └────┬────┘      └──────────┘
                               │
                    ┌──────────▼─────────┐
                    │ Is class teacher?  │
                    └──────────┬─────────┘
                               │
                        ┌──────┴──────┐
                        │             │
                    ┌───▼──┐      ┌──▼────┐
                    │  YES │      │  NO   │
                    │  ✅  │      │  ❌   │
                    └──────┘      └───────┘
                        │
                    ┌───▼──────────────┐
                    │ Enrolling what?  │
                    └───┬─────────┬────┘
                        │         │
                    ┌───▼───┐ ┌──▼──────┐
                    │TEACHER│ │ STUDENT │
                    │  ✅   │ │    ?    │
                    └───────┘ └──┬──────┘
                                 │
                         ┌───────▼─────────┐
                         │ In my class?    │
                         └───┬─────────┬───┘
                             │         │
                         ┌───▼───┐ ┌──▼───┐
                         │  YES  │ │  NO  │
                         │  ✅   │ │  ❌  │
                         └───────┘ └──────┘
```

### Face Recognition Flow

```
                    ┌──────────────────────┐
                    │ POST /recognition    │
                    │ recognize (with JWT) │
                    └──────────┬───────────┘
                               │
                      ┌────────▼────────┐
                      │  Verify JWT     │
                      │  Extract role   │
                      └────────┬────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Find best match    │
                    │ in face_embeddings │
                    └────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │  Check role     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼────┐          ┌───▼─────┐         ┌───▼────┐
    │ ADMIN  │          │ TEACHER │         │ OTHER  │
    │  ✅    │          │   ?     │         │  ❌    │
    └────────┘          └───┬─────┘         └────────┘
                            │
                    ┌───────▼─────────┐
                    │ Recognized who? │
                    └───┬─────────┬───┘
                        │         │
                    ┌───▼───┐ ┌──▼──────┐
                    │TEACHER│ │ STUDENT │
                    │  ✅   │ │    ?    │
                    └───────┘ └──┬──────┘
                                 │
                         ┌───────▼─────────┐
                         │ In my class?    │
                         └───┬─────────┬───┘
                             │         │
                         ┌───▼───┐ ┌──▼───┐
                         │  YES  │ │  NO  │
                         │  ✅   │ │  ❌  │
                         └───────┘ └──────┘
```

---

## 🔄 Data Flow Examples

### Class Teacher Enrolling Student (Happy Path)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Class Teacher Logs In                                │
│    └─ Receives JWT token with role="teacher"            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 2. Teacher Views Dashboard                              │
│    └─ GET /api/teachers/<id>/dashboard                  │
│       └─ Returns: students, class timetable, personal   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 3. Teacher Selects Student to Enroll                    │
│    └─ GET /api/enrollment/student/<id>                  │
│       └─ Returns: name, email, class, section           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 4. Teacher Captures Face Image                          │
│    └─ Image captured from webcam                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 5. System Enrolls Face                                  │
│    └─ POST /api/enrollment/enroll                       │
│       ├─ Verify JWT: role="teacher", is_class_teacher=1│
│       ├─ Verify: student in teacher's class ✅         │
│       ├─ Generate face embedding                        │
│       ├─ Check for duplicates (threshold 0.6)          │
│       └─ Store in face_embeddings table                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 6. Response: Success                                    │
│    └─ 200 OK: {status: "success", person_id: 101}      │
└─────────────────────────────────────────────────────────┘
```

### Regular Teacher Trying to Enroll Student (Blocked)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Regular Teacher Logs In                              │
│    └─ Receives JWT token with role="teacher"            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 2. Teacher Views Attendance Interface                   │
│    └─ GET /api/teachers/<id>/attendance                 │
│       └─ Returns: attendance_only=true, can_enroll=false│
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 3. Teacher Captures Their Own Face (OK)                 │
│    └─ POST /api/enrollment/enroll                       │
│       ├─ Verify JWT: role="teacher" ✅                  │
│       ├─ Check: enrolling self? ✅                      │
│       ├─ Generate face embedding                        │
│       └─ Store successfully                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 4. Response: Success                                    │
│    └─ 200 OK: {status: "success", person_id: 2}        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 5. Teacher Tries to Enroll Student (BLOCKED)           │
│    └─ POST /api/enrollment/enroll                       │
│       ├─ Verify JWT: role="teacher" ✅                  │
│       ├─ Check: is_class_teacher? ❌                    │
│       └─ Return: 403 "Only class teachers can enroll"  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ 6. Response: Forbidden                                  │
│    └─ 403 Forbidden: {error: "Only class teachers..."}  │
└─────────────────────────────────────────────────────────┘
```

---

## 📡 API Response Examples

### ✅ Successful Class Teacher Dashboard

```json
{
  "teacher": {
    "id": 1,
    "name": "John Doe",
    "email": "john@school.com",
    "subject": "Mathematics",
    "assigned_class": "Class 10A",
    "assigned_section": "Section A"
  },
  "enrolled_students": [
    {
      "id": 101,
      "name": "Alice Johnson",
      "email": "alice@school.com",
      "class": "Class 10A",
      "section": "Section A"
    },
    {
      "id": 102,
      "name": "Bob Smith",
      "email": "bob@school.com",
      "class": "Class 10A",
      "section": "Section A"
    }
  ],
  "class_timetable": [
    {
      "day": "Monday",
      "start_time": "09:00",
      "end_time": "10:00",
      "subject": "Mathematics",
      "teacher_name": "John Doe"
    }
  ],
  "teacher_timetable": [
    {
      "day": "Monday",
      "start_time": "09:00",
      "end_time": "10:00",
      "subject": "Mathematics",
      "class": "Class 10A"
    }
  ]
}
```

### ❌ Regular Teacher Dashboard (Error)

```json
{
  "message": "Class teachers use /api/teachers/<id>/dashboard instead",
  "endpoint": "/api/teachers/<id>/dashboard"
}
Status: 400 Bad Request
```

### ❌ Face Enrollment - Unauthorized

```json
{
  "error": "Only class teachers can enroll students"
}
Status: 403 Forbidden
```

### ❌ Face Recognition - Outside Class

```json
{
  "error": "This student is not in your class"
}
Status: 403 Forbidden
```

---

## 🗂️ Database Schema Diagram

```
┌─────────────────────────────────────┐
│          USERS TABLE                │
├─────────────────────────────────────┤
│ id (PK)      | INTEGER              │
│ email (UQ)   | TEXT                 │
│ password     | TEXT                 │
│ role         | TEXT (teacher/admin) │
└─────────────────────────────────────┘
          ▲
          │ references by email
          │
┌─────────────────────────────────────┐
│        TEACHERS TABLE               │
├─────────────────────────────────────┤
│ id (PK)               | INTEGER     │
│ name                  | TEXT        │
│ email (FK)            | TEXT        │
│ id_code               | TEXT        │
│ subject               | TEXT        │
│                       │             │
│ [NEW FIELDS]          │             │
│ is_class_teacher      | INTEGER(0/1)│
│ assigned_class        | TEXT        │
│ assigned_section      | TEXT        │
└─────────────────────────────────────┘
          │
          ├─────────────┬──────────────────┐
          │             │                  │
          │ (class)     │ (section)        │
          ▼             ▼                  ▼
┌──────────────────────────────────────────┐
│         STUDENTS TABLE                   │
├──────────────────────────────────────────┤
│ id (PK)               | INTEGER          │
│ name                  | TEXT             │
│ email                 | TEXT             │
│ class_name            | TEXT             │
│ section               | TEXT             │
│ ...                   | ...              │
└──────────────────────────────────────────┘
          │
          │
          ▼
┌──────────────────────────────────────────┐
│      FACE_EMBEDDINGS TABLE               │
├──────────────────────────────────────────┤
│ id (PK)               | INTEGER          │
│ role                  | TEXT (student..)│
│ person_id             | INTEGER          │
│ embedding             | BLOB (128-D)    │
│ name                  | TEXT             │
│ email                 | TEXT             │
│ class_name            | TEXT (nullable)  │
│ section               | TEXT (nullable)  │
└──────────────────────────────────────────┘
```

---

## 🧪 Test Scenario Matrix

```
╔═══════════════════════╦═══════════════╦════════════════╦══════════╗
║ Scenario              ║ User Role     ║ Action         ║ Result   ║
╠═══════════════════════╬═══════════════╬════════════════╬══════════╣
║ Admin all-access      ║ ADMIN         ║ Any action     ║ ✅ OK    ║
║ Class teacher self    ║ CLASS TEACHER ║ Enroll self    ║ ✅ OK    ║
║ Class teacher student ║ CLASS TEACHER ║ Enroll student ║ ✅ OK    ║
║ Class teacher other   ║ CLASS TEACHER ║ Enroll other   ║ ❌ 403   ║
║ Regular teacher self  ║ REGULAR       ║ Enroll self    ║ ✅ OK    ║
║ Regular teacher std   ║ REGULAR       ║ Enroll student ║ ❌ 403   ║
║ Regular recognize self║ REGULAR       ║ Recognize self ║ ✅ OK    ║
║ Regular recognize std ║ REGULAR       ║ Recognize std  ║ ❌ 403   ║
║ Class dashboard       ║ CLASS TEACHER ║ Access         ║ ✅ OK    ║
║ Regular dashboard     ║ REGULAR       ║ Access         ║ ❌ 400   ║
║ Attendance interface  ║ REGULAR       ║ Access         ║ ✅ OK    ║
║ No auth               ║ NONE          ║ Any action     ║ ❌ 401   ║
╚═══════════════════════╩═══════════════╩════════════════╩══════════╝
```

---

## 📊 Feature Comparison Table

```
                  ADMIN    CLASS TEACHER    REGULAR TEACHER    STUDENT
─────────────────────────────────────────────────────────────────────────
Full Dashboard     ✅          ✅               ❌                ❌
Student List       ✅          ✅ (own)        ❌                ❌
Class Timetable    ✅          ✅ (own)        ❌                ❌
Enroll Student     ✅          ✅ (own)        ❌                ❌
Recognize Student  ✅          ✅ (own)        ❌                ❌
Edit Enrollment    ✅ (any)    ✅ (own/class) ✅ (self)         ✅ (self)
Mark Attendance    ✅          ✅              ✅                ✅
Personal Timetable ✅          ✅              ✅                ✅
Attendance Only    N/A         N/A             ✅                N/A
is_class_teacher   N/A         1               0                 N/A
```

---

## 🎯 Success Metrics

```
✅ All 5 Requirements Implemented
   ├─ Class teacher selection during enrollment
   ├─ Face recognition restricted by role
   ├─ Class teacher gets student list
   ├─ Class teacher dashboard with timetables
   ├─ Regular teacher attendance only
   └─ Enrollment edit with form pre-population

✅ 6 New Endpoints Added
   ├─ GET /api/teachers/<id>/dashboard
   ├─ GET /api/teachers/<id>/enrolled-students
   ├─ GET /api/teachers/<id>/attendance
   ├─ GET /api/enrollment/<role>/<id>
   ├─ PUT /api/enrollment/<role>/<id>
   └─ PUT /api/teachers/<id> (enhanced)

✅ Authorization Fully Implemented
   ├─ JWT authentication on all endpoints
   ├─ Role-based access control
   ├─ Class membership verification
   ├─ Consistent error responses
   └─ Proper HTTP status codes

✅ Code Quality
   ├─ No syntax errors
   ├─ SQL injection prevention
   ├─ Clear error messages
   ├─ Backward compatible
   └─ Auto-migration ready

✅ Documentation Complete
   ├─ 4 comprehensive guides
   ├─ 1 test script with 16 scenarios
   ├─ API examples provided
   └─ Frontend specifications included
```

---

## 🚀 Deployment Overview

```
┌──────────────────────────────────────────────────────────┐
│ PRE-DEPLOYMENT CHECKLIST                                 │
├──────────────────────────────────────────────────────────┤
│ ✅ Code reviewed and approved                            │
│ ✅ Syntax validation passed                              │
│ ✅ Authorization logic verified                          │
│ ✅ Documentation complete                                │
│ ✅ Test script provided                                  │
│ ✅ Backward compatibility ensured                        │
│ ✅ Database migration ready (auto)                       │
│ ✅ Rollback plan prepared                                │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│ DEPLOYMENT STEPS                                         │
├──────────────────────────────────────────────────────────┤
│ 1. Backup production database                            │
│ 2. Deploy code to staging                                │
│ 3. Run smoke tests                                       │
│ 4. Deploy to production                                  │
│ 5. Verify auto-migration completed                       │
│ 6. Monitor logs for errors                               │
│ 7. Run test suite                                        │
│ 8. Get user feedback                                     │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│ POST-DEPLOYMENT MONITORING                               │
├──────────────────────────────────────────────────────────┤
│ ✅ API response times                                    │
│ ✅ Authorization success rates                           │
│ ✅ Face recognition accuracy                             │
│ ✅ Database performance                                  │
│ ✅ Error rates                                           │
│ ✅ User feedback                                         │
└──────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0  
**Status:** ✅ COMPLETE - Ready for Production  
**Created:** [TODAY]

