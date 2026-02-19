from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.db.database import get_db
from app.lib.auth import SESSION_COOKIE, create_session, get_or_create_user
from app.lib.errors import api_success
from app.lib.oauth import oauth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "providers": ["google"]},
    )


@router.get("/api/pages/login/data")
async def login_data() -> dict:
    return api_success({"providers": ["google"], "oauth_url": "/auth/google"})


@router.get("/auth/google")
async def google_login(request: Request) -> RedirectResponse:
    from app.config import settings
    redirect_uri = f"{settings.app_url}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)  # type: ignore[no-any-return]


@router.get("/auth/callback")
async def auth_callback(
    request: Request,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        return RedirectResponse("/login?error=no_user_info")

    user = get_or_create_user(
        db,
        provider_id="google",
        account_id=user_info["sub"],
        email=user_info["email"],
        name=user_info.get("name"),
        image=user_info.get("picture"),
        access_token=token.get("access_token"),
        id_token=token.get("id_token"),
    )

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    session = create_session(db, user.id, ip_address=ip, user_agent=ua)

    from app.config import settings
    response = RedirectResponse("/")
    response.set_cookie(
        SESSION_COOKIE,
        session.token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response
