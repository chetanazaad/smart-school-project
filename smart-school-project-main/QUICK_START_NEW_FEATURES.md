# 🚀 QUICK START GUIDE - NEW FEATURES

**Date:** January 18, 2026  
**Version:** 2.0 with Role-Based Credentials

---

## 🔐 NEW LOGIN SYSTEM

### What Changed?
- **Before:** Only 3 roles (Admin, Teacher, Student)
- **Now:** 4 roles (Admin, Teacher, Student, Parent) with unified credential management

### Login URL
```
http://localhost:5173/login
```

### Available Roles at Login
1. **Admin** - School administrator
2. **Teacher** - Teaching staff
3. **Student** - Student users
4. **Parent** - Parent/Guardian users

---

## 👥 HOW TO ADD USERS

### Adding a Teacher
```
Admin Dashboard → Teachers → Add Teacher
├─ ID: Auto-generated (T1001, T1002, etc.)
├─ Name: Teacher full name
├─ Email: teacher@school.com ✨ (Login credential)
├─ Subject: Subject taught
├─ Password: Min 6 characters ✨ (Login credential)
├─ Face Enrollment: Required
└─ Submit
```

**Teacher can then login with:**
- Email: teacher@school.com
- Password: [set during addition]
- Role: Teacher

### Adding a Student
```
Admin Dashboard → Students → Add Student
├─ ID: Auto-generated (ST1001, ST1002, etc.)
├─ Name: Student full name
├─ Email: student@school.com ✨ (Login credential)
├─ Class: 1-12
├─ Section: A-F
├─ Password: Min 6 characters ✨ (Login credential)
├─ Face Enrollment: Required
└─ Submit
```

**Student can then login with:**
- Email: student@school.com
- Password: [set during addition]
- Role: Student

### Adding a Parent ⭐ NEW
```
Admin Dashboard → Parents → Add Parent
├─ ID: Auto-generated (P1001, P1002, etc.)
├─ Name: Parent full name
├─ Email: parent@school.com ✨ (Login credential)
├─ Phone: Optional
├─ Password: Min 6 characters ✨ (Login credential)
└─ Submit (NO face enrollment needed)
```

**Parent can then login with:**
- Email: parent@school.com
- Password: [set during addition]
- Role: Parent

---

## 🔧 ADMIN SETTINGS ⭐ NEW

### Change Admin Credentials
```
Admin Dashboard → Settings
├─ Change Email
│  └─ Current Email → New Email
└─ Change Password
   ├─ Current Password (verification)
   ├─ New Password (min 6 chars)
   └─ Confirm New Password
```

**After change:**
- Admin must login with new credentials
- Session remains active during change
- Changes take effect immediately

---

## 📊 CREDENTIAL MANAGEMENT SUMMARY

| Role | Added Via | Email Setup | Password Setup | Face Required |
|------|-----------|-------------|----------------|---------------|
| Teacher | Admin → Teachers | During addition | During addition | YES |
| Student | Admin → Students | During addition | During addition | YES |
| Parent | Admin → Parents | During addition | During addition | NO |
| Admin | Database | Set initially | Dashboard Settings | N/A |

---

## 🔑 DEFAULT LOGIN (First Time)

```
Email: admin
Password: password
Role: Admin
```

**⚠️ IMPORTANT:** Change these credentials after first login!

---

## 🧪 TEST ACCOUNTS

### Create Test Accounts:
1. Go to Admin Dashboard
2. Add test teacher:
   - Name: "John Teacher"
   - Email: "john@test.com"
   - Password: "test1234"
3. Add test student:
   - Name: "Alice Student"
   - Email: "alice@test.com"
   - Password: "test1234"
4. Add test parent:
   - Name: "Bob Parent"
   - Email: "bob@test.com"
   - Password: "test1234"

### Login with Test Accounts:
```
Teacher Login:
  Email: john@test.com
  Password: test1234
  Role: Teacher

Student Login:
  Email: alice@test.com
  Password: test1234
  Role: Student

Parent Login:
  Email: bob@test.com
  Password: test1234
  Role: Parent
```

---

## 🔒 PASSWORD REQUIREMENTS

