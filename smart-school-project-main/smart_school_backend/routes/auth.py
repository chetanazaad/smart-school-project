# smart_school_backend/routes/auth.py
import logging

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models.user import validate_user, get_user_by_email, get_user_by_id, update_user_email, update_user_password, validate_password_strength
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.jwt_blacklist import add_to_blacklist
try:
    from utils.db import get_db
except ImportError:
    from smart_school_backend.utils.db import get_db

bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

# Initialize limiter for this blueprint
limiter = Limiter(key_func=get_remote_address)

@bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Stricter rate limit for login: 5 attempts per minute
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not email or not password or not role:
        return jsonify({"error": "Missing fields"}), 400

    # Try fast password validation (validate_user will check hash)
    user = validate_user(email, password)

    # If validate_user returns None, user not found or invalid password
    if not user:
        # give a consistent message without leaking which part failed
        logger.warning("Login failed for email")
        return jsonify({"error": "Invalid email or password"}), 401

    # Role verification (defense-in-depth)
    if user.get("role") != role:
        return jsonify({"error": "Incorrect role"}), 401

    # Fetch profile details based on role
    profile_id = user["id"]
    profile_data = {}
    
    db = get_db()
    cur = db.cursor()
    
    if user["role"] == "teacher":
        cur.execute("SELECT id, is_class_teacher, assigned_class, assigned_section FROM teachers WHERE email=?", (email,))
        t = cur.fetchone()
        if t:
            profile_id = t["id"]
            profile_data = {
                "is_class_teacher": bool(t["is_class_teacher"]),
                "assigned_class": t["assigned_class"],
                "assigned_section": t["assigned_section"]
            }
    elif user["role"] == "student":
        cur.execute("SELECT id, class_name, section FROM students WHERE email=?", (email,))
        s = cur.fetchone()
        if s:
            profile_id = s["id"]
            profile_data = {
                "class_name": s["class_name"],
                "section": s["section"]
            }

    # Generate token (identity = user email for consistency)
    additional_claims = {"id": user["id"], "role": user["role"], "profile_id": profile_id}
    token = create_access_token(identity=user["email"], additional_claims=additional_claims)

    logger.info(f"Login successful for {email} as {user['role']}")
    response_data = {
        "message": "Login successful",
        "token": token,
        "role": user["role"],
        "id": profile_id,   # We return profile_id as 'id' for frontend convenience
        "user_id": user["id"], # Keep original user_id
        "email": user["email"],
        "name": user["name"]
    }
    response_data.update(profile_data)
    
    return jsonify(response_data), 200


# Get current user profile
@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Fetch profile details
    profile_id = user["id"]
    profile_data = {}
    
    db = get_db()
    cur = db.cursor()
    
    if user["role"] == "teacher":
        cur.execute("SELECT id, is_class_teacher, assigned_class, assigned_section FROM teachers WHERE email=?", (email,))
        t = cur.fetchone()
        if t:
            profile_id = t["id"]
            profile_data = {
                "is_class_teacher": bool(t["is_class_teacher"]),
                "assigned_class": t["assigned_class"],
                "assigned_section": t["assigned_section"]
            }
    elif user["role"] == "student":
        cur.execute("SELECT id, class_name, section FROM students WHERE email=?", (email,))
        s = cur.fetchone()
        if s:
            profile_id = s["id"]
            profile_data = {
                "class_name": s["class_name"],
                "section": s["section"]
            }

    response_data = {
        "id": profile_id,
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }
    response_data.update(profile_data)
    
    return jsonify(response_data), 200


# Update email
@bp.route("/update-email", methods=["POST"])
@jwt_required()
def update_email():
    current_email = get_jwt_identity()
    user = get_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_id = user["id"]
    
    data = request.get_json() or {}
    
    new_email = data.get("new_email")
    if not new_email:
        return jsonify({"error": "New email is required"}), 400
    
    # Check if email already exists
    existing_user = get_user_by_email(new_email)
    if existing_user and existing_user["id"] != user_id:
        return jsonify({"error": "Email already in use"}), 400
    
    try:
        update_user_email(user_id, new_email)
        return jsonify({"message": "Email updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update password
@bp.route("/update-password", methods=["POST"])
@jwt_required()
def update_password():
    current_email = get_jwt_identity()
    user = get_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_id = user["id"]
    
    data = request.get_json() or {}
    
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    
    if not current_password or not new_password:
        return jsonify({"error": "Both current and new password are required"}), 400
    
    # Verify current password
    validated = validate_user(user["email"], current_password)
    if not validated:
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Validate new password strength
    is_valid, error_message = validate_password_strength(new_password)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    try:
        update_user_password(user_id, new_password)
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Logout endpoint - blacklist the current token
@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout by blacklisting the current JWT token.
    The token will no longer be valid for future requests.
    """
    jti = get_jwt().get("jti")
    if jti:
        add_to_blacklist(jti)
        logger.info(f"User logged out, token blacklisted: {jti}")
        return jsonify({"message": "Logged out successfully"}), 200
    
    return jsonify({"error": "Invalid token"}), 400


# Optional: a small ping endpoint to test token from front-end (not strictly required)
@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "auth service up"}), 200
