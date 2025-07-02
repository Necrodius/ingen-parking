# schemas/user_schema.py
# Marshmallow schema for User objects.

from marshmallow import Schema, fields, EXCLUDE
from models.user import UserRole


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE   # ignore extra attrs on input
        ordered = True      # keep field order on dump

    # ---------- READ‑ONLY ----------
    id         = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ---------- READ/WRITE ----------
    email      = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name  = fields.Str(required=True)

    role = fields.Function(
        serialize=lambda obj: obj.role.value,
        deserialize=lambda v: UserRole(v),
    )

    active = fields.Function(
        serialize=lambda obj: obj.active,
        deserialize=lambda v: bool(v),
    )

    # ---------- WRITE‑ONLY ----------
    password = fields.Str(load_only=True)


user_schema  = UserSchema()
users_schema = UserSchema(many=True)
