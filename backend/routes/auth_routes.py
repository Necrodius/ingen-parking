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
        # Validate request JSON using Marshmallow
        data = register_schema.load(request.get_json())

        # Call AuthService to register user
        user = AuthService.register_user(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        # Return basic info after registration
        return jsonify({
            "id": user.id,
            "email": user.email
        }), 201

    except ValidationError as err:
        # Schema validation error (missing/invalid fields)
        return jsonify({"errors": err.messages}), 400

    except ValueError as dup:
        # Duplicate email or other registration issues
        return jsonify({"error": str(dup)}), 409

# ---------- LOGIN ----------
@auth_bp.post("/login")
def login_user():
    try:
        # Validate request using Marshmallow
        data = login_schema.load(request.get_json())

        # Attempt login via AuthService
        user = AuthService.authenticate(
            email=data["email"],
            password=data["password"]
        )
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Create JWT with identity and role
        jwt_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role.value},
        )

        return jsonify({"access_token": jwt_token}), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
