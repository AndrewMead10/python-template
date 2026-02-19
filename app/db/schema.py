import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


def generate_id() -> str:
    return str(uuid.uuid4())


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=generate_id, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    image: Optional[str] = None
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(default_factory=generate_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: str = Field(default_factory=generate_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    account_id: str  # Provider's user ID (e.g., Google sub)
    provider_id: str  # e.g., "google"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token_expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
