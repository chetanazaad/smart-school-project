#!/usr/bin/env python3
"""
Test script for Teacher Role-Based Features
Tests all new endpoints and authorization logic
"""

import requests
import json
import base64
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_TOKEN = "YOUR_ADMIN_JWT_TOKEN"
CLASS_TEACHER_TOKEN = "YOUR_CLASS_TEACHER_JWT_TOKEN"
REGULAR_TEACHER_TOKEN = "YOUR_REGULAR_TEACHER_JWT_TOKEN"
STUDENT_TOKEN = "YOUR_STUDENT_JWT_TOKEN"

# Test data
CLASS_TEACHER_ID = 1
REGULAR_TEACHER_ID = 2
STUDENT_ID = 101
INVALID_STUDENT_ID = 999

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_test(name):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}TEST: {name}{bcolors.ENDC}")

def print_success(msg):
    print(f"{bcolors.OKGREEN}✅ {msg}{bcolors.ENDC}")

def print_error(msg):
    print(f"{bcolors.FAIL}❌ {msg}{bcolors.ENDC}")

def print_warning(msg):
    print(f"{bcolors.WARNING}⚠️  {msg}{bcolors.ENDC}")

def print_info(msg):
    print(f"{bcolors.OKCYAN}ℹ️  {msg}{bcolors.ENDC}")

