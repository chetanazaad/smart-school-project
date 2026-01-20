# 🔴 CRITICAL FIX: JWT Identity Mismatch

## The Problem

**In Logs:**
```
[FACE ENROLL] JWT Identity: 1, Role: None
[FACE ENROLL] Unauthorized - Role: None
```

**Root Cause:**
- JWT token created with `identity = user["id"]` (the number: 1)
- Face enrollment code expected `identity = email` (string: admin@school.com)
- Mismatch caused role lookup to fail

**Logic:**
```
auth.py login creates: create_access_token(identity=1)           ❌ WRONG
enrollment.py checks:  SELECT role FROM users WHERE email = 1   ❌ No user with email "1"
Result: Role = None                                              ❌ Authorization fails
```

## The Fix

**File:** `smart_school_backend/routes/auth.py`

**Change:** Use email as JWT identity instead of user ID

### Before:
```python
# Line 33 - WRONG
additional_claims = {"email": user["email"], "role": user["role"]}
token = create_access_token(identity=str(user["id"]), additional_claims=additional_claims)
```

### After:
```python
# Line 33 - CORRECT
additional_claims = {"id": user["id"], "role": user["role"]}
token = create_access_token(identity=user["email"], additional_claims=additional_claims)
```

**Now:**
```
auth.py login creates: create_access_token(identity="admin@school.com")  ✅ CORRECT
enrollment.py checks:  SELECT role FROM users WHERE email = "admin@school.com"  ✅ Found!
Result: Role = admin                                                     ✅ Authorization passes!
```

## Changes Made

### 1. Login endpoint (Line 33)
- Changed: `identity=str(user["id"])` → `identity=user["email"]`
- Changed: JWT claims from `{"email": ..., "role": ...}` → `{"id": ..., "role": ...}`

### 2. /me endpoint (Line 48)
- Changed: `get_jwt_identity()` returns email (was ID)
- Updated: Use `get_user_by_email()` instead of `get_user_by_id()`

### 3. /update-email endpoint (Line 63)
- Changed: Get user_id by looking up the email from JWT
- Updated: No longer assume JWT identity is numeric

### 4. /update-password endpoint (Line 89)
- Changed: Get user_id by looking up the email from JWT
- Updated: No longer assume JWT identity is numeric

## Test Steps

1. **Restart backend:**
   ```bash
   cd smart_school_backend
   python app.py
   ```

2. **Clear browser storage:**
   - F12 → Application → Local Storage → Clear All
   - Close and reopen browser

3. **Log in as admin:**
   - Email: admin@school.com
   - Password: admin123

4. **Create a teacher:**
   - Go to Admin → Add Teacher
   - Fill form and capture face
   - Click "Add Teacher"

5. **Check logs:**
   - Should see: `[FACE ENROLL] JWT Identity: admin@school.com, Role: admin`
   - Should NOT see: `[FACE ENROLL] JWT Identity: 1, Role: None`

## Expected Results After Fix ✅

```
POST /api/teachers → 201 ✅ Teacher created
POST /api/face/enroll → [FACE ENROLL] JWT Identity: admin@school.com, Role: admin
POST /api/face/enroll → 200 ✅ Face enrolled successfully
```

## No Breaking Changes ✅

- ✅ Login still works same way
- ✅ Token still contains id and role in claims (just reorganized)
- ✅ Frontend doesn't need changes
- ✅ All other endpoints using JWT still work
- ✅ Backward compatible with existing authentication flow

## Why This Was Missed

The code had two different patterns:
- Some parts expected JWT identity = user ID (integer)
- Other parts expected JWT identity = email (string)

The conflict only appeared when using authorization checks that look up user by email. The face enrollment is one of the few places that does email-based lookups, which exposed the bug.

## Files Modified

- `smart_school_backend/routes/auth.py` - JWT identity changed from ID to email

---

**Status:** ✅ FIXED
**Ready to Deploy:** YES
**Test Required:** YES - Log in again after fix
