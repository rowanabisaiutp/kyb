import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

TEST_DB_URL = os.environ.get("DATABASE_URL", "")

if TEST_DB_URL and "postgresql" in TEST_DB_URL:
    _engine = create_async_engine(TEST_DB_URL, echo=False)
else:
    _engine = create_async_engine(
        "sqlite+aiosqlite:///test_kyb.db",
        echo=False,
        connect_args={"check_same_thread": False},
    )

_session_factory = async_sessionmaker(
    _engine, class_=AsyncSession, expire_on_commit=False
)

import app.database as db_module
import app.dependencies as dep_module

db_module.engine = _engine
db_module.async_session = _session_factory


async def _get_test_db():
    async with _session_factory() as session:
        yield session


from main import app

app.dependency_overrides[dep_module.get_db] = _get_test_db


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await _engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
