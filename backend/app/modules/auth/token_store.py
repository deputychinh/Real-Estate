"""Revoked token ids. Unlike the cache, this is a security check: if Redis is down the request fails
(503) instead of accepting a possibly revoked token."""

from redis.asyncio import Redis

from app.cache import keys
from app.core.security import TokenClaims


class TokenStore:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def revoke(self, claims: TokenClaims) -> None:
        await self._redis.set(keys.revoked_token(claims.jti), "1", ex=claims.seconds_left())

    async def is_revoked(self, jti: str) -> bool:
        return bool(await self._redis.exists(keys.revoked_token(jti)))
