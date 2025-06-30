from typing import Optional
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.user import User, UserRole
from services.user_service import UserService
from utils.security import hash_password, verify_password, normalize_email

class AuthService:
    @staticmethod
    def register_user(
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.user
    ) -> User:
        # Normalize email
        email_norm = normalize_email(email)

        # Prevent duplicate email
        if UserService.get_by_email(email_norm):
            raise ValueError("Email already in use")

        # Create new user with hashed password
        user = User(
            email=email_norm,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        # Save to database
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Email already in use")

    @staticmethod
    def authenticate(*, email: str, password: str) -> Optional[User]:
        # Normalize email
        email_norm = normalize_email(email)

        # Reuse UserService to retrieve by email
        user = UserService.get_by_email(email_norm)

        # Verify password using utility
        if user and verify_password(password, user.password_hash):
            return user
        return None
