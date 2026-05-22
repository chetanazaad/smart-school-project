import subprocess
import sys
import os
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
import logging
from dotenv import load_dotenv

# ============================================================
# MINIMIZE LOGGING OUTPUT
# ============================================================
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)
logging.getLogger('tensorflow').setLevel(logging.CRITICAL)
logging.getLogger('tensorflow.python').setLevel(logging.CRITICAL)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow C++ logs

# Suppress face_recognition_models warning
import warnings
warnings.filterwarnings('ignore', message='.*face_recognition_models.*')

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
# 2. REQUEST ID TRACKING (must be before other imports)
# ============================================================
try:
    from utils.request_id import init_request_id
except ImportError:
    from smart_school_backend.utils.request_id import init_request_id

# ============================================================
# 3. DB CLOSE HANDLER
# ============================================================
try:
    from utils.db import close_db
except ImportError:
    from smart_school_backend.utils.db import close_db

# ============================================================
# 4. FLASK CONFIG
# ============================================================
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Database URI configuration
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "smart_school.db")
os.makedirs(DB_DIR, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Setup Flask-Migrate
try:
    from models import *
except ImportError:
    from smart_school_backend.models import *

db = None
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
except ImportError:
    pass

# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[os.getenv("RATE_LIMIT", "100/hour")],
)
limiter.init_app(app)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_jwt_secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["JSON_SORT_KEYS"] = False

# ============================================================
# 5. INITIALIZE DB TABLES (CRITICAL)
# ============================================================
try:
    from database.init_db import init_db
except ImportError:
    from smart_school_backend.database.init_db import init_db

with app.app_context():
    # Use fresh=False to preserve existing data (students, teachers, attendance, face embeddings)
    # Set fresh=True only when you want to reset the entire database
    init_db(fresh=False)

# ============================================================
# FACE EMBEDDINGS PRESERVED - NO LONGER CLEARED ON STARTUP
# ============================================================
# Note: Face embeddings are now preserved across server restarts
# to maintain enrolled faces between deployments.

# ============================================================
# 6. SAFE ROUTE IMPORTER
# ============================================================
def safe_import_route(primary, fallback, obj):
    try:
        mod = __import__(primary, fromlist=[obj])
        return getattr(mod, obj)
    except ImportError:
        mod = __import__(fallback, fromlist=[obj])
        return getattr(mod, obj)

# ============================================================
# 7. CORE ROUTES
# ============================================================
auth_bp = safe_import_route("routes.auth", "smart_school_backend.routes.auth", "bp")
students_bp = safe_import_route("routes.students", "smart_school_backend.routes.students", "bp")
teachers_bp = safe_import_route("routes.teachers", "smart_school_backend.routes.teachers", "bp")
parents_bp = safe_import_route("routes.parents", "smart_school_backend.routes.parents", "bp")
users_bp = safe_import_route("routes.users", "smart_school_backend.routes.users", "bp")

attendance_bp = safe_import_route("routes.attendance", "smart_school_backend.routes.attendance", "bp")
attendance_view_bp = safe_import_route("routes.attendance", "smart_school_backend.routes.attendance", "attendance_view_bp")

student_attendance_bp = safe_import_route(
    "routes.student_attendance",
    "smart_school_backend.routes.student_attendance",
    "student_attendance_bp",
)

teacher_attendance_bp = safe_import_route(
    "routes.teacher_attendance",
    "smart_school_backend.routes.teacher_attendance",
    "bp",
)

try:
    from routes.enrollment import enrollment_bp
except ImportError:
    from smart_school_backend.routes.enrollment import enrollment_bp

try:
    from routes.recognition import recognition_bp
except ImportError:
    from smart_school_backend.routes.recognition import recognition_bp

try:
    from routes.face import face_bp
except ImportError:
    from smart_school_backend.routes.face import face_bp

# ============================================================
# 8. AUTO / REALTIME ATTENDANCE
# ============================================================
automatic_attendance_bp = safe_import_route(
    "routes.automatic_attendance",
    "smart_school_backend.routes.automatic_attendance",
    "bp",
)

realtime_attendance_bp = safe_import_route(
    "routes.realtime_attendance",
    "smart_school_backend.routes.realtime_attendance",
    "bp",
)

# ============================================================
# 9. OPTIONAL MODULES
# ============================================================
timetable_bp = safe_import_route("routes.timetable", "smart_school_backend.routes.timetable", "bp")

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
            "origins": os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(","),
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "supports_credentials": True,
        }
    },
)

# ============================================================
# 12. REGISTER BLUEPRINTS (API v1)
# ============================================================
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

app.register_blueprint(students_bp, url_prefix="/api/v1/students")
app.register_blueprint(teachers_bp, url_prefix="/api/v1/teachers")
app.register_blueprint(parents_bp, url_prefix="/api/v1/parents")
app.register_blueprint(users_bp, url_prefix="/api/v1/users")

app.register_blueprint(attendance_bp, url_prefix="/api/v1/attendance")
app.register_blueprint(attendance_view_bp, url_prefix="/api/v1/attendance-view")
app.register_blueprint(student_attendance_bp, url_prefix="/api/v1/student-attendance")
app.register_blueprint(teacher_attendance_bp, url_prefix="/api/v1/teacher-attendance")
app.register_blueprint(realtime_attendance_bp, url_prefix="/api/v1/realtime-attendance")

# Unified Face APIs - Enabled
app.register_blueprint(enrollment_bp, url_prefix="/api/v1/enrollment")
app.register_blueprint(recognition_bp, url_prefix="/api/v1/recognition")
app.register_blueprint(face_bp, url_prefix="/api/v1/face")

# Auto systems
app.register_blueprint(automatic_attendance_bp, url_prefix="/api/v1/auto-attendance")

# Optional
app.register_blueprint(timetable_bp, url_prefix="/api/v1/timetable")

# ============================================================
# 13. HEALTH CHECK
# ============================================================
@app.route("/")
def home():
    return {
        "status": "running",
        "message": "Smart School Backend Running",
        "api_version": "v1",
        "api_prefix": "/api/v1"
    }, 200

# ============================================================
# 14. AUTH DEBUG
# ============================================================
@app.route("/api/v1/auth/me")
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
    # Log the error properly with full traceback at ERROR level
    logging.error(f"Unhandled error: {str(error)}\n{traceback.format_exc()}")
    # Return generic message to avoid exposing internal details
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }, 500

@app.errorhandler(404)
def handle_404(error):
    """Handle route not found"""
    return {
        "error": "Route not found",
        "message": str(error)
    }, 404

# ============================================================
# 17. REQUEST ID TRACKING
# ============================================================
init_request_id(app)

# ============================================================
# 18. RUN SERVER
# ============================================================
if __name__ == "__main__":
    print("[*] Starting Smart School Backend...")
    print(f"[*] Project Root: {ROOT_DIR}")
    print(f"[*] Database: {DB_PATH}")
    print(f"[*] Running on http://127.0.0.1:5000")
    print(f"[*] Press CTRL+C to stop")
    # Use threaded mode, no debug reload (debug=True causes issues on Windows)
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False, threaded=True)
