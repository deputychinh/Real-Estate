from unittest.mock import AsyncMock

import pytest
from fakeredis import FakeAsyncRedis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.cache.cache_service import CacheService
from app.cache.rate_limiter import RateLimiter
from app.core.exceptions import RateLimitedError
from app.modules.properties.schemas import PropertySearchParams


async def test_rate_limiter_blocks_above_limit(redis: FakeAsyncRedis) -> None:
    limiter = RateLimiter(redis)
    for _ in range(3):
        await limiter.hit("ratelimit:test:1", limit=3, window_seconds=60)
    with pytest.raises(RateLimitedError) as error:
        await limiter.hit("ratelimit:test:1", limit=3, window_seconds=60)
    assert 1 <= error.value.retry_after_seconds <= 60


async def test_cache_degrades_to_miss_when_redis_is_down() -> None:
    broken = AsyncMock()
    broken.get.side_effect = RedisConnectionError("down")
    broken.set.side_effect = RedisConnectionError("down")
    cache = CacheService(broken)
    assert await cache.get_json("any") is None
    await cache.set_json("any", {"a": 1}, 10)  # does not raise
    assert await cache.search_version() == 0


async def test_search_version_bump_changes_keys(redis: FakeAsyncRedis) -> None:
    cache = CacheService(redis)
    assert await cache.search_version() == 0
    await cache.bump_search_version()
    assert await cache.search_version() == 1


def test_search_params_validate_ranges_and_hash_stably() -> None:
    with pytest.raises(ValueError, match="price_min"):
        PropertySearchParams(price_min=10, price_max=5)
    assert (
        PropertySearchParams(city="dubai").cache_digest() == PropertySearchParams(city="dubai").cache_digest()
    )
    assert (
        PropertySearchParams(city="dubai").cache_digest() != PropertySearchParams(city="hcm").cache_digest()
    )
