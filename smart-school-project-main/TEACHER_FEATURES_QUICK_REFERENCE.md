# Teacher Role-Based Features - Quick Reference

## What Changed?

### Database Schema
Added 3 new columns to `teachers` table:
- `is_class_teacher` (INT): 0 = regular, 1 = class teacher
- `assigned_class` (TEXT): e.g., "Class 10A"
- `assigned_section` (TEXT): e.g., "Section A"

### New Endpoints Added

#### Teacher Management
- `PUT /api/teachers/<id>/` → Update teacher (including role change)
- `GET /api/teachers/<id>/dashboard` → Class teacher dashboard with students + timetables
- `GET /api/teachers/<id>/enrolled-students` → List of class students
- `GET /api/teachers/<id>/attendance` → Regular teacher attendance interface

#### Enrollment Management
- `GET /api/enrollment/<role>/<id>` → Get enrollment details (for editing)
- `PUT /api/enrollment/<role>/<id>` → Update enrollment details

### Authorization Updates

#### Face Enrollment (`POST /api/enrollment/enroll`)
- **Admin:** Can enroll anyone ✅
- **Class Teacher:** Can enroll themselves + their class students ✅
- **Regular Teacher:** Cannot enroll (403) ❌
- **Others:** Unauthorized ❌

#### Face Recognition (`POST /api/recognition/recognize`)
- **Admin:** Can recognize anyone ✅
- **Class Teacher:** Can recognize themselves + their class students ✅
- **Regular Teacher:** Can only recognize themselves ✅
- **Others:** Unauthorized ❌

---

## Usage Examples

### 1. Create Class Teacher
```bash
curl -X POST http://localhost:5000/api/teachers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "name": "John Doe",
    "email": "john@school.com",
    "id_code": "T001",
    "subject": "Math",
    "is_class_teacher": true,
    "assigned_class": "Class 10A",
    "assigned_section": "Section A"
  }'
```

### 2. Get Class Teacher Dashboard
```bash
curl http://localhost:5000/api/teachers/1/dashboard \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Returns: Teacher info + enrolled students + class timetable + personal timetable

### 3. Get Regular Teacher Attendance Interface
```bash
curl http://localhost:5000/api/teachers/2/attendance \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Returns: Teacher info with `attendance_only: true` and `can_enroll: false`

### 4. Enroll Face (Class Teacher enrolling student)
```bash
curl -X POST http://localhost:5000/api/enrollment/enroll \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <CLASS_TEACHER_TOKEN>" \
  -d '{
    "image": "base64_image_data",
    "user_id": 101,
    "role": "student"
  }'
```

### 5. Recognize Face
```bash
curl -X POST http://localhost:5000/api/recognition/recognize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "image_base64": "base64_image_data"
  }'
```

Returns different results based on current user's role and class assignment.

---

## Frontend Checklist

### Class Teacher Dashboard
- [ ] Display teacher info with class assignment
- [ ] Show list of enrolled students
- [ ] Show "Enroll Face" button (self + students)
- [ ] Show class timetable
- [ ] Show personal timetable
- [ ] Show "Edit Enrollment" links
- [ ] Show "Mark Attendance" option

### Regular Teacher Dashboard
- [ ] Display teacher info (no class assignment)
- [ ] Show personal timetable only
- [ ] Show "Enroll Face" button (self only)
- [ ] Hide student list
- [ ] Hide class timetable
- [ ] Show "Mark Attendance" interface
- [ ] Show "Edit Enrollment" link (self only)

### Enrollment Form
- [ ] Pre-fill all current details
- [ ] Allow edit of: name, email, id_code, subject
- [ ] Make fields non-editable: is_class_teacher, assigned_class, assigned_section
- [ ] Submit to `PUT /api/enrollment/<role>/<id>`
- [ ] Show validation errors

---

## Testing Commands

### Test Class Teacher Creation
```bash
# Create class teacher
curl -X POST http://localhost:5000/api/teachers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Test Teacher",
    "email": "test.teacher@school.com",
    "id_code": "T999",
    "subject": "Math",
    "is_class_teacher": 1,
    "assigned_class": "Class 10A",
    "assigned_section": "Section A"
  }'
```

