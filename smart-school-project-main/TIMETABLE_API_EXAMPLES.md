# Timetable API - Complete Usage Examples

## Quick Reference

### Base URLs
- **Backend API**: `http://localhost:5000`
- **All endpoints require**: `Authorization: Bearer {JWT_TOKEN}`

---

## 1. ADD TIMETABLE ENTRY (Admin Dashboard)

### Endpoint
```
POST /api/timetable/add
```

### Using cURL
```bash
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "class_name": "10",
    "section": "A",
    "subject": "Mathematics",
    "teacher_name": "Ratan",
    "day": "Monday",
    "start_time": "09:00",
    "end_time": "09:40"
  }'
```

### Using Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

data = {
    "class_name": "10",
    "section": "A",
    "subject": "Mathematics",
    "teacher_name": "Ratan",
    "day": "Monday",
    "start_time": "09:00",
    "end_time": "09:40"
}

response = requests.post(
    "http://localhost:5000/api/timetable/add",
    headers=headers,
    json=data
)

print(response.json())
# Output: {"message": "Timetable entry added successfully", "id": 1}
```

### Using JavaScript/Fetch
```javascript
const token = localStorage.getItem('jwt_token');

fetch('http://localhost:5000/api/timetable/add', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        class_name: "10",
        section: "A",
        subject: "Mathematics",
        teacher_name: "Ratan",
        day: "Monday",
        start_time: "09:00",
        end_time: "09:40"
    })
})
.then(res => res.json())
.then(data => console.log(data))
// Output: {message: "Timetable entry added successfully", id: 1}
```

### Response
```json
{
    "message": "Timetable entry added successfully",
    "id": 1
}
```

### Error Response
```json
{
    "error": "All fields are required: class_name, section, subject, teacher_name, day, start_time, end_time"
}
```

---

## 2. GET STUDENT TIMETABLE (Student Dashboard)

### Endpoint
```
GET /api/timetable/student/{student_id}/week
```

### Using cURL
```bash
curl -X GET http://localhost:5000/api/timetable/student/1/week \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Using Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.get(
    "http://localhost:5000/api/timetable/student/1/week",
    headers=headers
)

data = response.json()

print(f"Student: {data['student_name']}")
print(f"Class: {data['class_name']} Section: {data['section']}")
print("\nWeekly Timetable:")

for entry in data['timetable']:
    print(f"{entry['day']:12} | {entry['subject']:15} | Teacher: {entry['teacher_name']:15} | {entry['start_time']}-{entry['end_time']}")
```

### Using JavaScript/Fetch
```javascript
const token = localStorage.getItem('jwt_token');
const studentId = 1;

