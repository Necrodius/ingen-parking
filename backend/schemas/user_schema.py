# backend/schemas/user_schema.py
#
# A **minimal, safe** schema that never tries to serialise relationships
# or the password hash, so it will not raise ValidationError / 422.

from marshmallow import Schema, fields, EXCLUDE
from models.user import UserRole


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE        # ignore extra attributes
        ordered = True           # keep field order in dumps

    # ───────── read‑only ─────────
    id         = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ───────── common (dump + load) ─────────
    email      = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name  = fields.Str(required=True)

    # Enum → its value (“admin” | “user”)
    role       = fields.Function(lambda obj: obj.role.value,
                                 deserialize=lambda v: UserRole(v))

    # ───────── write‑only (accepted on load, never dumped) ─────────
    password   = fields.Str(load_only=True)

# shared singletons – import these everywhere else
user_schema  = UserSchema()
users_schema = UserSchema(many=True)
