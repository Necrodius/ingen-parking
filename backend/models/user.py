# This file defines the User model for the application.

from app import db
from .mixins import TimestampMixin
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), nullable=False, unique=True, index=True)

    password_hash = db.Column(db.String(128), nullable=False)

    first_name = db.Column(db.String(120), nullable=False)
    
    last_name = db.Column(db.String(120), nullable=False)

    role = db.Column(
        db.Enum(UserRole), nullable=False, default=UserRole.USER
    )
    
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    reservations = db.relationship(
        "Reservation", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
