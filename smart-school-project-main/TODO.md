# Smart School Project - TODO List

## Completed
[x] 9. Remove debug logs from frontend. (Console logs removed from api.js.)
[x] 10. Add error handling to frontend. (Basic error handling added to api.js.)
[x] 11. Consolidate documentation index. (Documentation index consolidated; see DOCUMENTATION_INDEX.md.)
[x] 12. Remove redundant markdown files. (Redundant markdown files removed from project root.)
[x] 8. Move API config to env vars. (API baseURL now uses env variable VITE_API_BASE_URL.)
[x] 7. Verify frontend teacher attendance. (TeacherAttendancePage fetches and displays teacher attendance records correctly.)
[x] 6. Add error handling to API. (Global error handler added for consistent API error responses.)
[x] 5. Implement DB migration system. (Flask-Migrate integrated for database migrations.)
[x] 4. Use PostgreSQL for production. (PostgreSQL supported via env variables; falls back to SQLite if not set.)
[x] 3. Implement rate limiting on API endpoints. (Flask-Limiter added with default limit from env variable RATE_LIMIT.)
[x] 2. Configure CORS for production domains. (CORS config now uses env variable `CORS_ALLOWED_ORIGINS` for production domains.)

[x] 1. encoder.py - Variable name bug fixed (image_bytes = base64.b64decode(image_base64))
[x] 2. encoder.py - Debug image saving now opt-in via SAVE_DEBUG_IMAGES env var
[x] 3. app.py - Duplicate error handler removed
[x] 4. app.py - Generic exception handler now returns safe messages (no stack traces exposed)
[x] 5. api.js - Alert spam removed; errors now rejected for component handling
[x] 9. api.js - Empty else blocks removed from interceptor
[x] 10. app.py - Error handler now uses proper logging instead of print()

[x] 6. jwt_manager.py - JWT secret now requires env var, fails gracefully if not set
[x] 7. auth.py - Print statements replaced with proper logging (no email exposure)
[x] 8. encoder.py - Print statements replaced with proper logging
[x] 11. tests/fix_admin_password.py - Credentials now use environment variables

[x] 12. routes/recognition.py - Excessive print statements removed (50+ print statements replaced with logging)
[x] 13. routes/teachers.py - Print statements replaced with proper logging
[x] 14. routes/students.py - Print statements replaced with proper logging  
[x] 15. routes/attendance_view.py - Print/traceback statements replaced with proper logging
[x] 16. realtime_attendance_old.py - Print statements replaced with proper logging

[x] 18. api.js - Added 30 second timeout to axios requests (timeout: 30000)
[x] 20. auth.py - Added stricter rate limiting for login endpoint (5 per minute)
[x] 21. Error messages - Improved error messages in multiple routes
[x] 23. Logging - Inconsistent logging levels standardized (remaining files fixed):
  - routes/parents.py - Print statements replaced with proper logging
  - routes/enrollment.py - Print statements replaced with proper logging
  - routes/automatic_attendance.py - Print statements replaced with proper logging
  - routes/face.py - Print statements replaced with proper logging
  - routes/realtime_attendance.py - Print statements replaced with proper logging
  - routes/realtime_attendance_old.py - Print statements replaced with proper logging

[x] 17. Test files - Files already organized in tests/ directory
[x] 25. Password requirements - Implemented password strength validation (min 8 chars, uppercase, lowercase, digit, special char)
[x] 26. Session management - JWT token blacklist implemented for logout functionality (see utils/jwt_blacklist.py)
[x] 30. Backend - Request ID tracking implemented for log tracing (see utils/request_id.py)
[x] 19. Frontend - Loading states added to TeacherDashboard and other pages
[x] 24. CORS - Already uses environment variable for production domains (CORS_ALLOWED_ORIGINS)

[x] 27. API versioning - IMPLEMENTED - All routes now use /api/v1/ prefix
[x] 28. Database indexes - IMPLEMENTED - All frequently queried columns have indexes:
  - users (email, role)
  - students (class_name, id_code)
  - timetable (class_section, teacher_day, day_time)
  - face_embeddings (role_student, role_teacher)
  - teacher_attendance (teacher_date)

[x] 29. Frontend - Bundle size - PARTIAL - Using Vite for optimized builds (code splitting available via dynamic imports)

[x] 31. Bug fix - Teacher/Student deletion not working - FIXED: 
  - Fixed delete_teacher() in routes/teachers.py - was using wrong column name 'person_id' instead of 'teacher_id'
  - Now properly deletes from face_embeddings table when teacher is deleted

## NEW - Face Recognition Attendance Issues

[x] 32. FIX: Database fresh=True issue causing data loss - FIXED:
  - Changed init_db(fresh=True) to init_db(fresh=False) in app.py
  - This prevents database from being deleted on every server restart
  - Students, teachers, attendance records, and face embeddings are now preserved

[x] 33. FIX: Student attendance schema mismatch - FIXED:
  - The student_attendance table requires class_name (NOT NULL)
  - Updated automatic_attendance.py to fetch and include class_name when inserting attendance
  - Now properly gets student.class_name from database and includes it in INSERT

[x] 34. FIX: Teacher attendance marking - VERIFIED:
  - Teacher attendance route verified working in automatic_attendance.py
  - Properly inserts into teacher_attendance table with teacher_id, date, status, marked_at

## Remaining (Future Enhancements)

- **Advanced code splitting** - Could benefit from React.lazy() for route-based splitting
- **PostgreSQL production** - Ready for production deployment with external database
