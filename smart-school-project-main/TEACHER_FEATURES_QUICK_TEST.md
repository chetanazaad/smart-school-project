# Teacher Features - Quick Start Testing Guide

**Last Updated**: January 19, 2026

Quick reference for testing all teacher features.

---

## 1. Create Teachers

### Create a Class Teacher
```bash
curl -X POST http://localhost:5000/api/teachers \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@school.com",
    "id_code": "T001",
    "subject": "English",
    "password": "pass123",
    "is_class_teacher": true,
    "assigned_class": "Class 10",
    "assigned_section": "A"
  }'
```

### Create a Regular Teacher
```bash
curl -X POST http://localhost:5000/api/teachers \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@school.com",
    "id_code": "T002",
    "subject": "Mathematics",
    "password": "pass123",
    "is_class_teacher": false
  }'
```

---

## 2. Test Class Teacher Features

### Get Class Teacher Dashboard
```bash
curl -X GET http://localhost:5000/api/teachers/1/dashboard \
  -H "Authorization: Bearer {jane_token}"
```

**Expected**: Returns teacher info, enrolled students, class timetable, personal timetable

### Get Enrolled Students
```bash
curl -X GET http://localhost:5000/api/teachers/1/enrolled-students \
  -H "Authorization: Bearer {jane_token}"
```

**Expected**: List of students in Class 10, Section A

### Enroll Student Face (Class Teacher)
```bash
curl -X POST http://localhost:5000/api/face/enroll \
  -H "Authorization: Bearer {jane_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_image_data",
    "user_id": 1,
    "role": "student",
    "current_teacher_id": 1
  }'
```

**Expected**: Success - "Face enrolled successfully"

---

## 3. Test Regular Teacher Features

### Get Attendance Interface
```bash
curl -X GET http://localhost:5000/api/teachers/2/attendance \
  -H "Authorization: Bearer {john_token}"
```

**Expected**: 
```json
{
  "id": 2,
  "name": "John Doe",
  "attendance_only": true,
  "can_enroll": false
}
```

### Try Enrollment (Should Fail)
```bash
curl -X POST http://localhost:5000/api/face/enroll \
  -H "Authorization: Bearer {john_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_image_data",
    "user_id": 1,
    "role": "student",
    "current_teacher_id": 2
  }'
```

**Expected Error**: "Only class teachers can enroll students"

---

## 4. Test Authorization

### Class Teacher Dashboard - Regular Teacher (Should Fail)
```bash
curl -X GET http://localhost:5000/api/teachers/2/dashboard \
  -H "Authorization: Bearer {john_token}"
```

**Expected Error**: "Only class teachers can access this dashboard"

### Attendance Interface - Class Teacher (Should Fail)
```bash
curl -X GET http://localhost:5000/api/teachers/1/attendance \
  -H "Authorization: Bearer {jane_token}"
```

**Expected Error**: "Class teachers use /api/teachers/<id>/dashboard instead"

---

## 5. Test Face Recognition

### Recognize Face (Regular Teacher)
```bash
curl -X POST http://localhost:5000/api/face/recognize \
  -H "Authorization: Bearer {john_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "base64_image_data"
  }'
```

**Expected**: Can only recognize themselves (if face is John's)

### Recognize Student (Class Teacher)
```bash
curl -X POST http://localhost:5000/api/face/recognize \
  -H "Authorization: Bearer {jane_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "base64_student_face"
  }'
```

**Expected**: Can recognize students in their class (Class 10, Section A)

---

## 6. Test Updates

### Change Regular Teacher to Class Teacher
```bash
curl -X PUT http://localhost:5000/api/teachers/2 \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "is_class_teacher": true,
    "assigned_class": "Class 11",
    "assigned_section": "B"
  }'
```

**Expected**: "Teacher updated"

### Update Teacher Without Class (Make Regular Again)
```bash
curl -X PUT http://localhost:5000/api/teachers/1 \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "is_class_teacher": false,
    "assigned_class": null,
    "assigned_section": null
  }'
```

**Expected**: "Teacher updated"

---

## 7. Mark Teacher Attendance

```bash
curl -X POST http://localhost:5000/api/teacher-attendance/mark \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_id": 1,
    "status": "present"
  }'
```

**Expected**: "Attendance marked successfully"

---

## Test Results Template

| Feature | Status | Notes |
|---------|--------|-------|
| Create Class Teacher | ⏳ | |
| Create Regular Teacher | ⏳ | |
| Class Teacher Dashboard | ⏳ | |
| Get Enrolled Students | ⏳ | |
| Enroll Student Face | ⏳ | |
| Regular Teacher Attendance | ⏳ | |
| Regular Teacher Cannot Enroll | ⏳ | |
| Face Recognition Authorization | ⏳ | |
| Update Teacher Type | ⏳ | |
| Mark Attendance | ⏳ | |

---

## Common Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Face recognized, attendance marked |
| 201 | Created | Teacher created successfully |
| 400 | Bad Request | Missing required fields |
| 403 | Forbidden | Not authorized for this action |
| 404 | Not Found | Teacher not found |
| 409 | Conflict | Face already enrolled |
| 500 | Server Error | Database issue |

---

## Troubleshooting

### Issue: "Unauthorized" Error
**Solution**: Check that JWT token is valid and included in Authorization header

### Issue: "Only class teachers can access"
**Solution**: Make sure you're using class teacher's token and that `is_class_teacher=true` in database

### Issue: Face not recognized
**Solution**: Check that face was enrolled first, and user has authorization to recognize it

### Issue: "This face is already enrolled"
**Solution**: Each person can only be enrolled once. Delete old record or use different image

---

## Database Verification

Check current teacher status:
```bash
python
>>> import sqlite3
>>> conn = sqlite3.connect('smart_school_backend/database/smart_school.db')
>>> cur = conn.cursor()
>>> cur.execute("SELECT id, name, is_class_teacher, assigned_class, assigned_section FROM teachers")
>>> for row in cur.fetchall():
...     print(row)
```

---

## Quick Reference URLs

| Feature | URL |
|---------|-----|
| Teacher List | `GET /api/teachers` |
| Create Teacher | `POST /api/teachers` |
| Get Teacher | `GET /api/teachers/{id}` |
| Update Teacher | `PUT /api/teachers/{id}` |
| Class Dashboard | `GET /api/teachers/{id}/dashboard` |
| Enrolled Students | `GET /api/teachers/{id}/enrolled-students` |
| Attendance Interface | `GET /api/teachers/{id}/attendance` |
| Enroll Face | `POST /api/face/enroll` |
| Recognize Face | `POST /api/face/recognize` |
| Mark Attendance | `POST /api/teacher-attendance/mark` |

---

## Notes

- All endpoints require JWT authentication (`@jwt_required()`)
- Admin can access all features
- Class teachers can only see their own data
- Regular teachers have limited access
- Database must have fresh schema with new teacher fields
- Use `database/setup_database.py` to recreate database

