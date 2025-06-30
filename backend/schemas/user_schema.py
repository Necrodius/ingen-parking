# This file defines the UserSchema for serializing and deserializing User objects using Marshmallow.
# It includes fields for both read-only and write operations, ensuring that sensitive information like password hashes is handled appropriately.
# It also uses SQLAlchemyAutoSchema to automatically generate fields based on the User model.

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.user import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        ordered = True

    # ---------- READ-ONLY ----------
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ---------- WRITE ----------
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password = fields.Str(load_only=True)  # write-only (input only)
    role = fields.Str()

    # ---------- HIDDEN ----------
    password_hash = fields.Str(load_only=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
