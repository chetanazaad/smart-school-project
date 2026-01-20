from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
import os
import sys

# ============================================================
# 1. FIX PYTHON PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # smart_school_backend/
ROOT_DIR = os.path.dirname(BASE_DIR)                    # project root

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ============================================================
# 2. DB CLOSE HANDLER
# ============================================================
try:
    from smart_school_backend.utils.db import close_db
except ImportError:
    from utils.db import close_db

# ============================================================
# 3. FLASK CONFIG
# ============================================================
app = Flask(__name__)

app.config["SECRET_KEY"] = "SMART_SCHOOL_SECRET_KEY"
app.config["JWT_SECRET_KEY"] = "SMART_SCHOOL_JWT_SECRET"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["JSON_SORT_KEYS"] = False

# ============================================================
# 4. INITIALIZE DB TABLES (CRITICAL)
# ============================================================
from smart_school_backend.database.init_db import init_db
with app.app_context():
    init_db()

# ============================================================
# 5. SAFE ROUTE IMPORTER
# ============================================================
def safe_import_route(primary, fallback, obj):
    try:
        mod = __import__(primary, fromlist=[obj])
        return getattr(mod, obj)
    except ImportError:
        mod = __import__(fallback, fromlist=[obj])
        return getattr(mod, obj)

# ============================================================
# 6. CORE ROUTES
# ============================================================
auth_bp = safe_import_route("smart_school_backend.routes.auth", "routes.auth", "bp")
students_bp = safe_import_route("smart_school_backend.routes.students", "routes.students", "bp")
teachers_bp = safe_import_route("smart_school_backend.routes.teachers", "routes.teachers", "bp")
parents_bp = safe_import_route("smart_school_backend.routes.parents", "routes.parents", "bp")

attendance_bp = safe_import_route("smart_school_backend.routes.attendance", "routes.attendance", "bp")
attendance_view_bp = safe_import_route("smart_school_backend.routes.attendance", "routes.attendance", "attendance_view_bp")

student_attendance_bp = safe_import_route(
    "smart_school_backend.routes.student_attendance",
    "routes.student_attendance",
    "student_attendance_bp",
)

teacher_attendance_bp = safe_import_route(
    "smart_school_backend.routes.teacher_attendance",
    "routes.teacher_attendance",
    "bp",
)

# ============================================================
# 7. FACE SYSTEM (UNIFIED)
# ============================================================
face_recognition_bp = safe_import_route(
    "smart_school_backend.routes.face_recognition",
    "routes.face_recognition",
    "face_recognition_bp",
)

from smart_school_backend.routes.enrollment import enrollment_bp
from smart_school_backend.routes.recognition import recognition_bp

# ============================================================
# 8. AUTO / REALTIME ATTENDANCE
# ============================================================
automatic_attendance_bp = safe_import_route(
    "smart_school_backend.routes.automatic_attendance",
    "routes.automatic_attendance",
    "bp",
)

realtime_attendance_bp = safe_import_route(
    "smart_school_backend.routes.realtime_attendance",
    "routes.realtime_attendance",
    "bp",
)

# ============================================================
# 9. OPTIONAL MODULES
# ============================================================
timetable_bp = safe_import_route("smart_school_backend.routes.timetable", "routes.timetable", "bp")
chatbot_bp = safe_import_route("smart_school_backend.routes.chatbot", "routes.chatbot", "chatbot_bp")

# ============================================================
# 10. JWT SETUP
# ============================================================
jwt = JWTManager(app)

# ============================================================
# 11. CORS CONFIG
# ============================================================
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "supports_credentials": True,
        }
    },
)

# ============================================================
# 12. REGISTER BLUEPRINTS
# ============================================================
app.register_blueprint(auth_bp, url_prefix="/api/auth")

app.register_blueprint(students_bp, url_prefix="/api/students")
app.register_blueprint(teachers_bp, url_prefix="/api/teachers")
app.register_blueprint(parents_bp, url_prefix="/api/parents")

app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
app.register_blueprint(attendance_view_bp, url_prefix="/api/attendance-view")

app.register_blueprint(student_attendance_bp, url_prefix="/api/student-attendance")
app.register_blueprint(teacher_attendance_bp, url_prefix="/api/teacher-attendance")

app.register_blueprint(face_recognition_bp, url_prefix="/api/face-recognition")

# Unified Face APIs
app.register_blueprint(enrollment_bp, url_prefix="/api/face")
app.register_blueprint(recognition_bp, url_prefix="/api/face")

# Auto systems
app.register_blueprint(automatic_attendance_bp, url_prefix="/api/auto-attendance")
app.register_blueprint(realtime_attendance_bp, url_prefix="/api/realtime-attendance")

# Optional
app.register_blueprint(timetable_bp, url_prefix="/api/timetable")
app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

# ============================================================
# 13. HEALTH CHECK
# ============================================================
@app.route("/")
def home():
    return {
        "status": "running",
        "message": "Smart School Backend Running"
    }, 200

# ============================================================
# 14. AUTH DEBUG
# ============================================================
@app.route("/api/auth/me")
@jwt_required()
def get_me():
    return {
        "identity": get_jwt_identity(),
        "claims": get_jwt(),
    }, 200

# ============================================================
# 15. CLOSE DB CONNECTION
# ============================================================
app.teardown_appcontext(close_db)

# ============================================================
# 16. GLOBAL ERROR HANDLERS
# ============================================================
@app.errorhandler(Exception)
def handle_error(error):
    """Catch all unhandled errors"""
    import traceback
    print(f"❌ ERROR: {str(error)}")
    print(traceback.format_exc())
    return {
        "error": "Internal server error",
        "message": str(error)
    }, 500

@app.errorhandler(404)
def handle_404(error):
    """Handle route not found"""
    return {
        "error": "Route not found",
        "message": str(error)
    }, 404

# ============================================================
# 17. RUN SERVER
# ============================================================
if __name__ == "__main__":
    # Use debug=False in production, True for development
    # Set use_reloader=False to prevent constant restarts
    app.run(debug=False, use_reloader=False, host="127.0.0.1", port=5000)
