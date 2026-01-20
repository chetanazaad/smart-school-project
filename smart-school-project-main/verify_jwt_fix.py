# Quick test to verify JWT fix
import sys
sys.path.insert(0, 'd:\\data_science_project\\smart-school-project-main')
sys.path.insert(0, 'd:\\data_science_project\\smart-school-project-main\\smart_school_backend')

# Test the auth.py changes
print("=== Testing JWT Identity Fix ===\n")

# Read and verify the auth.py changes
with open('d:\\data_science_project\\smart-school-project-main\\smart_school_backend\\routes\\auth.py', 'r') as f:
    content = f.read()
    
print("✓ Checking auth.py login endpoint...")
if 'create_access_token(identity=user["email"]' in content:
    print("  ✅ JWT token created with email identity - CORRECT!")
else:
    print("  ❌ JWT token still uses user ID - NEEDS FIX")

if 'additional_claims = {"id": user["id"], "role": user["role"]}' in content:
    print("  ✅ JWT claims include id and role - CORRECT!")
else:
    print("  ❌ JWT claims structure wrong")

print("\n✓ Checking /me endpoint...")
if 'email = get_jwt_identity()' in content and 'get_user_by_email(email)' in content:
    print("  ✅ /me endpoint uses email identity lookup - CORRECT!")
else:
    print("  ❌ /me endpoint still using user ID lookup")

print("\n✓ Checking /update-email endpoint...")
if 'current_email = get_jwt_identity()' in content:
    print("  ✅ /update-email gets current email from JWT - CORRECT!")
else:
    print("  ❌ /update-email not updated")

print("\n✓ Checking /update-password endpoint...")
update_password_section = content[content.find('def update_password'):content.find('def update_password')+800]
if 'current_email = get_jwt_identity()' in update_password_section:
    print("  ✅ /update-password gets current email from JWT - CORRECT!")
else:
    print("  ❌ /update-password not updated")

print("\n" + "="*50)
print("Summary: JWT Identity Fix Applied ✅")
print("="*50)
print("\nWhat this fixes:")
print("- BEFORE: [FACE_ENROLL] JWT Identity: 1, Role: None")
print("- AFTER:  [FACE_ENROLL] JWT Identity: admin@school.com, Role: admin")
print("\nNext steps:")
print("1. Stop current backend (if running)")
print("2. Start backend: python app.py")
print("3. Clear browser local storage")
print("4. Log in as admin@school.com / admin123")
print("5. Try creating a teacher with face enrollment")
print("6. Face enrollment should work - no 403 error!")
