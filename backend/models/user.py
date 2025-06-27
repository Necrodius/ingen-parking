# This file defines the User model for the application.

from sqlalchemy import Column, Integer, String, Boolean, Enum as PgEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app import db
from .mixins import TimestampMixin

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String(120), nullable=False, unique=True, index=True)

    password_hash = Column(String(128), nullable=False)

    first_name = Column(String(120), nullable=False)
    
    last_name = Column(String(120), nullable=False)

    role = Column(PgEnum(UserRole), nullable=False, default=UserRole.USER)
    
    is_active = Column(Boolean, nullable=False, default=True)

    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
