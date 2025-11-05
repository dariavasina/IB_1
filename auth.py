import os
import datetime
import jwt
from functools import wraps
from flask import request, jsonify

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 86400  # 24 hours

def create_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401

        try:
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                return jsonify({"error": "Invalid token type"}), 401

            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = payload["user_id"]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)
    return decorated_function
