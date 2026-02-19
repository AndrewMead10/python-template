# Python App - Agent Instructions

This is a full-stack local Python web application template. Read this document before making any changes.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| Templates | Jinja2 + htmx |
| Styling | Tailwind CSS (CDN in dev) |
| Database | SQLite via SQLModel + SQLAlchemy |
| Migrations | Alembic |
| Auth | Google OAuth via authlib + custom session table |
| Validation | Pydantic v2 (built into FastAPI) |
| Storage | Local filesystem |
| Logging | loguru |
| Package manager | uv |

## Critical Rules

1. **Always use `uv run`** for all Python commands: `uv run uvicorn ...`, `uv run alembic ...`, `uv run pyright ...`
2. **Never use pip directly** — use `uv add <package>` to add dependencies
3. **Run type checking** with `uv run pyright app/` after making changes
4. **Generate migrations** after every schema change: `uv run alembic revision --autogenerate -m "description"`
5. **Apply migrations** before running: `uv run alembic upgrade head`
6. **Extract shared DB logic** into `app/functions/` — never duplicate queries across pages
7. **All DB operations** must use the `Session` from `app.db.database.get_db` via FastAPI `Depends`

## Project Structure

```
app/
├── main.py              # FastAPI app, middleware registration, router mounts
├── config.py            # Settings (pydantic-settings, reads .env)
├── db/
│   ├── database.py      # SQLAlchemy engine, get_db dependency, create_tables
│   └── schema.py        # SQLModel table definitions (User, UserSession, Account)
├── lib/
│   ├── auth.py          # Session CRUD, get_or_create_user for OAuth flow
│   ├── errors.py        # api_success(), api_error(), ErrorCodes constants
│   ├── oauth.py         # authlib OAuth client (google registered here)
│   └── storage.py       # Local file storage helpers
├── middleware/
│   ├── auth.py          # require_auth / get_current_user_optional FastAPI deps
│   ├── logging.py       # Request/response logging middleware
│   └── security.py      # CSP + security headers middleware
├── pages/               # One module per page - handles both HTML and API routes
│   ├── index.py
│   ├── login.py         # Also handles /auth/google and /auth/callback
│   └── logout.py
├── functions/           # Reusable DB query functions, imported by pages
│   └── user.py
└── templates/           # Jinja2 HTML templates
    ├── base.html        # Base layout with Tailwind CDN + htmx
    ├── index.html
    ├── login.html
    └── logout.html
alembic/
├── env.py               # Alembic config - imports all models automatically
├── script.py.mako       # Migration file template
└── versions/            # Generated migration files (commit these)
scripts/
└── setup.py             # Interactive first-time setup script
```

## Pages Pattern

Each page in `app/pages/` has:
- `GET /{page}` — renders the full HTML page via Jinja2
- `GET /api/pages/{page}/data` — returns page init data as JSON (for htmx or API use)
- `POST /api/pages/{page}/{action}` — handles form submissions, returns JSON
- `POST /{page}` — handles standard HTML form submissions (redirects)

Example for a new `dashboard` page:

```python
# app/pages/dashboard.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.db.database import get_db
from app.db.schema import User, UserSession
from app.lib.errors import api_success
from app.middleware.auth import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    auth: tuple[User, UserSession] = Depends(require_auth),
) -> HTMLResponse:
    user, session = auth
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user},
    )


@router.get("/api/pages/dashboard/data")
async def dashboard_data(
    auth: tuple[User, UserSession] = Depends(require_auth),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = auth
    return api_success({"user_id": user.id, "email": user.email})
```

Then register in `app/main.py`:
```python
from app.pages import dashboard
app.include_router(dashboard.router)
```

## API Response Format

All JSON endpoints must use these helpers from `app/lib/errors.py`:

```python
# Success
return api_success({"key": "value"})
# -> {"success": True, "data": {"key": "value"}}

# Error
return api_error(ErrorCodes.NOT_FOUND, "User not found")
# -> {"success": False, "error": {"code": "NOT_FOUND", "message": "User not found"}}

# Validation error with field errors
return api_error(
    ErrorCodes.VALIDATION_ERROR,
    "Invalid input",
    field_errors={"email": "Invalid email format"},
)
```

## Authentication

Auth state is accessed via FastAPI dependencies:

```python
from app.middleware.auth import require_auth, get_current_user_optional

# Protected route - raises 401 if not logged in
@router.get("/protected")
async def protected(auth: tuple[User, UserSession] = Depends(require_auth)):
    user, session = auth
    ...

# Optional auth - returns None if not logged in
@router.get("/public")
async def public(auth = Depends(get_current_user_optional)):
    if auth:
        user, session = auth
    ...
```

