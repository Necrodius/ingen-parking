# This file defines the User model for the application, including user roles and account status.

from app import db 
from sqlalchemy import Enum
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(128), nullable=False)

    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
