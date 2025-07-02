from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from services.auth_service import AuthService
from schemas.login_schema import login_schema
from schemas.register_schema import register_schema

auth_bp = Blueprint("auth_bp", __name__)

# ---------- REGISTER ----------
@auth_bp.post("/register")
def register_user():
    try:
        data = register_schema.load(request.get_json())

        user = AuthService.register_user(
            email       = data["email"],
            password    = data["password"],
            first_name  = data["first_name"],
            last_name   = data["last_name"],
        )
        return jsonify({"id": user.id, "email": user.email}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except ValueError as dup:
        return jsonify({"error": str(dup)}), 409

# ---------- LOGIN ----------
@auth_bp.post("/login")
def login_user():
    try:
        data = login_schema.load(request.get_json())

        # Authenticate email/password
        user = AuthService.authenticate(
            email    = data["email"],
            password = data["password"]
        )
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Block deactivated accounts
        if not user.active:
            return jsonify({"error": "Account disabled. Contact an administrator."}), 403

        # Issue JWT
        jwt_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role.value},
        )
        return jsonify({"access_token": jwt_token}), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
