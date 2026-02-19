from collections.abc import Generator

from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)
