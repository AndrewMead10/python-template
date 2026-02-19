import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select

from app.db.schema import Account, User, UserSession

SESSION_COOKIE = "session_token"
SESSION_EXPIRES_DAYS = 30


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def create_session(
    db: Session,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserSession:
    session = UserSession(
        user_id=user_id,
        token=generate_token(),
        expires_at=datetime.utcnow() + timedelta(days=SESSION_EXPIRES_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, token: str) -> Optional[tuple[User, UserSession]]:
    statement = (
        select(User, UserSession)
        .join(UserSession, User.id == UserSession.user_id)  # type: ignore[arg-type]
        .where(UserSession.token == token)
        .where(UserSession.expires_at > datetime.utcnow())
    )
    result = db.exec(statement).first()
    return result  # type: ignore[return-value]


def delete_session(db: Session, token: str) -> None:
    statement = select(UserSession).where(UserSession.token == token)
    session = db.exec(statement).first()
    if session:
        db.delete(session)
        db.commit()


def get_or_create_user(
    db: Session,
    provider_id: str,
    account_id: str,
    email: str,
    name: Optional[str] = None,
    image: Optional[str] = None,
    access_token: Optional[str] = None,
    id_token: Optional[str] = None,
) -> User:
    # Try to find existing account link
    account_stmt = select(Account).where(
        Account.provider_id == provider_id,
        Account.account_id == account_id,
    )
    account = db.exec(account_stmt).first()

    if account:
        user = db.get(User, account.user_id)
        if user:
            # Update tokens
            account.access_token = access_token
            account.id_token = id_token
            account.updated_at = datetime.utcnow()
            db.add(account)
            db.commit()
            return user

    # Try to find existing user by email
    user_stmt = select(User).where(User.email == email)
    user = db.exec(user_stmt).first()

    if not user:
        user = User(email=email, name=name, image=image, email_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create account link
    new_account = Account(
        user_id=user.id,
        provider_id=provider_id,
        account_id=account_id,
        access_token=access_token,
        id_token=id_token,
    )
    db.add(new_account)
    db.commit()
    return user
