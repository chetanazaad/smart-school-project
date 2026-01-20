# Quick Reference Card - Class Teacher UI

## What Was Done ✅

✅ **AddTeacher.jsx** - Added class teacher selection UI
✅ **EditTeacher.jsx** - Added class teacher selection UI
✅ Both forms now have checkbox for marking teachers as class teachers
✅ Both forms conditionally show class/section fields when checkbox selected
✅ Validation requires class/section when marking as class teacher

## How to Use

### As an Admin

**Create a Class Teacher:**
1. Go to Admin → Add Teacher
2. Fill teacher details
3. **CHECK** "This teacher is a Class Teacher"
4. Blue box appears → Enter Class Name (e.g., "Class 10")
5. Blue box → Enter Section (e.g., "A")
6. Complete enrollment
7. Teacher is now a class teacher!

**Create a Regular Teacher:**
1. Go to Admin → Add Teacher
2. Fill teacher details
3. Leave "This teacher is a Class Teacher" **UNCHECKED**
4. No class/section fields needed
5. Complete enrollment

**Edit a Teacher:**
1. Go to Admin → Teachers
2. Click Edit on teacher
3. Check/uncheck the class teacher checkbox
4. Edit class/section if needed
5. Click Update

## Visual Guide

### Checkbox (Always Visible)
```
┌──────────────────────────────┐
│ ☑ This teacher is a Class    │
│   Teacher                    │
│                              │
│ Class teachers manage a      │
│ specific class and can       │
│ enroll students              │
└──────────────────────────────┘
```

### Conditional Fields (Only When Checkbox Checked)
```
┌──────────────────────────────┐
│ Class Name *                 │
│ [e.g., Class 10, Class 11]   │
│                              │
│ Section *                    │
│ [e.g., A, B, C]             │
└──────────────────────────────┘
```

## What Gets Sent to Backend

**Regular Teacher:**
```json
{
  "name": "John Doe",
  "email": "john@school.com",
  "subject": "Math",
  "is_class_teacher": false,
  "assigned_class": null,
  "assigned_section": null
}
```

**Class Teacher:**
```json
{
  "name": "Jane Smith",
  "email": "jane@school.com",
  "subject": "Science",
  "is_class_teacher": true,
  "assigned_class": "Class 10",
  "assigned_section": "A"
}
```

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Class and Section are required for Class Teachers" | Checkbox checked but empty fields | Fill Class Name and Section |
| "All fields are required" | Missing name/email/subject | Fill all basic fields |
| "Password must be at least 6 characters" | Password too short | Use 6+ character password |
| "Passwords do not match" | Password fields don't match | Re-enter matching passwords |

## Testing Checklist

- [ ] Can check the class teacher checkbox
- [ ] Blue section appears when checkbox checked
- [ ] Blue section disappears when checkbox unchecked
- [ ] Can't submit if checkbox checked but class/section empty
- [ ] Can submit when all required fields filled
- [ ] Created teacher shows in teachers list
- [ ] Can edit teacher and toggle class teacher status
- [ ] Form validates properly
- [ ] No console errors in DevTools

## Browser DevTools Check

To verify data is being sent correctly:

1. Press **F12** to open DevTools
2. Go to **Network** tab
3. Create/Edit a teacher with class teacher checked
4. Find the **POST /teachers** or **PUT /teachers/{id}** request
5. Click on it and go to **Request** tab
6. Look for:
   ```json
   {
     "is_class_teacher": true,
     "assigned_class": "Class 10",
     "assigned_section": "A"
   }
   ```

## Files Updated

| File | Location |
|------|----------|
| **AddTeacher.jsx** | `smart-school-frontend/smart-school-frontend/src/pages/Admin/` |
| **EditTeacher.jsx** | `smart-school-frontend/smart-school-frontend/src/pages/Admin/` |

## Start Frontend

```bash
cd smart-school-frontend/smart-school-frontend
npm run dev
```

Then open: http://localhost:5173

## Common Issues & Fixes

**Issue:** Blue section not showing when checkbox checked
- **Fix:** Clear browser cache (Ctrl+Shift+Del) and refresh

**Issue:** Can't click the checkbox
- **Fix:** Restart dev server (`npm run dev`)

**Issue:** Form won't submit with class teacher selected
- **Fix:** Make sure both Class Name and Section are filled in

**Issue:** Backend shows error when submitting
- **Fix:** Check Network tab (F12) to see what data is being sent
- **Fix:** Verify class/section fields have values

## Key Points

✅ Checkbox controls visibility of class/section fields
✅ Class/section fields are required when checkbox is checked
✅ Form won't submit if data is invalid
✅ Both Add and Edit forms work the same way
✅ Backend is already ready to receive this data
✅ No breaking changes - regular teachers still work fine

## Success = 

✅ Checkbox visible in Add/Edit forms
✅ Can toggle checkbox on/off
✅ Blue section appears/disappears correctly
✅ Form validates data properly
✅ Backend receives POST/PUT requests without error
✅ Teacher successfully created/updated with class teacher status

---

**Ready to use!** Start the frontend and go to Admin → Add Teacher to see the new class teacher option.
