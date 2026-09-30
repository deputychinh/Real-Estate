from redis.asyncio import Redis

from app.core.exceptions import RateLimitedError


class RateLimiter:
    """Fixed-window counter: INCR the key, set its expiry on the first hit, reject above the limit."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def hit(self, key: str, limit: int, window_seconds: int) -> None:
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, window_seconds)
        if count > limit:
            ttl = await self._redis.ttl(key)
            raise RateLimitedError("Too many requests, try again later", retry_after_seconds=max(ttl, 1))
