from typing import Generator, Optional
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, text

from app.core.config import settings


def _ensure_data_dir() -> None:
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    db_dir = db_path.parent
    db_dir.mkdir(parents=True, exist_ok=True)


_ensure_data_dir()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.SQL_ECHO
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    _ensure_data_dir()
    SQLModel.metadata.create_all(engine)


def init_db() -> None:
    _ensure_data_dir()
    create_db_and_tables()
