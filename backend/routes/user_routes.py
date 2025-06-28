from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from services.user_service import UserService
from schemas.user_schema import user_schema, users_schema

user_bp = Blueprint("user_bp", __name__)

# ---------- CREATE ----------
@user_bp.post("/users/")
def create_user():
    try:
        data = user_schema.load(request.get_json())
        user = UserService.create_user(**data)
        return jsonify({"user": user_schema.dump(user)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- READ ----------
@user_bp.get("/users/")
def list_users():
    users = UserService.list_users()
    return jsonify({"users": users_schema.dump(users)}), 200

@user_bp.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user_schema.dump(user)}), 200

# ---------- UPDATE ----------
@user_bp.put("/users/<int:user_id>")
def update_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    try:
        data = user_schema.load(request.get_json(), partial=True)  # partial = PATCH‑like
        user = UserService.update_user(user, **data)
        return jsonify({"user": user_schema.dump(user)}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- DELETE ----------
@user_bp.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    UserService.delete_user(user)
    return jsonify({}), 204

# ---------- DEACTIVATE ----------
@user_bp.post("/users/<int:user_id>/deactivate")
def deactivate_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user = UserService.deactivate_user(user)
    return jsonify({"user": user_schema.dump(user)}), 200