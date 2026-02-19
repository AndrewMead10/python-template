from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from app.db.database import get_db
from app.db.schema import User, UserSession
from app.lib.auth import SESSION_COOKIE, get_session
from app.lib.errors import ErrorCodes


def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> Optional[tuple[User, UserSession]]:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    return get_session(db, token)


def require_auth(
    result: Optional[tuple[User, UserSession]] = Depends(get_current_user_optional),
) -> tuple[User, UserSession]:
    if result is None:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodes.UNAUTHORIZED,
                    "message": "Authentication required",
                },
            },
        )
    return result
