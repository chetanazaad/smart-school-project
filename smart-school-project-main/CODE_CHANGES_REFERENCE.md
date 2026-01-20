# Code Changes Reference

## Modified Files

### 1. AddTeacher.jsx - Complete Updated File
**Path:** `smart-school-frontend/src/pages/Admin/AddTeacher.jsx`

Key changes:
1. **State** - Added 3 new fields (lines 16-18)
2. **Validation** - Added class/section check (lines 57-60)
3. **API Call** - Sends new fields (lines 78-79)
4. **UI** - Added checkbox and conditional fields (lines 158-201)

**Snippet - State Addition:**
```javascript
const [form, setForm] = useState({
  id_code: "",
  name: "",
  email: "",
  subject: "",
  password: "",
  confirmPassword: "",
  is_class_teacher: false,        // NEW
  assigned_class: "",              // NEW
  assigned_section: "",            // NEW
});
```

**Snippet - Validation:**
```javascript
if (form.is_class_teacher && (!form.assigned_class || !form.assigned_section)) {
  setError("Class and Section are required for Class Teachers");
  return;
}
```

**Snippet - API Call:**
```javascript
const createRes = await API.post("/teachers", {
  id_code: form.id_code,
  name: form.name,
  email: form.email,
  subject: form.subject,
  password: form.password,
  is_class_teacher: form.is_class_teacher,           // NEW
  assigned_class: form.is_class_teacher ? form.assigned_class : null,  // NEW
  assigned_section: form.is_class_teacher ? form.assigned_section : null,  // NEW
});
```

**Snippet - UI (Checkbox):**
```jsx
<div className="border border-amber-300 bg-amber-50 p-4 rounded">
  <label className="flex items-center gap-3 cursor-pointer">
    <input
      type="checkbox"
      name="is_class_teacher"
      checked={form.is_class_teacher}
      onChange={(e) => setForm({ ...form, is_class_teacher: e.target.checked })}
      className="w-5 h-5"
    />
    <span className="font-medium text-gray-800">This teacher is a Class Teacher</span>
  </label>
  <p className="text-sm text-gray-600 mt-2">Class teachers manage a specific class and can enroll students</p>
</div>
```

**Snippet - UI (Conditional Fields):**
```jsx
{form.is_class_teacher && (
  <div className="space-y-3 p-4 bg-blue-50 border border-blue-200 rounded">
    <div>
      <label className="block text-sm font-medium mb-1">Class Name *</label>
      <input
        name="assigned_class"
        placeholder="e.g., Class 10, Class 11"
        value={form.assigned_class}
        onChange={handleChange}
        className="border p-3 rounded w-full"
        required={form.is_class_teacher}
      />
    </div>
    <div>
      <label className="block text-sm font-medium mb-1">Section *</label>
      <input
        name="assigned_section"
        placeholder="e.g., A, B, C"
        value={form.assigned_section}
        onChange={handleChange}
        className="border p-3 rounded w-full"
        required={form.is_class_teacher}
      />
    </div>
  </div>
)}
```

---

### 2. EditTeacher.jsx - Complete Updated File
**Path:** `smart-school-frontend/src/pages/Admin/EditTeacher.jsx`