### Test Dashboard Access
```bash
# Verify class teacher can access dashboard
curl http://localhost:5000/api/teachers/1/dashboard \
  -H "Authorization: Bearer $CLASS_TEACHER_TOKEN"

# Verify regular teacher gets error
curl http://localhost:5000/api/teachers/2/dashboard \
  -H "Authorization: Bearer $REGULAR_TEACHER_TOKEN"
```

### Test Face Enrollment Authorization
```bash
# Class teacher enrolling student (should work)
curl -X POST http://localhost:5000/api/enrollment/enroll \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CLASS_TEACHER_TOKEN" \
  -d '{
    "image": "base64...",
    "user_id": 101,
    "role": "student"
  }'

# Regular teacher enrolling student (should fail with 403)
curl -X POST http://localhost:5000/api/enrollment/enroll \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $REGULAR_TEACHER_TOKEN" \
  -d '{
    "image": "base64...",
    "user_id": 101,
    "role": "student"
  }'
```

---

## Key Implementation Details

### Authorization Pattern
All endpoints follow this pattern:
```python
@jwt_required()
def endpoint():
    # 1. Get current user from JWT
    current_identity = get_jwt_identity()
    
    # 2. Look up their role from users table
    cur.execute("SELECT role FROM users WHERE email = ?", (current_identity,))
    user_role = cur.fetchone()["role"]
    
    # 3. Check authorization
    if user_role == "admin":
        # Unrestricted
    elif user_role == "teacher":
        # Check class teacher status
        cur.execute("SELECT is_class_teacher, assigned_class, assigned_section FROM teachers")
        # Verify access
    else:
        # Forbidden
        return 403
```

### Class Filtering
When checking if student belongs to teacher's class:
```python
cur.execute("""
    SELECT id FROM students 
    WHERE id = ? AND class_name = ? AND section = ?
""", (student_id, teacher.assigned_class, teacher.assigned_section))
```

### Database Auto-Migration
No manual migration needed. The `teacher.py` model automatically adds missing columns:
```python
# In smart_school_backend/models/teacher.py
# ALTER TABLE triggers automatically on app startup
```

---

## Files Modified

1. **models/teacher.py**
   - Added schema with new columns
   - Added auto-migration logic

2. **routes/teachers.py**
   - Updated GET/POST/PUT endpoints with new fields
   - Added `/api/teachers/<id>/dashboard` endpoint
   - Added `/api/teachers/<id>/enrolled-students` endpoint
   - Added `/api/teachers/<id>/attendance` endpoint

3. **routes/enrollment.py**
   - Added @jwt_required() to `/enroll` endpoint
   - Added role-based authorization checks
   - Added GET `/api/enrollment/<role>/<id>` endpoint
   - Added PUT `/api/enrollment/<role>/<id>` endpoint
   - Added sqlite3 import for IntegrityError handling

4. **routes/recognition.py**
   - Added @jwt_required() to `/recognize` endpoint
   - Added role-based authorization checks
   - Class teachers can only recognize own class students
   - Regular teachers can only recognize themselves

---

## Error Response Format

All endpoints return consistent error responses:

```json
{
  "error": "Error message describing what went wrong"
}
```

HTTP Status Codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (no token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate email, etc.)
- `500` - Server Error

---

## Next Steps for Frontend

1. Create separate UI components for class teacher vs regular teacher
2. Add conditional rendering based on `is_class_teacher` flag
3. Implement enrollment edit form with GET → PUT flow
4. Add face enrollment UI with role-based visibility
5. Integrate face recognition with authorization checks
6. Add proper error handling and user feedback

---

## Configuration Notes

- All endpoints except `/enroll` and `/recognize` are GET/PUT (stateless)
- All endpoints except health/status require JWT authentication
- All database queries use parameterized statements (SQL injection safe)
- No additional environment variables needed

---

## Support

For issues or questions:
1. Check `TEACHER_ROLE_FEATURES.md` for detailed API documentation
2. Review error responses and HTTP status codes
3. Verify JWT token is valid and user has correct role
4. Check database migrations ran successfully (no ALTER TABLE errors)
