from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.lib.errors import api_success

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Python App",
            "description": "A full-stack local Python web application template",
        },
    )


@router.get("/api/pages/index/data")
async def index_data() -> dict:
    return api_success({
        "title": "Python App",
        "description": "A full-stack local Python web application template",
    })
