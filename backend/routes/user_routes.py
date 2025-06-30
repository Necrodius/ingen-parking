from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from marshmallow import ValidationError

from models.user import UserRole
from services.user_service import UserService
from schemas.user_schema import user_schema, users_schema
from utils.security import role_required

user_bp = Blueprint("user_bp", __name__)


# ---------------------------------------------------
# helpers
# ---------------------------------------------------
def _is_self(user_id: int) -> bool:
    """True if the request's JWT belongs to the same user_id."""
    try:
        return user_id == int(get_jwt_identity())
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------
# CREATE  (admin)
# ---------------------------------------------------
@user_bp.post("/")
@jwt_required()
@role_required(UserRole.admin)
def create_user():
    try:
        data = user_schema.load(request.get_json())
        user = UserService.create_user(**data)
        return jsonify({"user": user_schema.dump(user)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as dup:
        return jsonify({"error": str(dup)}), 409


# ---------------------------------------------------
# READ  (admin list • self/admin detail)
# ---------------------------------------------------
@user_bp.get("/")
@jwt_required()
@role_required(UserRole.admin)
def list_users():
    users = UserService.list_users()
    return jsonify({"users": users_schema.dump(users)}), 200

@user_bp.get("/me")
@jwt_required()
def get_me():
    """Return the authenticated user’s own record, or 404 if somehow missing."""
    me_id = int(get_jwt_identity())
    user  = UserService.get_user(me_id)
    if not user:                                 # ✅ null‑check prevents 422
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user_schema.dump(user)}), 200

@user_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id: int):
    if not (_is_self(user_id) or role_required("admin", silent=True)):
        return jsonify({"error": "Forbidden"}), 403

    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user_schema.dump(user)}), 200

# ---------------------------------------------------
# UPDATE  (self or admin)
# ---------------------------------------------------
@user_bp.put("/<int:user_id>")
@jwt_required()
def update_user(user_id: int):
    if not (_is_self(user_id) or role_required("admin", silent=True)):
        return jsonify({"error": "Forbidden"}), 403

    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        data = user_schema.load(request.get_json(), partial=True)
        user = UserService.update_user(user, **data)
        return jsonify({"user": user_schema.dump(user)}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as dup:
        return jsonify({"error": str(dup)}), 409


# ---------------------------------------------------
# DELETE & DEACTIVATE  (admin)
# ---------------------------------------------------
@user_bp.delete("/<int:user_id>")
@jwt_required()
@role_required(UserRole.admin)
def delete_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    UserService.delete_user(user)
    return jsonify({}), 204


@user_bp.post("/<int:user_id>/deactivate")
@jwt_required()
@role_required(UserRole.admin)
def deactivate_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user = UserService.deactivate_user(user)
    return jsonify({"user": user_schema.dump(user)}), 200


# ---------------------------------------------------
# CHANGE PASSWORD  (self only)
# ---------------------------------------------------
@user_bp.post("/<int:user_id>/change-password")
@jwt_required()
def change_password(user_id: int):
    """
    Expect JSON: { "old_password": "...", "new_password": "..." }
    Allows a user to change their own password after validating the old one.
    """
    if not _is_self(user_id):
        return jsonify({"error": "Forbidden"}), 403

    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    old_pw = data.get("old_password")
    new_pw = data.get("new_password")

    if not old_pw or not new_pw:
        return jsonify({"error": "Both old_password and new_password are required"}), 400

    try:
        UserService.change_password(user, old_pw, new_pw)
        return jsonify({"message": "Password updated successfully"}), 200
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
