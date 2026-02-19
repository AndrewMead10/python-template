import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db.database import create_tables
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.pages import index, login, logout

# Configure loguru
logger.remove()
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up - creating database tables")
    create_tables()
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Middleware (applied in reverse order - last added = outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    https_only=not settings.debug,
    same_site="lax",
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Page routers
app.include_router(index.router)
app.include_router(login.router)
app.include_router(logout.router)


# Health check
@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
