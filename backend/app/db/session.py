import ssl
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


def connect_args(settings: Settings) -> dict[str, Any]:
    """TLS to MySQL when a CA bundle is configured; the context verifies the server certificate."""
    if not settings.database_ssl_ca:
        return {}
    return {"ssl": ssl.create_default_context(cafile=settings.database_ssl_ca)}


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
        connect_args=connect_args(settings),
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
