# utils/jwt_manager.py
import jwt
import datetime
import os

# Load JWT secret from environment - fail if not set in production
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    import sys
    print("WARNING: JWT_SECRET_KEY environment variable not set. Using temporary key for development only.")
    SECRET_KEY = f"dev_temp_key_{datetime.datetime.now().strftime('%Y%m%d')}"

def create_access_token(identity):
    """
    Generate a JWT access token.
    The identity can be:
      - user id
      - dict containing user id + role
    """
    payload = {
        "identity": identity,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),  # token valid for 12 hours
        "iat": datetime.datetime.utcnow(),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_access_token(token):
    """
    Decode and return payload of JWT token.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"
