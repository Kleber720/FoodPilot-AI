"""Fixtures compartilhadas e cliente ASGI síncrono compatível com o sandbox Windows."""

from collections.abc import Generator
from pathlib import Path
from typing import Any

import anyio.to_thread
import httpx
import pytest
import starlette.concurrency
from sqlalchemy.orm import Session, sessionmaker

from backend.database import build_engine, get_db, init_db
from backend.main import app


async def _sync_direct(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Executa funções síncronas diretamente na corrotina sem abrir threads/socketpair."""
    kwargs.pop("abandon_on_cancel", None)
    kwargs.pop("limiter", None)
    return func(*args, **kwargs)


anyio.to_thread.run_sync = _sync_direct
starlette.concurrency.run_in_threadpool = _sync_direct


def run_sync(coro: Any) -> Any:
    """Executa uma corrotina pura sem depender de event loop com socketpair no Windows."""
    try:
        while True:
            coro.send(None)
    except StopIteration as exc:
        return exc.value


class SyncASGIClient:
    """Cliente HTTP de teste sobre ASGITransport sem criação de sockets."""

    def __init__(self, fastapi_app: Any) -> None:
        self.app = fastapi_app

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async def _do() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as ac:
                return await ac.request(method, url, **kwargs)

        return run_sync(_do())

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)


@pytest.fixture()
def sample_csv_path() -> Path:
    """Caminho absoluto para o dataset canônico `data/sample_orders.csv`."""
    return Path(__file__).resolve().parent.parent / "data" / "sample_orders.csv"


@pytest.fixture()
def sample_csv_bytes(sample_csv_path: Path) -> bytes:
    """Conteúdo binário do dataset canônico `data/sample_orders.csv`."""
    return sample_csv_path.read_bytes()


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    """Cria um banco SQLite isolado em diretório temporário para cada teste."""
    db_file = tmp_path / "test_foodpilot.db"
    test_engine = build_engine(f"sqlite:///{db_file}")
    init_db(test_engine)
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        class_=Session,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        test_engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[SyncASGIClient, None, None]:
    """Fornece um cliente HTTP acoplado ao banco SQLite temporário isolado do teste."""

    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield SyncASGIClient(app)
    finally:
        app.dependency_overrides.clear()
