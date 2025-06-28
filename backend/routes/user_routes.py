from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from schemas.user_schema import UserSchema
from marshmallow import ValidationError

user_bp = Blueprint("user_bp", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

@user_bp.route("/users/", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        return jsonify({"users": users_schema.dump(users)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/users/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user = user_schema.load(data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"user": user_schema.dump(user)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
