# smart_school_backend/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import validate_user, get_user_by_email, get_user_by_id, update_user_email, update_user_password

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["POST"])
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
        return jsonify({"error": "Invalid email or password"}), 401

    # Role verification (defense-in-depth)
    if user.get("role") != role:
        return jsonify({"error": "Incorrect role"}), 401

    # Generate token (identity = user email for consistency; we put id and role into additional claims)
    additional_claims = {"id": user["id"], "role": user["role"]}
    token = create_access_token(identity=user["email"], additional_claims=additional_claims)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user["role"],
        "id": user["id"],
        "email": user["email"]
    }), 200


# Get current user profile
@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }), 200


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
    
    try:
        update_user_password(user_id, new_password)
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Optional: a small ping endpoint to test token from front-end (not strictly required)
@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "auth service up"}), 200
