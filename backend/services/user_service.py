from typing import List, Optional
from extensions import db
from models.user import User

class UserService:
    
    # ---------- Create ----------
    @staticmethod
    def create_user(**user_dict) -> User:
        user = User(**user_dict)
        db.session.add(user)
        db.session.commit()
        return user
    
    # ---------- Read ----------
    @staticmethod
    def list_users() -> List[User]:
        return User.query.all()

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    # ---------- Update ----------
    @staticmethod
    def update_user(user: User, **changes) -> User:
        for field, value in changes.items():
            setattr(user, field, value)
        db.session.commit()
        return user

    # ---------- Delete ----------
    @staticmethod
    def delete_user(user: User) -> None:
        db.session.delete(user)
        db.session.commit()

    # ---------- Deactivate ----------
    @staticmethod
    def deactivate_user(user: User) -> User:
        user.is_active = False
        db.session.commit()
        return user


