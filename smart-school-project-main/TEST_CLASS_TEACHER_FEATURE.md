# Quick Test Guide: Class Teacher Feature

## Start the Frontend
```bash
cd smart-school-frontend/smart-school-frontend
npm run dev
```

## Test 1: Add New Class Teacher

1. Open http://localhost:5173 (or your dev server URL)
2. Navigate to **Admin → Add Teacher**
3. Fill in basic details:
   - Teacher ID: Auto-generated (or click "New")
   - Name: John Mathematics
   - Email: john.math@school.com
   - Subject: Mathematics
4. **IMPORTANT**: Check the amber box: "This teacher is a Class Teacher"
5. Blue section appears with two new fields:
   - Class Name: Enter "Class 10"
   - Section: Enter "A"
6. Set password: Test1234 (must be 6+ chars)
7. Click "Enroll Face" - use your camera to capture a face
8. Click "Add Teacher"
9. **Verify**: Teacher created successfully, redirects to teacher list

## Test 2: Class Teacher Validation

1. In **Add Teacher** form:
2. Check "This teacher is a Class Teacher"
3. Leave Class Name and Section EMPTY
4. Click "Add Teacher"
5. **Expected**: Error message appears: "Class and Section are required for Class Teachers"
6. Fill in Class Name and Section
7. **Expected**: Error disappears, form can be submitted

## Test 3: Regular Teacher (Not Class Teacher)

1. In **Add Teacher** form:
2. Leave "This teacher is a Class Teacher" UNCHECKED
3. Fill teacher details normally (no Class/Section needed)
4. The blue section with Class/Section should NOT appear
5. Complete enrollment
6. **Verify**: Teacher created without class teacher assignment

## Test 4: Edit Class Teacher

1. Navigate to **Admin → Teachers** list
2. Click edit button on any teacher
3. Check the "This teacher is a Class Teacher" checkbox
4. Blue section appears with Class/Section fields
5. Enter Class Name and Section
6. Click "Update Teacher"
7. **Verify**: Update successful, returns to teacher list

## Test 5: Edit to Remove Class Teacher Status

1. Edit an existing class teacher
2. UNCHECK "This teacher is a Class Teacher"
3. Blue section disappears
4. Click "Update Teacher"
5. **Verify**: Teacher status updated

## Backend Integration Check

1. Open browser DevTools (F12)
2. Go to Network tab
3. Create/Edit a teacher with class teacher selected
4. Look for **POST /teachers** or **PUT /teachers/{id}** request
5. Click on request, view "Request" tab
6. **Verify** JSON body includes:
   ```json
   {
     "is_class_teacher": true,
     "assigned_class": "Class 10",
     "assigned_section": "A"
   }
   ```

## Terminal Check

1. Watch backend terminal where Flask is running
2. Create/Edit a teacher with class teacher selected
3. **Verify** you see HTTP request logs showing the requests being processed
4. **Verify** No 400/500 errors
5. Response should be 200 OK

## Expected Screen Changes

### Before (Old UI)
```
Add Teacher Form:
- Teacher ID
- Name
- Email
- Subject
- Password
- Confirm Password
- Face Enroll
- Add Button
```

### After (New UI)
```
Add Teacher Form:
- Teacher ID
- Name
- Email
- Subject
- [NEW] ☑ This teacher is a Class Teacher    ← AMBER BOX
- [NEW] Class Name (when checkbox checked)   ← BLUE SECTION
- [NEW] Section (when checkbox checked)      ← BLUE SECTION
- Password
- Confirm Password
- Face Enroll
- Add Button
```

## Troubleshooting

### Issue: Class/Section fields not appearing when checkbox checked
- **Solution**: Clear browser cache (Ctrl+Shift+Del)
- **Solution**: Restart dev server (npm run dev)
- **Check**: Verify AddTeacher.jsx includes conditional render: `{form.is_class_teacher && (...)}`

### Issue: Form submits but class teacher fields not saved
- **Check**: Browser DevTools Network tab - verify fields in POST/PUT request body
- **Check**: Backend should show fields in request logs
- **Solution**: Verify backend database has schema with new columns

### Issue: Cannot uncheck checkbox
- **Solution**: Verify handleChange includes: `type === "checkbox" ? checked : value`

### Issue: Error "Class and Section are required" even when filled
- **Check**: Verify fields have correct names: `assigned_class` and `assigned_section`
- **Check**: Verify validation uses `form.assigned_class` and `form.assigned_section`

## Success Indicators ✅

- [x] Amber checkbox appears in Add/Edit forms
- [x] Checkbox is clickable and toggles state
- [x] Blue section appears/disappears based on checkbox state
- [x] Class Name and Section inputs appear in blue section
- [x] Form validates that class/section required when checkbox selected
- [x] Form sends new fields to backend API
- [x] Backend receives requests without errors
- [x] Teacher successfully created/updated with class teacher status