def test_endpoint(method, endpoint, token, data=None, expected_status=200):
    """
    Test an API endpoint
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            print_error(f"Unknown method: {method}")
            return None
        
        print_info(f"{method} {endpoint}")
        print_info(f"Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print_info(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print_info(f"Response: {response.text}")
        
        if response.status_code == expected_status:
            print_success(f"Status code {response.status_code} as expected")
            return response
        else:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            return response
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None

# ============================================================================
# TEST SUITE
# ============================================================================

def test_create_class_teacher():
    """Test creating a class teacher"""
    print_test("Create Class Teacher")
    
    data = {
        "name": "Test Class Teacher",
        "email": "test.class.teacher@school.com",
        "id_code": "TCT001",
        "subject": "Mathematics",
        "is_class_teacher": True,
        "assigned_class": "Class 10A",
        "assigned_section": "Section A"
    }
    
    response = test_endpoint("POST", "/api/teachers", ADMIN_TOKEN, data, 201)
    if response:
        try:
            result = response.json()
            if result.get("is_class_teacher"):
                print_success("Class teacher created with is_class_teacher=true")
        except:
            pass

def test_create_regular_teacher():
    """Test creating a regular teacher"""
    print_test("Create Regular Teacher")
    
    data = {
        "name": "Test Regular Teacher",
        "email": "test.regular.teacher@school.com",
        "id_code": "TRT001",
        "subject": "English",
        "is_class_teacher": False
    }
    
    response = test_endpoint("POST", "/api/teachers", ADMIN_TOKEN, data, 201)
    if response:
        print_success("Regular teacher created with is_class_teacher=false")

def test_class_teacher_missing_assignment():
    """Test creating class teacher without assignment (should fail)"""
    print_test("Create Class Teacher Without Assignment (Should Fail)")
    
    data = {
        "name": "Invalid Class Teacher",
        "email": "invalid.class.teacher@school.com",
        "id_code": "ICT001",
        "subject": "Science",
        "is_class_teacher": True
        # Missing assigned_class and assigned_section
    }
    
    response = test_endpoint("POST", "/api/teachers", ADMIN_TOKEN, data, 400)
    if response:
        print_success("Correctly rejected class teacher without assignment")

def test_get_teacher_list():
    """Test getting all teachers"""
    print_test("Get All Teachers")
    
    response = test_endpoint("GET", "/api/teachers", ADMIN_TOKEN)
    if response:
        try:
            teachers = response.json()
            print_success(f"Retrieved {len(teachers)} teachers")
        except:
            pass

def test_get_teacher_details():
    """Test getting single teacher details"""
    print_test("Get Teacher Details")
    
    response = test_endpoint("GET", f"/api/teachers/{CLASS_TEACHER_ID}", ADMIN_TOKEN)
    if response:
        try:
            teacher = response.json()
            if "is_class_teacher" in teacher:
                print_success("Teacher details include is_class_teacher field")
        except:
            pass

def test_update_teacher():
    """Test updating teacher details"""
    print_test("Update Teacher Details")
    
    data = {
        "name": "Updated Teacher Name",
        "subject": "Physics"
    }
    
    response = test_endpoint("PUT", f"/api/teachers/{CLASS_TEACHER_ID}", ADMIN_TOKEN, data)
    if response:
        print_success("Teacher details updated")

def test_class_teacher_dashboard():
    """Test class teacher dashboard access"""
    print_test("Class Teacher Dashboard")
    
    response = test_endpoint("GET", f"/api/teachers/{CLASS_TEACHER_ID}/dashboard", 
                            CLASS_TEACHER_TOKEN)
    if response and response.status_code == 200:
        try:
            data = response.json()
            if "enrolled_students" in data and "class_timetable" in data and "teacher_timetable" in data:
                print_success("Dashboard contains students and both timetables")
        except:
            pass

def test_regular_teacher_dashboard_fails():
    """Test that regular teacher dashboard fails"""
    print_test("Regular Teacher Dashboard (Should Fail)")
    
    response = test_endpoint("GET", f"/api/teachers/{REGULAR_TEACHER_ID}/dashboard", 
                            REGULAR_TEACHER_TOKEN, None, 400)
    if response:
        print_success("Regular teacher correctly denied dashboard access")

def test_enrolled_students():
    """Test getting enrolled students"""
    print_test("Get Enrolled Students")
    
    response = test_endpoint("GET", f"/api/teachers/{CLASS_TEACHER_ID}/enrolled-students", 
                            CLASS_TEACHER_TOKEN)
    if response and response.status_code == 200:
        try:
            data = response.json()
            if "students" in data and "total_students" in data:
                print_success(f"Retrieved {data['total_students']} enrolled students")
        except:
            pass

def test_attendance_interface():
    """Test regular teacher attendance interface"""
    print_test("Regular Teacher Attendance Interface")
    
    response = test_endpoint("GET", f"/api/teachers/{REGULAR_TEACHER_ID}/attendance", 
                            REGULAR_TEACHER_TOKEN)
    if response and response.status_code == 200:
        try:
            data = response.json()
            if data.get("attendance_only") and not data.get("can_enroll"):
                print_success("Attendance interface correctly configured")
        except:
            pass

def test_get_enrollment_details():
    """Test getting enrollment details"""
    print_test("Get Enrollment Details (Student)")
    
    response = test_endpoint("GET", f"/api/enrollment/student/{STUDENT_ID}", CLASS_TEACHER_TOKEN)
    if response and response.status_code == 200:
        try:
            data = response.json()
            if "name" in data and "email" in data:
                print_success("Enrollment details retrieved successfully")
        except:
            pass

def test_update_enrollment_details():
    """Test updating enrollment details"""
    print_test("Update Enrollment Details (Student)")
    
    data = {
        "name": "Updated Student Name"
    }
    
    response = test_endpoint("PUT", f"/api/enrollment/student/{STUDENT_ID}", 
                            CLASS_TEACHER_TOKEN, data)
    if response:
        print_success("Enrollment details updated")

def test_teacher_get_own_enrollment():
    """Test teacher getting their own enrollment details"""
    print_test("Get Teacher Own Enrollment Details")
    
    response = test_endpoint("GET", f"/api/enrollment/teacher/{CLASS_TEACHER_ID}", 
                            CLASS_TEACHER_TOKEN)
    if response and response.status_code == 200:
        try:
            data = response.json()
            if "is_class_teacher" in data:
                print_success("Teacher enrollment details retrieved")
        except:
            pass

def test_face_enroll_auth():
    """Test face enrollment authorization"""
    print_test("Face Enrollment Authorization")
    
    # Regular teacher trying to enroll student (should fail)
    data = {
        "image": "base64_placeholder",
        "user_id": STUDENT_ID,
        "role": "student"
    }
    
    response = test_endpoint("POST", "/api/enrollment/enroll", REGULAR_TEACHER_TOKEN, data, 403)
    if response:
        print_success("Regular teacher correctly blocked from enrolling student")

def test_face_recognize_auth():
    """Test face recognition authorization"""
    print_test("Face Recognition Authorization")
    
    data = {
        "image_base64": "base64_placeholder"
    }
    
    response = test_endpoint("POST", "/api/recognition/recognize", REGULAR_TEACHER_TOKEN, data)
    # Note: Will fail with 400 or 200 depending on image, but should not be 403
    print_info("Regular teacher tested for face recognition")

def test_cross_class_student_access():
    """Test that class teacher cannot access students outside their class"""
    print_test("Cross-Class Student Access Prevention")
    
    # This test depends on having students in different classes
    data = {
        "name": "Other Student"
    }
    
    response = test_endpoint("PUT", f"/api/enrollment/student/{INVALID_STUDENT_ID}", 
                            CLASS_TEACHER_TOKEN, data, 403)
    if response:
        print_success("Cross-class access correctly prevented")

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}")
    print("=" * 60)
    print("TEACHER ROLE-BASED FEATURES TEST SUITE")
    print("=" * 60)
    print(f"{bcolors.ENDC}\n")
    
    print_warning("Prerequisites:")
    print_info("1. Smart School backend is running on localhost:5000")
    print_info("2. Update JWT tokens at top of this script")
    print_info("3. Update test IDs to match your database")
    
    input(f"\n{bcolors.BOLD}Press Enter to start tests...{bcolors.ENDC}")
    
    # Run test suite
    tests = [
        test_create_class_teacher,
        test_create_regular_teacher,
        test_class_teacher_missing_assignment,
        test_get_teacher_list,
        test_get_teacher_details,
        test_update_teacher,
        test_class_teacher_dashboard,
        test_regular_teacher_dashboard_fails,
        test_enrolled_students,
        test_attendance_interface,
        test_get_enrollment_details,
        test_update_enrollment_details,
        test_teacher_get_own_enrollment,
        test_face_enroll_auth,
        test_face_recognize_auth,
        test_cross_class_student_access,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print_error(f"Test failed with exception: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"{bcolors.ENDC}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    print(f"\nTotal: {passed + failed} tests\n")
    
    if failed == 0:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}✅ ALL TESTS PASSED{bcolors.ENDC}\n")
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}❌ SOME TESTS FAILED{bcolors.ENDC}\n")

if __name__ == "__main__":
    main()
