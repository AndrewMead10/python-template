.PHONY: install dev setup db-generate db-migrate db-downgrade typecheck lint format

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload --port 8000

setup:
	uv run python scripts/setup.py

db-generate:
	uv run alembic revision --autogenerate -m "$(msg)"

db-migrate:
	uv run alembic upgrade head

db-downgrade:
	uv run alembic downgrade -1

typecheck:
	uv run pyright app/

lint:
	uv run ruff check app/

format:
	uv run ruff format app/
