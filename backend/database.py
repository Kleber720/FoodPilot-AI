"""Configuração do banco de dados SQLite e gerenciamento de sessão SQLAlchemy 2.x."""

import os
from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./foodpilot.db"


def get_database_url() -> str:
    """Retorna a URL de conexão configurada em DATABASE_URL ou o banco SQLite padrão."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


DATABASE_URL: str = get_database_url()


class Base(DeclarativeBase):
    """Classe base declarativa para os modelos ORM do SQLAlchemy 2.x."""


def build_engine(database_url: str | None = None) -> Engine:
    """Cria uma instância de Engine SQLAlchemy configurada para SQLite ou outro dialeto."""
    url = database_url or get_database_url()
    connect_args: dict[str, Any] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args, future=True)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Ativa integridade referencial (FOREIGN KEYS) em conexões SQLite."""
    module_name = type(dbapi_connection).__module__
    if "sqlite3" in module_name:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine: Engine = build_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def init_db(target_engine: Engine | None = None) -> None:
    """Garante que todas as tabelas declaradas em Base.metadata existam no banco."""
    import backend.models  # noqa: F401

    Base.metadata.create_all(bind=target_engine or engine)


def get_db() -> Generator[Session, None, None]:
    """Dependência FastAPI que fornece uma sessão transacional por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
