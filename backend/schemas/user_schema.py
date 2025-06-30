# This file defines the schema for user data serialization and deserialization using Marshmallow.
# It includes fields for user attributes, handling of unknown fields, and read/write properties.

from marshmallow import Schema, fields, EXCLUDE
from models.user import UserRole


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE        # ignore extra attributes
        ordered = True           # keep field order in dumps

    # ---------- READ-ONLY ----------
    id         = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    email      = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name  = fields.Str(required=True)

    role       = fields.Function(lambda obj: obj.role.value,
                                 deserialize=lambda v: UserRole(v))
    
    # ---------- WRITE-ONLY ----------
    password   = fields.Str(load_only=True)

user_schema  = UserSchema()
users_schema = UserSchema(many=True)