fetch(`http://localhost:5000/api/timetable/student/${studentId}/week`, {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(res => res.json())
.then(data => {
    console.log(`Student: ${data.student_name}`);
    console.log(`Class: ${data.class_name} Section: ${data.section}`);
    console.log('Weekly Timetable:');
    
    data.timetable.forEach(entry => {
        console.log(`${entry.day}: ${entry.subject} (${entry.teacher_name}) - ${entry.start_time} to ${entry.end_time}`);
    });
})
```

### Sample Response
```json
{
    "student_name": "John Doe",
    "class_name": "10",
    "section": "A",
    "timetable": [
        {
            "id": 1,
            "day": "Monday",
            "subject": "Mathematics",
            "teacher_name": "Ratan",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "id": 2,
            "day": "Monday",
            "subject": "English",
            "teacher_name": "Priya",
            "start_time": "09:40",
            "end_time": "10:20"
        },
        {
            "id": 3,
            "day": "Monday",
            "subject": "Science",
            "teacher_name": "Kumar",
            "start_time": "10:20",
            "end_time": "11:00"
        },
        {
            "id": 4,
            "day": "Tuesday",
            "subject": "Mathematics",
            "teacher_name": "Ratan",
            "start_time": "09:00",
            "end_time": "09:40"
        }
    ]
}
```

---

## 3. GET TEACHER TIMETABLE (Teacher Dashboard)

### Endpoint
```
GET /api/timetable/teacher/{teacher_id}/week
```

### Using cURL
```bash
curl -X GET http://localhost:5000/api/timetable/teacher/1/week \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Using Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.get(
    "http://localhost:5000/api/timetable/teacher/1/week",
    headers=headers
)

data = response.json()

print(f"Teacher: {data['teacher_name']}")
print("\nTeaching Schedule:")

for entry in data['timetable']:
    print(f"{entry['day']:12} | Class {entry['class_name']}{entry['section']:2} | {entry['subject']:15} | {entry['start_time']}-{entry['end_time']}")
```

### Using JavaScript/Fetch
```javascript
const token = localStorage.getItem('jwt_token');
const teacherId = 1;

fetch(`http://localhost:5000/api/timetable/teacher/${teacherId}/week`, {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(res => res.json())
.then(data => {
    console.log(`Teacher: ${data.teacher_name}`);
    console.log('Teaching Schedule:');
    
    data.timetable.forEach(entry => {
        console.log(`${entry.day}: Class ${entry.class_name}${entry.section} - ${entry.subject} (${entry.start_time} to ${entry.end_time})`);
    });
})
```

### Sample Response
```json
{
    "teacher_name": "Ratan",
    "timetable": [
        {
            "id": 1,
            "day": "Monday",
            "class_name": "10",
            "section": "A",
            "subject": "Mathematics",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "id": 5,
            "day": "Monday",
            "class_name": "10",
            "section": "B",
            "subject": "Mathematics",
            "start_time": "10:00",
            "end_time": "10:40"
        },
        {
            "id": 9,
            "day": "Monday",
            "class_name": "9",
            "section": "A",
            "subject": "Mathematics",
            "start_time": "14:00",
            "end_time": "14:40"
        },
        {
            "id": 4,
            "day": "Tuesday",
            "class_name": "10",
            "section": "A",
            "subject": "Mathematics",
            "start_time": "09:00",
            "end_time": "09:40"
        }
    ]
}
```

---

## 4. GET CLASS TIMETABLE (Generic)

### Endpoint
```
GET /api/timetable/{class_name}/{section}
```

### Using cURL
```bash
curl -X GET http://localhost:5000/api/timetable/10/A \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Using Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.get(
    "http://localhost:5000/api/timetable/10/A",
    headers=headers
)

data = response.json()

print("Class 10A Timetable:")
for entry in data['timetable']:
    print(f"{entry['day']:12} | {entry['subject']:15} | Teacher: {entry['teacher_name']:15} | {entry['start_time']}-{entry['end_time']}")
```

### Sample Response
```json
{
    "timetable": [
        {
            "id": 1,
            "class_name": "10",
            "section": "A",
            "subject": "Mathematics",
            "teacher_name": "Ratan",
            "day": "Monday",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "id": 2,
            "class_name": "10",
            "section": "A",
            "subject": "English",
            "teacher_name": "Priya",
            "day": "Monday",
            "start_time": "09:40",
            "end_time": "10:20"
        }
    ]
}
```

---

## 5. DELETE TIMETABLE ENTRY

### Endpoint
```
DELETE /api/timetable/{entry_id}
```

### Using cURL
```bash
curl -X DELETE http://localhost:5000/api/timetable/1 \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Using Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.delete(
    "http://localhost:5000/api/timetable/1",
    headers=headers
)

print(response.json())
```

### Response
```json
{
    "message": "Timetable entry removed successfully"
}
```

---

## 6. GET TEACHER'S CLASSES TODAY

### Endpoint
```
GET /api/timetable/teacher/{teacher_id}/today
```

### Using cURL
```bash
curl -X GET http://localhost:5000/api/timetable/teacher/1/today \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Response
```json
{
    "count": 3
}
```

---

## Complete Workflow Example

### Step 1: Admin adds timetable entries
```bash
# Add Math for Class 10A on Monday
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"class_name":"10","section":"A","subject":"Math","teacher_name":"Ratan","day":"Monday","start_time":"09:00","end_time":"09:40"}'

# Add English for Class 10A on Monday
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"class_name":"10","section":"A","subject":"English","teacher_name":"Priya","day":"Monday","start_time":"09:40","end_time":"10:20"}'

# Add Math for Class 10B on Monday
curl -X POST http://localhost:5000/api/timetable/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"class_name":"10","section":"B","subject":"Math","teacher_name":"Ratan","day":"Monday","start_time":"10:00","end_time":"10:40"}'
```

### Step 2: Student John (ID 1, Class 10A) views his timetable
```bash
curl -X GET http://localhost:5000/api/timetable/student/1/week \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

Response shows:
- Math on Monday 09:00-09:40 (Ratan)
- English on Monday 09:40-10:20 (Priya)
- (Other classes for this week)

### Step 3: Teacher Ratan (ID 1) views his schedule
```bash
curl -X GET http://localhost:5000/api/timetable/teacher/1/week \
  -H "Authorization: Bearer $TEACHER_TOKEN"
```

Response shows:
- Class 10A - Math on Monday 09:00-09:40
- Class 10B - Math on Monday 10:00-10:40
- (All other classes he teaches)

---

## Integration with Frontend

### React Component Example
```javascript
import React, { useEffect, useState } from 'react';

const StudentTimetable = ({ studentId, token }) => {
    const [timetable, setTimetable] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchTimetable();
    }, [studentId]);

    const fetchTimetable = async () => {
        try {
            const response = await fetch(
                `http://localhost:5000/api/timetable/student/${studentId}/week`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            
            if (!response.ok) throw new Error('Failed to fetch timetable');
            
            const data = await response.json();
            setTimetable(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h2>{timetable.student_name}</h2>
            <p>Class: {timetable.class_name}{timetable.section}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Day</th>
                        <th>Subject</th>
                        <th>Teacher</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {timetable.timetable.map((entry, idx) => (
                        <tr key={idx}>
                            <td>{entry.day}</td>
                            <td>{entry.subject}</td>
                            <td>{entry.teacher_name}</td>
                            <td>{entry.start_time} - {entry.end_time}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default StudentTimetable;
```

---

## Error Codes

| Code | Error | Meaning |
|------|-------|---------|
| 400 | All fields are required | Missing required fields in POST request |
| 404 | Student not found | Student ID doesn't exist |
| 404 | Teacher not found | Teacher ID doesn't exist |
| 500 | Failed to fetch timetable | Database or server error |
| 401 | Unauthorized | JWT token missing or invalid |

---

## Valid Day Values
- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

## Time Format
- 24-hour format: HH:MM
- Examples: 09:00, 14:30, 16:45

## Useful Tools for Testing
- **Postman**: https://www.postman.com/ (GUI REST client)
- **cURL**: Command line tool
- **Python Requests**: Python library
- **JavaScript Fetch**: Built-in browser API
