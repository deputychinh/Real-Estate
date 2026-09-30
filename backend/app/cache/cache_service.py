"""Cache-aside helpers. The cache is an optimisation, so a Redis outage degrades to a cache miss
(logged) instead of failing the request. Security checks do not use this class (see auth.token_store)."""

import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.cache import keys

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get_json(self, key: str) -> Any | None:
        try:
            raw = await self._redis.get(key)
        except RedisError:
            logger.warning("cache get failed, treating as miss", extra={"key": key})
            return None
        return json.loads(raw) if raw is not None else None

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        try:
            await self._redis.set(key, json.dumps(value), ex=ttl_seconds)
        except RedisError:
            logger.warning("cache set failed", extra={"key": key})

    async def delete(self, *keys_to_delete: str) -> None:
        try:
            await self._redis.delete(*keys_to_delete)
        except RedisError:
            logger.warning("cache delete failed", extra={"keys": keys_to_delete})

    async def search_version(self) -> int:
        try:
            raw = await self._redis.get(keys.SEARCH_VERSION_KEY)
        except RedisError:
            logger.warning("cache version read failed")
            return 0
        return int(raw) if raw is not None else 0

    async def bump_search_version(self) -> None:
        try:
            await self._redis.incr(keys.SEARCH_VERSION_KEY)
        except RedisError:
            # Search results may stay stale for up to CACHE_TTL_SEARCH_SECONDS; logged so it is visible.
            logger.error("cache version bump failed; search results may be stale until TTL")