**Complete file:**
```javascript
import { useEffect, useState } from "react";
import API from "../../services/api";
import { useNavigate, useParams } from "react-router-dom";

export default function EditTeacher() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    is_class_teacher: false,          // NEW
    assigned_class: "",                // NEW
    assigned_section: "",              // NEW
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchTeacher = async () => {
    try {
      const res = await API.get(`/teachers/${id}`);
      setForm(res.data.teacher);
    } catch (err) {
      console.error("Error fetching teacher:", err);
      setError("Failed to load teacher details");
    }
  };

  useEffect(() => {
    fetchTeacher();
  }, []);

  // NEW: Handle checkbox separately from text inputs
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,  // UPDATED
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // NEW: Validate class/section for class teachers
    if (form.is_class_teacher && (!form.assigned_class || !form.assigned_section)) {
      setError("Class and Section are required for Class Teachers");
      return;
    }

    setLoading(true);
    try {
      await API.put(`/teachers/${id}`, form);  // UPDATED: sends new fields
      navigate("/admin/teachers");
    } catch (err) {
      console.error("Update failed:", err);
      setError(err.response?.data?.error || "Failed to update teacher");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-5">Edit Teacher</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <input
          name="name"
          placeholder="Teacher Name"
          value={form.name}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        <input
          name="subject"
          placeholder="Subject"
          value={form.subject}
          onChange={handleChange}
          className="border p-3 rounded w-full"
          required
        />

        {/* NEW: Class teacher checkbox section */}
        <div className="border border-amber-300 bg-amber-50 p-4 rounded">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              name="is_class_teacher"
              checked={form.is_class_teacher}
              onChange={handleChange}
              className="w-5 h-5"
            />
            <span className="font-medium text-gray-800">This teacher is a Class Teacher</span>
          </label>
          <p className="text-sm text-gray-600 mt-2">Class teachers manage a specific class and can enroll students</p>
        </div>

        {/* NEW: Conditional class/section fields */}
        {form.is_class_teacher && (
          <div className="space-y-3 p-4 bg-blue-50 border border-blue-200 rounded">
            <div>
              <label className="block text-sm font-medium mb-1">Class Name *</label>
              <input
                name="assigned_class"
                placeholder="e.g., Class 10, Class 11"
                value={form.assigned_class || ""}
                onChange={handleChange}
                className="border p-3 rounded w-full"
                required={form.is_class_teacher}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Section *</label>
              <input
                name="assigned_section"
                placeholder="e.g., A, B, C"
                value={form.assigned_section || ""}
                onChange={handleChange}
                className="border p-3 rounded w-full"
                required={form.is_class_teacher}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Updating..." : "Update Teacher"}
        </button>
      </form>
    </div>
  );
}
```

---

## Summary of Changes

### What Changed
| Component | Before | After |
|-----------|--------|-------|
| **Form State** | 6 fields | 9 fields (+3 class teacher fields) |
| **handleChange** | Simple value change | Handles checkbox + text inputs |
| **Validation** | 4 checks | 5 checks (+class/section validation) |
| **API Call** | 6 field payload | 9 field payload (+3 new fields) |
| **Form UI** | 4 inputs | 4 inputs + checkbox + 2 conditional inputs |
| **Error States** | 4 possible errors | 5 possible errors |

### Fields Added to Both Components

1. **is_class_teacher** (boolean)
   - Checkbox input
   - Controls visibility of class/section fields
   
2. **assigned_class** (string)
   - Text input
   - Shows class name like "Class 10", "Class 11"
   - Required when is_class_teacher = true
   
3. **assigned_section** (string)
   - Text input
   - Shows section like "A", "B", "C"
   - Required when is_class_teacher = true

### UI Components Added

1. **Amber Checkbox Section**
   - Visual prominence (amber background)
   - Checkbox label
   - Description text
   - Always visible
   
2. **Blue Conditional Section**
   - Appears only when checkbox checked
   - Two input fields (class name, section)
   - Required field indicators (*)
   - Blue background for visual distinction

### Backend Compatibility

Both forms now send data in this format:
```javascript
{
  // Existing fields
  name: "John Doe",
  email: "john@school.com",
  subject: "Math",
  
  // New class teacher fields
  is_class_teacher: true,
  assigned_class: "Class 10",
  assigned_section: "A"
}
```

The backend API is already prepared to:
- Accept these fields in POST /teachers
- Accept these fields in PUT /teachers/{id}
- Store them in database columns: is_class_teacher, assigned_class, assigned_section
- Return them in GET /teachers/{id}

---

## Testing the Implementation

### Browser DevTools Check
1. Open DevTools (F12)
2. Go to Network tab
3. Create or edit a teacher with class teacher selected
4. Find the POST/PUT request to /teachers
5. Inspect Request payload - should include new fields

### Backend Logs Check
1. Watch the Flask backend terminal
2. Create/Edit teacher with class teacher selected
3. Should see HTTP request logged
4. No 400/500 errors
5. Response should be 200 OK with teacher data

### Frontend Visual Check
1. Load the form
2. Checkbox is visible (amber box)
3. Class/section fields NOT visible initially
4. Click checkbox → blue section appears
5. Unclick checkbox → blue section disappears
6. Required validation works when filling form

---

## No Breaking Changes

✅ All existing functionality preserved
✅ Non-class-teacher enrollment still works (just leave checkbox unchecked)
✅ All previous validation checks still in place
✅ API backward compatible (new fields are optional/null)
✅ Database backward compatible (new columns nullable)
✅ No changes needed to other components
