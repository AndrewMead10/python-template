from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.db.database import get_db
from app.lib.auth import SESSION_COOKIE, delete_session
from app.lib.errors import api_success

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "logout.html",
        {"request": request, "message": "Are you sure you want to log out?"},
    )


@router.get("/api/pages/logout/data")
async def logout_data() -> dict:
    return api_success({"message": "Are you sure you want to log out?"})


@router.post("/api/pages/logout/logout")
async def api_logout(request: Request, db: Session = Depends(get_db)) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        delete_session(db, token)
    return api_success({"redirect_url": "/"})


@router.post("/logout")
async def logout_action(
    request: Request,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        delete_session(db, token)
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response
