# This file defines the UserService class, which provides methods for managing users.
# It includes methods for creating, reading, updating, and deleting users and admins.

from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.user import User
from utils.security import hash_password, verify_password

class UserService:
    # ---------- CREATE ----------
    @staticmethod
    def create_user(**attrs) -> User:
        email = attrs.get("email")
        if email and UserService.get_by_email(email):
            raise ValueError("email already registered")

        # Accept raw `password` and store as hashed
        if raw_pw := attrs.pop("password", None):
            attrs["password_hash"] = hash_password(raw_pw)

        user = User(**attrs)
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("email already registered")

    # ---------- READ ----------
    @staticmethod
    def list_users() -> List[User]:
        return User.query.order_by(User.id).all()

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    # ---------- UPDATE ----------
    @staticmethod
    def update_user(user: User, **patch) -> User:
        # If changing email, ensure it's still unique
        if "email" in patch and patch["email"] != user.email:
            if UserService.get_by_email(patch["email"]):
                raise ValueError("email already registered")

        # Hash password if included in patch
        if "password" in patch:
            patch["password_hash"] = hash_password(patch.pop("password"))

        for field, value in patch.items():
            setattr(user, field, value)

        db.session.commit()
        return user

    # ---------- DELETE ----------
    @staticmethod
    def delete_user(user: User) -> None:
        db.session.delete(user)
        db.session.commit()

    # ---------- DEACTIVATE ----------
    @staticmethod
    def deactivate_user(user: User) -> User:
        user.active = False
        db.session.commit()
        return user

    # ---------- CHANGE PASSWORD ----------
    # This method changes the user's password after verifying the old one
    # Can be used together with the `update_user` method
    @staticmethod
    def change_password(user: User, old_pw: str, new_pw: str) -> None:
        # Ensure old password matches before changing to new one
        if not verify_password(old_pw, user.password_hash):
            raise ValueError("Incorrect old password")

        user.password_hash = hash_password(new_pw)
        db.session.commit()
