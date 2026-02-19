# Python App Template

A full-stack local Python web application template with FastAPI, Jinja2, htmx, Tailwind CSS, SQLite, and Google OAuth.

## Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI (async) |
| **Templates** | Jinja2 + htmx |
| **Styling** | Tailwind CSS |
| **Database** | SQLite (via SQLModel + SQLAlchemy) |
| **Migrations** | Alembic |
| **Auth** | Google OAuth (authlib) |
| **Validation** | Pydantic v2 |
| **Storage** | Local filesystem |
| **Logging** | loguru |
| **Package manager** | uv |

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
uv run python scripts/setup.py   # interactive setup
# or: cp .env.example .env && edit .env

# 3. Run database migrations
uv run alembic upgrade head

# 4. Start the development server
make dev
# -> http://localhost:8000
# -> http://localhost:8000/docs  (API docs)
```

## Project Structure

```
app/
├── main.py              # App entry point, middleware, router mounts
├── config.py            # Settings (reads .env)
├── db/
│   ├── database.py      # DB engine and session dependency
│   └── schema.py        # SQLModel table definitions
├── lib/
│   ├── auth.py          # Session management, OAuth user creation
│   ├── errors.py        # Standardised API response helpers
│   ├── oauth.py         # authlib Google OAuth client
│   └── storage.py       # Local file storage
├── middleware/
│   ├── auth.py          # Auth FastAPI dependencies
│   ├── logging.py       # Request logging
│   └── security.py      # CSP + security headers
├── pages/               # One file per page (HTML + API routes)
├── functions/           # Shared DB query functions
└── templates/           # Jinja2 HTML templates
alembic/                 # Database migrations
scripts/
└── setup.py             # Interactive setup
```

## Commands

```bash
make dev            # Start dev server with hot reload
make setup          # Interactive first-time configuration
make db-generate    # Generate a new migration (msg="description")
make db-migrate     # Apply pending migrations
make db-downgrade   # Roll back one migration
make typecheck      # Run pyright type checker
make lint           # Run ruff linter
make format         # Run ruff formatter
```

## Adding a New Page

1. Create `app/pages/my_page.py`
2. Create `app/templates/my_page.html`
3. Add `from app.pages import my_page` and `app.include_router(my_page.router)` in `app/main.py`

See `AGENTS.md` for detailed patterns and examples.

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Required | Default |
|---|---|---|
| `SECRET_KEY` | Yes | — |
| `APP_URL` | Yes | `http://localhost:8000` |
| `DATABASE_URL` | No | `sqlite:///./data.db` |
| `GOOGLE_CLIENT_ID` | OAuth only | — |
| `GOOGLE_CLIENT_SECRET` | OAuth only | — |
| `DEBUG` | No | `false` |

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create an OAuth 2.0 Client ID (Web application)
3. Add `http://localhost:8000/auth/callback` as an authorised redirect URI
4. Copy the client ID and secret into `.env`

## Deployment

```bash
# Run in production with gunicorn
uv add gunicorn
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with uvicorn directly
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Set `DEBUG=false` and `SECRET_KEY` to a strong random value in production.
