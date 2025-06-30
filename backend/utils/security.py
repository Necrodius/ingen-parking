# This file contains utility functions for security-related tasks such as password hashing, JWT role verification, and email normalization.
# It uses bcrypt for password hashing and Flask-JWT-Extended for JWT handling.

import bcrypt
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from models.user import UserRole

def role_required(role: UserRole):
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != role.value:
                return jsonify({"error": "Forbidden"}), 403
            return fn(*args, **kwargs)
        return inner
    return wrapper

def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(raw: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))

def normalize_email(email: str) -> str:
    return email.strip().lower()
