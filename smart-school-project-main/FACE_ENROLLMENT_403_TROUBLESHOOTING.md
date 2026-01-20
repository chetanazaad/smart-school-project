# Face Enrollment 403 Troubleshooting Guide

## The Problem
```
POST /api/face/enroll HTTP/1.1" 403
```

The face enrollment endpoint is returning 403 (Forbidden), meaning authorization is failing.

## Root Causes (In Priority Order)

### Cause 1: Admin User Not in Database ⚠️ MOST LIKELY
**Symptom:** `[FACE ENROLL] Role: None` in logs

**Why it happens:**
- Admin logged in but their email is not in the users table
- The authorization check tries to look up `SELECT role FROM users WHERE email = ?`
- If not found, `current_user_role` becomes `None`
- `None` doesn't match "admin", "teacher", or anything → Authorization fails

**How to check:**
```bash
# From backend directory:
python -c "
import sqlite3
db = sqlite3.connect('database/smart_school.db')
db.row_factory = sqlite3.Row
cur = db.cursor()

# 1. Check if admin exists
print('=== Users Table ===')
cur.execute('SELECT id, email, role FROM users')
for row in cur.fetchall():
    print(f'  ID: {row[\"id\"]}, Email: {row[\"email\"]}, Role: {row[\"role\"]}')

# 2. Check what the JWT token claims
print()
print('Note: Check browser DevTools to see what email the JWT token contains')
"
```

**Fix if admin not found:**
```bash
python -c "
import sqlite3
from smart_school_backend.models.user import create_user

# Create admin user
create_user(name='Admin', email='admin@school.com', password='Admin123', role='admin')
print('Admin user created')
"
```

### Cause 2: JWT Token Invalid or Expired
**Symptom:** `[FACE ENROLL] JWT Identity: None` in logs

**Why it happens:**
- `get_jwt_identity()` returns None
- Token is invalid, expired, or malformed
- Authorization header not properly sent

**How to check:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Look for POST /api/face/enroll request
4. Check "Request Headers" section
5. Look for: `Authorization: Bearer eyJ...` 
6. If missing or malformed → Token issue

**Fix:**
- Log out and log in again
- Clear browser cache and local storage
- Check if JWT secret matches between frontend and backend

### Cause 3: Database Connection Error
**Symptom:** `[FACE ENROLL] Error getting user role: ...` with exception details

**Why it happens:**
- Database is locked or unavailable
- SQL query syntax error
- Database file corrupted

**How to check:**
1. Verify database file exists: `database/smart_school.db`
2. Test database connection:
```bash
python -c "
import sqlite3
try:
    db = sqlite3.connect('database/smart_school.db')
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    print(f'Database OK - Users count: {cur.fetchone()[0]}')
except Exception as e:
    print(f'Database error: {e}')
"
```

### Cause 4: Multiple Authentication Issues
**Symptom:** Everything seems right but still 403

**How to debug:**
1. Add more logging temporarily to enrollment.py
2. Check if the problem is in JWT validation itself
3. Test with curl from terminal:

```bash
# Get a token first
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@school.com","password":"Admin123"}'

# Response: {"access_token": "eyJ..."}

# Then try face enroll with token
curl -X POST http://127.0.0.1:5000/api/face/enroll \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"image":"base64image","user_id":1,"role":"teacher"}'
```

## Step-by-Step Diagnostic

### Step 1: Check Backend Logs
When attempting to create a teacher with face enrollment, watch the terminal where Flask is running.

**Look for:**
```
[FACE ENROLL] JWT Identity: ???, Role: ???
```

**What each message means:**

| Message | Meaning |
|---------|---------|
| `JWT Identity: admin@school.com, Role: admin` | ✅ GOOD - Admin authorized |
| `JWT Identity: admin@school.com, Role: None` | ⚠️ Email not in users table |
| `JWT Identity: None, Role: None` | ⚠️ JWT token invalid |
| `Error getting user role: [error]` | ⚠️ Database error |
| `Unauthorized - Role: None` | ❌ Authorization failed |

### Step 2: Check Users Table
```bash
python -c "
import sqlite3
db = sqlite3.connect('database/smart_school.db')
db.row_factory = sqlite3.Row
cur = db.cursor()

print('=== All Users ===')
cur.execute('SELECT id, name, email, role FROM users')
for row in cur.fetchall():
    print(f'ID:{row[\"id\"]:3} | {row[\"name\"]:20} | {row[\"email\"]:30} | {row[\"role\"]}')

if not cur.fetchall():
    print('  (No users found!)')
"
```

