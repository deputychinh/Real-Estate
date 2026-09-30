"""Dependency wiring. Tests replace get_session and get_redis; everything else builds on them."""

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.cache_service import CacheService
from app.cache.rate_limiter import RateLimiter
from app.common.enums import TokenType, UserRole
from app.core.config import Settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import TokenClaims, decode_token
from app.db.unit_of_work import UnitOfWork
from app.modules.auth.service import AuthService
from app.modules.auth.token_store import TokenStore
from app.modules.currency.rates import CurrencyConverter, StaticRateProvider
from app.modules.favorites.service import FavoriteService
from app.modules.inquiries.service import InquiryService
from app.modules.locations.service import LookupService
from app.modules.properties.service import PropertyService
from app.modules.users.models import User

# ── Infrastructure ──


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as session:
        yield session


def get_redis(request: Request) -> Redis:
    redis: Redis = request.app.state.redis
    return redis


SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]

_converter = CurrencyConverter(StaticRateProvider())


def get_converter() -> CurrencyConverter:
    return _converter


def get_uow(session: SessionDep) -> UnitOfWork:
    return UnitOfWork(session)


def get_cache(redis: RedisDep) -> CacheService:
    return CacheService(redis)


def get_rate_limiter(redis: RedisDep) -> RateLimiter:
    return RateLimiter(redis)


def get_token_store(redis: RedisDep) -> TokenStore:
    return TokenStore(redis)


ConverterDep = Annotated[CurrencyConverter, Depends(get_converter)]
UowDep = Annotated[UnitOfWork, Depends(get_uow)]
CacheDep = Annotated[CacheService, Depends(get_cache)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]
TokenStoreDep = Annotated[TokenStore, Depends(get_token_store)]

# ── Services ──


def get_auth_service(
    uow: UowDep, tokens: TokenStoreDep, limiter: RateLimiterDep, settings: SettingsDep
) -> AuthService:
    return AuthService(uow, tokens, limiter, settings)


def get_property_service(uow: UowDep, cache: CacheDep, converter: ConverterDep) -> PropertyService:
    return PropertyService(uow, cache, converter)


def get_favorite_service(uow: UowDep) -> FavoriteService:
    return FavoriteService(uow)


def get_inquiry_service(uow: UowDep, limiter: RateLimiterDep) -> InquiryService:
    return InquiryService(uow, limiter)


def get_lookup_service(uow: UowDep, cache: CacheDep) -> LookupService:
    return LookupService(uow, cache)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
PropertyServiceDep = Annotated[PropertyService, Depends(get_property_service)]
FavoriteServiceDep = Annotated[FavoriteService, Depends(get_favorite_service)]
InquiryServiceDep = Annotated[InquiryService, Depends(get_inquiry_service)]
LookupServiceDep = Annotated[LookupService, Depends(get_lookup_service)]

# ── Auth: 401 = who are you?, 403 = you may not ──

_bearer = HTTPBearer(auto_error=False)


def get_access_claims(
    settings: SettingsDep, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]
) -> TokenClaims:
    if credentials is None:
        raise UnauthorizedError("Authentication required")
    return decode_token(settings, credentials.credentials, TokenType.ACCESS)


AccessClaimsDep = Annotated[TokenClaims, Depends(get_access_claims)]


async def get_current_user(claims: AccessClaimsDep, service: AuthServiceDep) -> User:
    return await service.authenticate(claims)


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], Awaitable[User]]:
    async def dependency(user: CurrentUserDep) -> User:
        if user.role not in roles:
            raise ForbiddenError(f"Requires role: {', '.join(roles)}")
        return user

    return dependency


AgentDep = Annotated[User, Depends(require_roles(UserRole.AGENT, UserRole.ADMIN))]
InvestorDep = Annotated[User, Depends(require_roles(UserRole.INVESTOR))]
