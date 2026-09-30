"""Tests run the real app over HTTP (httpx) with SQLite in memory and fakeredis instead of MySQL/Redis,
so the suite is fast and needs no services. MySQL compatibility is checked by migrations + seed."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from fakeredis import FakeAsyncRedis
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.db.models
from app.api.deps import get_redis, get_session
from app.common.enums import Environment
from app.core.config import Settings
from app.db.base import Base
from app.main import create_app
from tests.factories import World, build_world


@pytest.fixture
def settings() -> Settings:
    return Settings(
        environment=Environment.TEST,
        database_url="sqlite+aiosqlite://",
        redis_url="redis://unused",
        jwt_secret=SecretStr("test-secret-0123456789abcdef0123456789"),
        log_level="WARNING",
    )


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)

    @event.listens_for(engine.sync_engine, "connect")
    def enable_foreign_keys(dbapi_connection, _record):  # type: ignore[no-untyped-def]
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def redis() -> AsyncIterator[FakeAsyncRedis]:
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.fixture
def app(
    settings: Settings, session_factory: async_sessionmaker[AsyncSession], redis: FakeAsyncRedis
) -> FastAPI:
    application = create_app(settings)

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    application.dependency_overrides[get_session] = override_session
    application.dependency_overrides[get_redis] = lambda: redis
    return application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http


@pytest_asyncio.fixture
async def world(session_factory: async_sessionmaker[AsyncSession]) -> World:
    """Reference data + one user per role + a few listings, created directly in the database."""
    async with session_factory() as session:
        return await build_world(session)