Session cookie: `session_token` (httpOnly, secure in production, 30-day expiry)

## Database Patterns

Always inject the session via `Depends(get_db)`:

```python
from app.db.database import get_db
from sqlmodel import Session

@router.get("/example")
async def example(db: Session = Depends(get_db)) -> dict:
    users = db.exec(select(User)).all()
    return api_success({"users": [u.model_dump() for u in users]})
```

Extract reusable queries into `app/functions/`:

```python
# app/functions/user.py
def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)
```

## Schema Changes

1. Edit `app/db/schema.py`
2. Generate migration: `uv run alembic revision --autogenerate -m "add field X to users"`
3. Review generated file in `alembic/versions/`
4. Apply: `uv run alembic upgrade head`

## htmx Patterns

Use htmx attributes for dynamic behaviour without writing JavaScript:

```html
<!-- Partial reload on button click -->
<button
  hx-post="/api/pages/dashboard/refresh"
  hx-target="#content"
  hx-swap="innerHTML"
>
  Refresh
</button>

<!-- Form submission returning HTML fragment -->
<form hx-post="/api/pages/profile/update" hx-target="#result">
  <input name="name" type="text" />
  <button type="submit">Save</button>
</form>
<div id="result"></div>
```

For htmx endpoints, return `HTMLResponse` with a Jinja2 fragment instead of JSON:

```python
@router.post("/api/pages/profile/update")
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    auth: tuple[User, UserSession] = Depends(require_auth),
) -> HTMLResponse:
    user, _ = auth
    form = await request.form()
    # ... update logic
    return templates.TemplateResponse(
        "fragments/profile_updated.html",
        {"request": request, "user": user},
    )
```

## Security

- CSP headers applied globally via `SecurityHeadersMiddleware`
- All form inputs validated via Pydantic models
- Sessions stored in DB with expiry enforcement
- Cookies: httpOnly=True, secure=True in production, samesite=lax
- Never store sensitive data in templates — use Jinja2 autoescaping (enabled by default)

## Storage

```python
from app.lib.storage import save_file, generate_key, delete_file, get_storage_path

# Save an uploaded file
key = generate_key(prefix="avatars/", suffix=".jpg")
await save_file(key, file_bytes)

# Get the full path for serving
path = get_storage_path(key)
```

Mount the uploads directory as static files in `main.py` if you need to serve them:
```python
app.mount("/uploads", StaticFiles(directory=settings.storage_path), name="uploads")
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Session signing key (min 32 chars) |
| `APP_URL` | Yes | Base URL (e.g. http://localhost:8000) |
| `DATABASE_URL` | No | Defaults to `sqlite:///./data.db` |
| `GOOGLE_CLIENT_ID` | For OAuth | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | For OAuth | Google OAuth client secret |
| `DEBUG` | No | Enables debug mode + insecure cookies |
| `STORAGE_PATH` | No | Defaults to `./uploads` |
| `LOG_LEVEL` | No | Defaults to `INFO` |

## Commands

```bash
make install        # uv sync
make dev            # uvicorn app.main:app --reload
make setup          # interactive first-time config
make db-generate    # alembic revision --autogenerate -m "..."
make db-migrate     # alembic upgrade head
make db-downgrade   # alembic downgrade -1
make typecheck      # pyright app/
make lint           # ruff check app/
make format         # ruff format app/
```

## Default Pages

| Route | Description |
|---|---|
| `GET /` | Landing page |
| `GET /login` | Login page with Google OAuth button |
| `GET /auth/google` | Initiates Google OAuth flow |
| `GET /auth/callback` | OAuth callback, creates session |
| `GET /logout` | Logout confirmation page |
| `POST /logout` | Clears session and redirects to `/` |
| `GET /api/health` | Health check |
| `GET /docs` | FastAPI auto-generated API docs (Swagger UI) |
| `GET /redoc` | FastAPI auto-generated API docs (ReDoc) |

## Agent Checklist

When adding a new feature:
- [ ] Add route handler in `app/pages/<page>.py`
- [ ] Add Jinja2 template in `app/templates/<page>.html`
- [ ] Extract DB queries into `app/functions/`
- [ ] Register router in `app/main.py`
- [ ] Add schema changes to `app/db/schema.py` if needed
- [ ] Generate and apply migration if schema changed
- [ ] Run `uv run pyright app/` to verify types
