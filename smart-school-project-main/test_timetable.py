#!/usr/bin/env python3
"""
Test script for the timetable system.
This script tests:
1. Adding timetable entries (admin)
2. Retrieving student timetable
3. Retrieving teacher timetable
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
JWT_TOKEN = "your_jwt_token_here"  # Replace with actual JWT token

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def test_add_timetable():
    """Test adding timetable entries"""
    print("\n" + "="*60)
    print("TEST 1: Add Timetable Entries (Admin)")
    print("="*60)
    
    timetable_entries = [
        {
            "class_name": "10",
            "section": "A",
            "subject": "Math",
            "teacher_name": "Ratan",
            "day": "Monday",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "class_name": "10",
            "section": "A",
            "subject": "English",
            "teacher_name": "Priya",
            "day": "Monday",
            "start_time": "09:40",
            "end_time": "10:20"
        },
        {
            "class_name": "10",
            "section": "A",
            "subject": "Science",
            "teacher_name": "Kumar",
            "day": "Tuesday",
            "start_time": "09:00",
            "end_time": "09:40"
        },
        {
            "class_name": "10",
            "section": "B",
            "subject": "Math",
            "teacher_name": "Ratan",
            "day": "Monday",
            "start_time": "10:00",
            "end_time": "10:40"
        },
    ]
    
    for i, entry in enumerate(timetable_entries):
        try:
            response = requests.post(
                f"{BASE_URL}/api/timetable/add",
                headers=headers,
                json=entry
            )
            print(f"\nEntry {i+1}: {entry['class_name']}{entry['section']} - {entry['subject']} ({entry['day']})")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error adding entry {i+1}: {str(e)}")


def test_get_student_timetable():
    """Test retrieving student timetable"""
    print("\n" + "="*60)
    print("TEST 2: Get Student Timetable")
    print("="*60)
    
    # Assuming student ID 1 exists in class 10A
    student_id = 1
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/timetable/student/{student_id}/week",
            headers=headers
        )
        print(f"\nStudent ID: {student_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Student Name: {data.get('student_name')}")
            print(f"Class: {data.get('class_name')} Section: {data.get('section')}")
            print(f"\nTimetable ({len(data.get('timetable', []))} entries):")
            
            for entry in data.get('timetable', []):
                print(f"  {entry['day']:12} | {entry['subject']:15} | {entry['teacher_name']:15} | {entry['start_time']}-{entry['end_time']}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error retrieving student timetable: {str(e)}")


def test_get_teacher_timetable():
    """Test retrieving teacher timetable"""
    print("\n" + "="*60)
    print("TEST 3: Get Teacher Timetable")
    print("="*60)
    
    # Assuming teacher ID is 1 (name: Ratan)
    teacher_id = 1
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/timetable/teacher/{teacher_id}/week",
            headers=headers
        )
        print(f"\nTeacher ID: {teacher_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Teacher Name: {data.get('teacher_name')}")
            print(f"\nTimetable ({len(data.get('timetable', []))} entries):")
            
            for entry in data.get('timetable', []):
                print(f"  {entry['day']:12} | Class {entry['class_name']}{entry['section']:2} | {entry['subject']:15} | {entry['start_time']}-{entry['end_time']}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error retrieving teacher timetable: {str(e)}")


def test_get_class_timetable():
    """Test retrieving timetable by class"""
    print("\n" + "="*60)
    print("TEST 4: Get Class Timetable (Generic)")
    print("="*60)
    
    class_name = "10"
    section = "A"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/timetable/{class_name}/{section}",
            headers=headers
        )
        print(f"\nClass: {class_name}{section}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Timetable ({len(data.get('timetable', []))} entries):")
            
            for entry in data.get('timetable', []):
                print(f"  {entry['day']:12} | {entry['subject']:15} | {entry['teacher_name']:15} | {entry['start_time']}-{entry['end_time']}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error retrieving class timetable: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TIMETABLE SYSTEM TEST SUITE")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"JWT Token: {JWT_TOKEN[:20]}..." if JWT_TOKEN != "your_jwt_token_here" else "JWT Token: NOT SET!")
    
    if JWT_TOKEN == "your_jwt_token_here":
        print("\n⚠️  WARNING: Replace 'JWT_TOKEN' with an actual token before running!")
        print("Get your token by logging in through the API or admin dashboard.")
    else:
        try:
            test_add_timetable()
            test_get_class_timetable()
            test_get_student_timetable()
            test_get_teacher_timetable()
            
            print("\n" + "="*60)
            print("✅ All tests completed!")
            print("="*60)
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Cannot connect to the backend server.")
            print(f"Ensure the backend is running at {BASE_URL}")