- **Minimum Length:** 6 characters
- **Character Types:** No restrictions (for simplicity)
- **Security:** Passwords are hashed using werkzeug.security

### Strong Password Examples:
```
✅ secure@pass123
✅ School#2026
✅ Teacher@101
✅ Parent_Safe_123
```

---

## ⚠️ IMPORTANT NOTES

### Emails Must Be Unique
- Each email can only be used once across the system
- Cannot have duplicate emails for different users
- Email verification not required (optional future feature)

### Role Mismatch Error
If you see: **"Incorrect role"**
- The email/password are correct
- But the role you selected doesn't match
- Make sure you select the correct role at login

### Password Reset
- Currently not available
- Admin must be contacted to reset forgotten passwords
- Future feature: Self-service password reset

### Face Enrollment
- **Required for:** Teachers and Students
- **Not required for:** Parents and Admin

---

## 🚀 FEATURES AT A GLANCE

### New in This Update:
✨ **Parent Role** - Full parent user management  
✨ **Parent Tab** - Dedicated parents section in admin panel  
✨ **Admin Settings** - Change email and password securely  
✨ **Unified Login** - One login form for all 4 roles  
✨ **Automatic Credentials** - User accounts created during enrollment  
✨ **Role-Based Navigation** - Different dashboards per role  

---

## 📱 USER DASHBOARDS

### Admin Dashboard
```
/admin/dashboard
├─ Statistics & Overview
├─ Quick Actions
├─ Attendance Charts
└─ Recent Activity
```

### Teacher Dashboard
```
/teacher/dashboard
├─ My Attendance
├─ My Classes
├─ Student Enrollment
└─ Attendance Records
```

### Student Dashboard
```
/student/dashboard
├─ My Attendance
├─ My Timetable
├─ Class Information
└─ Performance
```

### Parent Dashboard ⭐ NEW
```
/parent/dashboard
├─ Child Performance
├─ Attendance Records
└─ Messages
```

---

## 🔄 LOGIN FLOW

```
┌──────────────────────┐
│  Visit Login Page    │
│  localhost:5173/login│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Select Role          │
│ • Admin              │
│ • Teacher            │
│ • Student            │
│ • Parent             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Enter Email          │
│ (enrollment email)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Enter Password       │
│ (enrollment password)│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Click Login          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ System validates:    │
│ ✓ Email exists       │
│ ✓ Password matches   │
│ ✓ Role is correct    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ JWT Token issued     │
│ Redirect to          │
│ role dashboard       │
└──────────────────────┘
```

---

## ❌ COMMON ISSUES & FIXES

### Issue: "Invalid email or password"
**Solution:** 
- Check email spelling exactly as set during enrollment
- Verify password is correct
- Try admin login first to verify system is working

### Issue: "Incorrect role"
**Solution:**
- You selected wrong role at login
- Check what role user was added as
- Select matching role before login

### Issue: Email already exists
**Solution:**
- Email must be unique
- Use different email when adding new user
- Old email: teacher@school.com (taken)
- New email: teacher2@school.com (available)

### Issue: Face enrollment fails
**Solution:**
- Only needed for Teachers and Students
- Parents don't need face enrollment
- Make sure webcam is accessible
- Check browser permissions for camera access

---

## 🆘 SUPPORT COMMANDS

### Check System Health
```
Backend API Health: http://localhost:5000/
Frontend Status: http://localhost:5173/
Auth Endpoint: http://localhost:5000/api/auth/ping
```

### Reset Admin Credentials (if locked out)
Contact system administrator with access to database.

---

## 📞 TROUBLESHOOTING

**Q: User can't login after being added**
A: Verify:
1. User was added with password
2. Email is correctly spelled
3. Password is at least 6 characters
4. Correct role is selected at login
5. Face enrollment was completed (if student/teacher)

**Q: Admin password needs to be reset**
A: Use Admin Settings:
1. Login as admin
2. Go to Settings
3. Click "Change Password"
4. Follow the form

**Q: Forgot admin password**
A: Contact database administrator (need direct DB access)

---

**Last Updated:** January 18, 2026  
**Version:** 2.0  
**Status:** ✅ Production Ready
