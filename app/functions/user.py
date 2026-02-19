from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.db.schema import User


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def update_user_profile(db: Session, user_id: str, name: str) -> Optional[User]:
    user = db.get(User, user_id)
    if user:
        user.name = name
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
