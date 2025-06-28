from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.user import User

class UserSchema(SQLAlchemyAutoSchema):
    """Serialize User without exposing password_hash."""
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        ordered = True

    password_hash = auto_field(load_only=True)

user_schema   = UserSchema()
users_schema  = UserSchema(many=True)
