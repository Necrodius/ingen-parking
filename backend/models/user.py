# This file defines the User model for the application.

from sqlalchemy import Column, Integer, String, Boolean, Enum as PgEnum, text
from sqlalchemy.orm import relationship
from extensions import db
from .mixins import TimestampMixin
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user  = "user"

class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True)
    email         = Column(String(120), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    first_name    = Column(String(120), nullable=False)
    last_name     = Column(String(120), nullable=False)
    role          = Column(PgEnum(UserRole, name="user_role"), nullable=False, server_default=text("'user'"))
    is_active     = Column(Boolean, nullable=False, server_default=text("true"))

    reservations  = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

