# Teacher Features - Comprehensive Documentation

**Status**: ✅ All features implemented and tested

This document covers all teacher-related features including class teacher functionality, face recognition, student enrollment, timetable management, and attendance marking.

---

## Table of Contents

1. [Overview](#overview)
2. [Teacher Roles & Permissions](#teacher-roles--permissions)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Authorization Rules](#authorization-rules)
6. [Frontend Integration Guide](#frontend-integration-guide)

---

## Overview

The Smart School system supports two types of teachers:

### **Class Teachers**
- Assigned to a specific class and section
- Can enroll their students for face recognition
- Can recognize their students' faces and their own
- View their enrolled students list
- View personal timetable + class timetable
- Mark their own attendance

### **Regular Teachers**
- Subject teachers without class assignment
- **Cannot** enroll students
- **Cannot** view student enrollment
- Can only recognize themselves via face recognition
- Can only mark their own attendance
- Use dedicated attendance-only dashboard

---

## Teacher Roles & Permissions

| Feature | Class Teacher | Regular Teacher | Admin |
|---------|---------------|-----------------|-------|
| **Enroll own face** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Enroll students' faces** | ✅ Yes (own class only) | ❌ No | ✅ Yes (any) |
| **Recognize own face** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Recognize students' faces** | ✅ Yes (own class) | ❌ No | ✅ Yes (any) |
| **View enrolled students** | ✅ Yes (own class) | ❌ No | ✅ Yes (all) |
| **View personal timetable** | ✅ Yes | ✅ Yes | ✅ Yes |
| **View class timetable** | ✅ Yes (own class) | ❌ No | ✅ Yes (any) |
| **Mark own attendance** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Mark student attendance** | ✅ Yes (own class) | ❌ No | ✅ Yes (any) |
| **Update profile** | ✅ Yes | ✅ Yes | ✅ Yes |

---

## API Endpoints

### 1. Teacher Management

#### **Create Teacher (Enrollment)**
```http
POST /api/teachers
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Regular Teacher Request:**
```json
{
  "name": "John Doe",
  "email": "john@school.com",
  "id_code": "T001",
  "subject": "Mathematics",
  "password": "secure_password",
  "is_class_teacher": false
}
```

**Class Teacher Request:**
```json
{
  "name": "Jane Smith",
  "email": "jane@school.com",
  "id_code": "T002",
  "subject": "English",
  "password": "secure_password",
  "is_class_teacher": true,
  "assigned_class": "Class 10",
  "assigned_section": "A"
}
```

**Response:**
```json
{
  "message": "Teacher created with login credentials",
  "id": 1,
  "user_id": 10,
  "is_class_teacher": true
}
```

**Validation Rules:**
- If `is_class_teacher` is `true`, both `assigned_class` and `assigned_section` are **required**
- If `is_class_teacher` is `false`, class/section are optional (can be `null`)
- Email must be unique
- Password is optional (can create teacher without login account)

---

#### **Get All Teachers**
```http
GET /api/teachers
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "teachers": [
    {
      "id": 1,
      "name": "Jane Smith",
      "email": "jane@school.com",
      "subject": "English",
      "is_class_teacher": true,
      "assigned_class": "Class 10",
      "assigned_section": "A"
    },
    {
      "id": 2,
      "name": "John Doe",
      "email": "john@school.com",
      "subject": "Mathematics",
      "is_class_teacher": false,
      "assigned_class": null,
      "assigned_section": null
    }
  ]
}
```

---

#### **Get Teacher Details**
```http
GET /api/teachers/{teacher_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "teacher": {
    "id": 1,
    "name": "Jane Smith",
    "email": "jane@school.com",
    "id_code": "T002",
    "subject": "English",
    "is_class_teacher": true,
    "assigned_class": "Class 10",
    "assigned_section": "A"
  }
}
```

---

#### **Update Teacher Details**
```http
PUT /api/teachers/{teacher_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request (Change to Class Teacher):**
```json
{
  "is_class_teacher": true,
  "assigned_class": "Class 11",
  "assigned_section": "B"
}
```

**Request (Update Profile):**
```json
{
  "name": "Jane Smith Updated",
  "subject": "English & Literature"
}
```

**Response:**
```json
{
  "message": "Teacher updated"
}
```

**Important:**
- If changing to class teacher, both `assigned_class` and `assigned_section` must be provided
- Partial updates are allowed (only send fields to update)
- All fields including new class teacher fields are returned in GET requests

---

#### **Delete Teacher**
```http
DELETE /api/teachers/{teacher_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "message": "Teacher deleted"
}
```

---

### 2. Class Teacher Dashboard

#### **Get Class Teacher Dashboard**
```http
GET /api/teachers/{teacher_id}/dashboard
Authorization: Bearer {jwt_token}
```

**Authorization:**
- ✅ Only class teachers can access (returns 403 if regular teacher)
- ✅ Can only view own dashboard

**Response:**
```json
{
  "teacher": {
    "id": 1,
    "name": "Jane Smith",
    "email": "jane@school.com",
    "subject": "English",
    "is_class_teacher": true,
    "assigned_class": "Class 10",
    "assigned_section": "A"
  },
  "enrolled_students": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@school.com",
      "id_code": "S001",
      "class_name": "Class 10",
      "section": "A"
    },
    {
      "id": 2,
      "name": "Bob Smith",
      "email": "bob@school.com",
      "id_code": "S002",
      "class_name": "Class 10",
      "section": "A"
    }
  ],
  "class_timetable": [
    {
      "id": 1,
      "day": "Monday",
      "subject": "English",
      "teacher_name": "Jane Smith",
      "start_time": "09:00",
      "end_time": "10:00"
    },
    {
      "id": 2,
      "day": "Monday",
      "subject": "Mathematics",
      "teacher_name": "John Doe",
      "start_time": "10:00",
      "end_time": "11:00"
    }
  ],
  "teacher_timetable": [
    {
      "id": 1,
      "day": "Monday",
      "class_name": "Class 10",
      "section": "A",
      "subject": "English",
      "start_time": "09:00",
      "end_time": "10:00"
    }
  ]
}
```

---

#### **Get Enrolled Students List**
```http
GET /api/teachers/{teacher_id}/enrolled-students
Authorization: Bearer {jwt_token}
```

**Authorization:**
- ✅ Only class teachers can access
- ✅ Returns students in their assigned class and section

**Response:**
```json
{
  "class": "Class 10",
  "section": "A",
  "total_students": 2,
  "students": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@school.com",
      "id_code": "S001",
      "class_name": "Class 10",
      "section": "A"
    },
    {
      "id": 2,
      "name": "Bob Smith",
      "email": "bob@school.com",
      "id_code": "S002",
      "class_name": "Class 10",
      "section": "A"
    }
  ]
}
```

---

### 3. Regular Teacher Attendance Dashboard

#### **Get Regular Teacher Attendance Interface**
```http
GET /api/teachers/{teacher_id}/attendance
Authorization: Bearer {jwt_token}
```

**Authorization:**
- ✅ Only regular teachers (non-class-teachers) can access
- ✅ Regular teachers get attendance-only interface without enrollment

**Response:**
```json
{
  "id": 2,
  "name": "John Doe",
  "email": "john@school.com",
  "subject": "Mathematics",
  "is_class_teacher": false,
  "can_enroll": false,
  "attendance_only": true
}
```

**Frontend Usage:**
- If `is_class_teacher` is `true` → Redirect to `/dashboard`
- If `is_class_teacher` is `false` → Show attendance-only interface
- Hide enrollment UI when `can_enroll` is `false`

---

### 4. Face Recognition & Enrollment

#### **Enroll Face**
```http
POST /api/face/enroll
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request:**
```json
{
  "image": "base64_encoded_image_data",
  "user_id": 1,
  "role": "student",
  "current_teacher_id": 2
}
```

**Authorization Rules:**
- **Admin**: Can enroll any student or teacher
- **Class Teacher**: Can enroll themselves or their students
- **Regular Teacher**: Can only enroll themselves (not students)
- **Student**: Cannot enroll

**Response (Success):**
```json
{
  "status": "success",
  "message": "Face enrolled successfully",
  "person_id": 1,
  "role": "student"
}
```

**Response (Unauthorized):**
```json
{
  "error": "Only class teachers can enroll students"
}
```

**Response (Already Enrolled):**
```json
{
  "error": "This face is already enrolled.",
  "existing_user": {
    "person_id": 1,
    "role": "student",
    "name": "Alice Johnson"
  }
}
```

---

#### **Recognize Face**
```http
POST /api/face/recognize
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request:**
```json
{
  "image_base64": "base64_encoded_image_data"
}
```

**Authorization Rules:**
- **Admin**: Can recognize any face (student or teacher)
- **Class Teacher**: 
  - Can recognize their own face
  - Can recognize students in their class
  - Cannot recognize other teachers' faces
- **Regular Teacher**: Can only recognize their own face
- **Student**: Cannot recognize anyone

**Response (Teacher):**
```json
{
  "match": true,
  "id": 1,
  "name": "Jane Smith",
  "role": "teacher",
  "distance": 0.45
}
```

**Response (Student):**
```json
{
  "match": true,
  "id": 1,
  "name": "Alice Johnson",
  "role": "student",
  "distance": 0.38
}
```

**Response (Unauthorized):**
```json
{
  "error": "You can only recognize yourself"
}
```

**Response (No Match):**
```json
{
  "match": false
}
```

---

#### **Get Enrollment Details (For Editing)**
```http
GET /api/face/enrollment/{role}/{user_id}
Authorization: Bearer {jwt_token}
```

**Authorization:**
- **Admin**: Can view any enrollment
- **Teacher**: Can view own or student enrollment (if class teacher)
- **Student**: Can view own enrollment only

**Response (Teacher):**
```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane@school.com",
  "id_code": "T002",
  "subject": "English",
  "is_class_teacher": true,
  "assigned_class": "Class 10",
  "assigned_section": "A",
  "role": "teacher"
}
```

**Response (Student):**
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@school.com",
  "id_code": "S001",
  "class": "Class 10",
  "section": "A",
  "role": "student"
}
```

---

### 5. Teacher Attendance

#### **Mark Teacher Attendance**
```http
POST /api/teacher-attendance/mark
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request:**
```json
{
  "teacher_id": 1,
  "status": "present"
}
```

**Status Options:**
- `present` (default)
- `absent`
- `late`
- `leave`

**Response:**
```json
{
  "message": "Attendance marked successfully"
}
```

---

#### **Get Teacher Attendance Records**
```http
GET /api/teacher-attendance/records
Authorization: Bearer {jwt_token}
```

**Response:**
```json
[
  {
    "date": "2025-01-19",
    "marked_at": "2025-01-19 09:15:30",
    "status": "present"
  },
  {
    "date": "2025-01-18",
    "marked_at": "2025-01-18 09:10:15",
    "status": "present"
  }
]
```

---

## Usage Examples

### **Scenario 1: Create a Class Teacher**

```bash
curl -X POST http://localhost:5000/api/teachers \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@school.com",
    "id_code": "T002",
    "subject": "English",
    "password": "secure123",
    "is_class_teacher": true,
    "assigned_class": "Class 10",
    "assigned_section": "A"
  }'
```

---

### **Scenario 2: Enroll Student's Face (By Class Teacher)**

1. **Get enrolled students:**
```bash
curl -X GET http://localhost:5000/api/teachers/1/enrolled-students \
  -H "Authorization: Bearer {jwt_token}"
```

2. **Enroll student's face:**
```bash
curl -X POST http://localhost:5000/api/face/enroll \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_image_data",
    "user_id": 1,
    "role": "student",
    "current_teacher_id": 1
  }'
```

---

### **Scenario 3: Recognize Student Face**

```bash
curl -X POST http://localhost:5000/api/face/recognize \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "base64_image_data"
  }'
```

**Result:** Only class teachers in the same class as the student will get a match for that student.

---

### **Scenario 4: Regular Teacher Accesses Attendance Dashboard**

```bash
# Get attendance interface
curl -X GET http://localhost:5000/api/teachers/2/attendance \
  -H "Authorization: Bearer {jwt_token}"

# Mark own attendance
curl -X POST http://localhost:5000/api/teacher-attendance/mark \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_id": 2,
    "status": "present"
  }'
```

---

### **Scenario 5: Change Regular Teacher to Class Teacher**

```bash
curl -X PUT http://localhost:5000/api/teachers/2 \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "is_class_teacher": true,
    "assigned_class": "Class 11",
    "assigned_section": "B"
  }'
```

---

## Authorization Rules

### **Face Enrollment (/api/face/enroll)**

| User Type | Can Enroll Self | Can Enroll Students | Can Enroll Other Teachers | Notes |
|-----------|-----------------|-------------------|--------------------------|-------|
| Admin | ✅ Yes | ✅ Yes (any) | ✅ Yes (any) | Full access |
| Class Teacher | ✅ Yes | ✅ Yes (own class only) | ❌ No | Cannot enroll other teachers |
| Regular Teacher | ✅ Yes | ❌ No | ❌ No | Limited access |
| Student | ❌ No | ❌ No | ❌ No | No access |

---

### **Face Recognition (/api/face/recognize)**

| User Type | Can Recognize Self | Can Recognize Students | Can Recognize Teachers | Notes |
|-----------|-------------------|----------------------|----------------------|-------|
| Admin | ✅ Yes | ✅ Yes (any) | ✅ Yes (any) | Full access |
| Class Teacher | ✅ Yes | ✅ Yes (own class) | ❌ No (others) | Limited to own class |
| Regular Teacher | ✅ Yes | ❌ No | ❌ No (others) | Self only |
| Student | ✅ Yes | ❌ No | ❌ No | Self only |

---

### **Dashboard Access**

| Endpoint | Admin | Class Teacher | Regular Teacher | Student |
|----------|-------|---------------|-----------------|---------|
| `/api/teachers/{id}/dashboard` | ✅ Yes | ✅ Yes (own) | ❌ No (403) | ❌ No (403) |
| `/api/teachers/{id}/attendance` | ✅ Yes | ❌ No (403) | ✅ Yes (own) | ❌ No (403) |
| `/api/teachers/{id}/enrolled-students` | ✅ Yes | ✅ Yes (own) | ❌ No (403) | ❌ No (403) |

---

## Frontend Integration Guide

### **1. Teacher Registration/Enrollment Form**

```javascript
// Form for creating a teacher
const teacherForm = {
  name: "Jane Smith",
  email: "jane@school.com",
  id_code: "T002",
  subject: "English",
  password: "secure123",
  is_class_teacher: true,  // Toggle
  assigned_class: "Class 10",  // Show if is_class_teacher = true
  assigned_section: "A"  // Show if is_class_teacher = true
};

// API Call
async function createTeacher(teacherData) {
  const response = await fetch('/api/teachers', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(teacherData)
  });
  return response.json();
}
```

### **2. Teacher Dashboard Selection**

```javascript
// After teacher login, determine which dashboard to show
async function getTeacherDashboard(teacherId) {
  const response = await fetch(`/api/teachers/${teacherId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const teacher = await response.json();
  
  if (teacher.teacher.is_class_teacher) {
    // Redirect to class teacher dashboard
    window.location.href = `/dashboard/class-teacher/${teacherId}`;
  } else {
    // Redirect to attendance-only dashboard
    window.location.href = `/dashboard/attendance/${teacherId}`;
  }
}
```

### **3. Class Teacher Dashboard**

```javascript
// Fetch class teacher dashboard data
async function fetchClassTeacherDashboard(teacherId) {
  const response = await fetch(`/api/teachers/${teacherId}/dashboard`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  return {
    teacher: data.teacher,
    students: data.enrolled_students,
    classTimetable: data.class_timetable,
    personalTimetable: data.teacher_timetable
  };
}
```

### **4. Student Enrollment (Class Teacher)**

```javascript
// Enroll a student's face
async function enrollStudentFace(studentId, imageBase64) {
  const response = await fetch('/api/face/enroll', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image: imageBase64,
      user_id: studentId,
      role: 'student',
      current_teacher_id: currentTeacherId
    })
  });
  
  return response.json();
}
```

### **5. Face Recognition (Attendance)**

```javascript
// Recognize a face
async function recognizeFace(imageBase64) {
  const response = await fetch('/api/face/recognize', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image_base64: imageBase64
    })
  });
  
  const result = await response.json();
  
  if (result.match) {
    // Show matched person
    console.log(`Recognized: ${result.name} (${result.role})`);
  } else {
    // No match
    console.log('Face not recognized');
  }
  
  return result;
}
```

### **6. Regular Teacher Dashboard**

```javascript
// Regular teacher gets attendance-only interface
async function getTeacherAttendanceInterface(teacherId) {
  const response = await fetch(`/api/teachers/${teacherId}/attendance`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  if (data.attendance_only) {
    // Show attendance marking UI only
    // Hide enrollment options
  }
  
  return data;
}

// Mark teacher attendance
async function markTeacherAttendance(teacherId, status = 'present') {
  const response = await fetch('/api/teacher-attendance/mark', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      teacher_id: teacherId,
      status: status
    })
  });
  
  return response.json();
}
```

---

## Error Handling

### **Common Error Responses**

#### **1. Unauthorized (403)**
```json
{
  "error": "Only class teachers can enroll students"
}
```

#### **2. Not Found (404)**
```json
{
  "error": "Teacher not found"
}
```

#### **3. Already Enrolled (409)**
```json
{
  "error": "This face is already enrolled.",
  "existing_user": {
    "person_id": 1,
    "role": "student",
    "name": "Alice Johnson"
  }
}
```

#### **4. Missing Fields (400)**
```json
{
  "error": "Class and section required for class teachers"
}
```

---

## Summary of Completed Features

✅ **Task 1**: Class teacher option during enrollment with `is_class_teacher`, `assigned_class`, `assigned_section`

✅ **Task 2**: Class teacher can enroll themselves and their students only. Face recognition authorization implemented.

✅ **Task 2.1**: Class teacher has list of enrolled students via `/api/teachers/{id}/enrolled-students`

✅ **Task 2.3**: Class teacher dashboard shows personal timetable + class timetable via `/api/teachers/{id}/dashboard`

✅ **Task 3**: Regular teachers can only mark their own attendance (no enrollment UI)

✅ **Task 4**: Update endpoint returns all editable fields (name, email, subject, is_class_teacher, assigned_class, assigned_section)

✅ **Teacher dashboard**: Does not have student enrollment option - uses `/api/teachers/{id}/attendance` for regular teachers

---

## Next Steps for Frontend

1. Modify teacher enrollment form to include class teacher toggle
2. Show class/section fields conditionally when `is_class_teacher` is enabled
3. Update teacher dashboard logic to redirect to appropriate view (class teacher dashboard vs attendance dashboard)
4. Hide enrollment UI for regular teachers
5. Implement face recognition and enrollment flows for class teachers
6. Add student list display for class teachers
7. Add timetable display for class teachers