### Step 3: Check Current Token
1. Open browser DevTools (F12)
2. Go to Console tab
3. Type: `localStorage.getItem('token')`
4. Copy the token
5. Go to jwt.io
6. Paste token on left side
7. Check "email" field in payload - is it an admin?

### Step 4: Manual Token Test
```bash
# Test with known good token
python -c "
from flask_jwt_extended import create_access_token

# Create admin token
admin_token = create_access_token(identity='admin@school.com')
print(f'Admin token: {admin_token}')

# Test decode
from flask_jwt_extended import decode_token
decoded = decode_token(admin_token)
print(f'Decoded: {decoded}')
"
```

## Common Fixes

### Fix 1: Recreate Admin User
```bash
python -c "
import sqlite3
db = sqlite3.connect('database/smart_school.db')
cur = db.cursor()

# Delete admin if exists
cur.execute('DELETE FROM users WHERE email = \"admin@school.com\"')
db.commit()

# Recreate admin
from smart_school_backend.models.user import create_user
user_id = create_user(
    name='Administrator',
    email='admin@school.com',
    password='SecureAdminPassword123',
    role='admin'
)
print(f'Admin user created with ID: {user_id}')
"
```

### Fix 2: Clear and Re-login
1. Stop frontend dev server
2. Clear browser storage:
   - F12 → Application → Local Storage → Clear All
   - F12 → Application → Cookies → Clear All
3. Restart frontend: `npm run dev`
4. Log in again as admin

### Fix 3: Restart Backend
```bash
# Stop current backend (Ctrl+C)
# Then restart:
python app.py
```

### Fix 4: Reset Database
⚠️ **WARNING: This deletes all data!**
```bash
python -c "
import os
os.remove('database/smart_school.db')
print('Database deleted')
"
# Then restart backend - it will recreate empty schema
```

## After Each Fix, Test With:

1. **Browser Console:**
   ```javascript
   // Check token
   console.log(localStorage.getItem('token').substring(0, 50));
   
   // Check if admin
   // Manually decode the token on jwt.io
   ```

2. **Test Add Teacher:**
   - Go to Admin → Add Teacher
   - Fill basic info
   - Capture face
   - Click "Add Teacher"
   - Watch backend logs for `[FACE ENROLL]` message
   - Check response status (should be 200)

3. **Network Tab Check:**
   - F12 → Network
   - Create teacher
   - Find `/api/face/enroll` request
   - Status should be 200 (not 403)
   - Response should show success

## Expected Log Output (Success Case)

```
[FACE ENROLL] JWT Identity: admin@school.com, Role: admin
[FACE ENROLL] Admin authorization passed
Embedding saved successfully
```

## Expected Log Output (Failure Case - Fix It!)

```
[FACE ENROLL] JWT Identity: admin@school.com, Role: None
Unauthorized - Role: None (indicates user email not in database)

# Or:

[FACE ENROLL] Error getting user role: ...
# (indicates database error)

# Or:

[FACE ENROLL] JWT Identity: None, Role: None
# (indicates invalid JWT token)
```

## Quick Test Script

Save as `test_face_enroll.py` and run:

```python
import sqlite3
import requests

# 1. Check database
print("=== Database Check ===")
db = sqlite3.connect('database/smart_school.db')
cur = db.cursor()
cur.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
admin_count = cur.fetchone()[0]
print(f"Admin users in DB: {admin_count}")

if admin_count == 0:
    print("❌ ERROR: No admin user found!")
    print("   Create admin first: python create_admin.py")
else:
    print("✅ Admin user exists")

# 2. Test login
print("\n=== Login Test ===")
try:
    response = requests.post(
        'http://127.0.0.1:5000/api/auth/login',
        json={'email': 'admin@school.com', 'password': 'Admin123'}
    )
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✅ Login successful")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Login error: {e}")

# 3. Check teachers
print("\n=== Teachers Check ===")
cur.execute("SELECT COUNT(*) FROM teachers")
teacher_count = cur.fetchone()[0]
print(f"Teachers in DB: {teacher_count}")
```

Run it:
```bash
python test_face_enroll.py
```

This will tell you exactly what's wrong!
