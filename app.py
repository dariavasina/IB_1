import os
import re
import dotenv
from flask import Flask, request, jsonify, session
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

import db
import auth


dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.teardown_appcontext(db.close_db)
with app.app_context():
    db.init_db()


def validate_login_password(login, password):
    if not isinstance(login, str) or not isinstance(password, str):
        return False, "Login and password must be strings"
    if len(login) < 3 or len(login) > 50:
        return False, "Login must be between 3 and 50 characters"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.fullmatch(r"[A-Za-z0-9_]+", login):
        return False, "Login can contain only letters, digits, and underscores"
    return True, ""


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    is_valid, error_msg = validate_login_password(login, password)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    if db.create_user(login, generate_password_hash(password)):
        return jsonify({"message": "User registered successfully"}), 201

    return jsonify({"error": f"User {escape(login)} already exists"}), 400


@app.route("/auth/login", methods=["POST"])
def login_user():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    is_valid, error_msg = validate_login_password(login, password)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    user = db.get_user_by_login(login)
    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        token = auth.create_jwt(user["id"])
        return jsonify({"message": "Login successful", "token": token}), 200

    return jsonify({"error": "Invalid login or password"}), 401


@app.route("/api/data", methods=["GET"])
@auth.jwt_required
def get_data():
    users_list = db.get_all_users()
    return jsonify(users_list)


if __name__ == "__main__":
    app.run(debug=False)