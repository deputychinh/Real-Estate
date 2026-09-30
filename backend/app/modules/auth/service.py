from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from app.cache import keys
from app.cache.rate_limiter import RateLimiter
from app.common.constants import RATE_LIMIT_LOGIN_PER_MINUTE, RATE_LIMIT_LOGIN_WINDOW_SECONDS
from app.common.enums import TokenType
from app.core.config import Settings
from app.core.exceptions import AppError, ConflictError, UnauthorizedError
from app.core.security import (
    TokenClaims,
    TokenPair,
    create_token_pair,
    decode_token,
    dummy_password_hash,
    hash_password,
    verify_password,
)
from app.db.unit_of_work import UnitOfWork
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.auth.token_store import TokenStore
from app.modules.users.models import User

INVALID_CREDENTIALS = "Incorrect email or password"


class AuthService:
    def __init__(self, uow: UnitOfWork, tokens: TokenStore, limiter: RateLimiter, settings: Settings) -> None:
        self.uow = uow
        self.tokens = tokens
        self.limiter = limiter
        self.settings = settings

    async def register(self, data: RegisterRequest) -> User:
        user = User(
            email=data.email,
            hashed_password=await run_in_threadpool(hash_password, data.password),  # bcrypt is CPU-bound
            full_name=data.full_name,
            phone=data.phone,
            role=data.role,
        )
        try:
            await self.uow.users.add(user)
            await self.uow.commit()
        except IntegrityError as error:  # the UNIQUE index decides, so two parallel sign-ups cannot both win
            await self.uow.rollback()
            raise ConflictError("Email is already registered") from error
        return user

    async def login(self, data: LoginRequest, client_ip: str) -> tuple[User, TokenPair]:
        await self.limiter.hit(
            keys.rate_limit("login", client_ip), RATE_LIMIT_LOGIN_PER_MINUTE, RATE_LIMIT_LOGIN_WINDOW_SECONDS
        )
        user = await self.uow.users.get_by_email(data.email)
        stored_hash = user.hashed_password if user else dummy_password_hash()
        password_ok = await run_in_threadpool(verify_password, data.password, stored_hash)
        if user is None or not password_ok or not user.is_active:
            raise UnauthorizedError(INVALID_CREDENTIALS)
        return user, create_token_pair(self.settings, user.id, user.role)

    async def refresh(self, refresh_token: str | None) -> tuple[User, TokenPair]:
        if not refresh_token:
            raise UnauthorizedError("Missing refresh token")
        claims = decode_token(self.settings, refresh_token, TokenType.REFRESH)
        if await self.tokens.is_revoked(claims.jti):
            raise UnauthorizedError("Refresh token has been revoked")
        user = await self._active_user(claims.user_id)
        await self.tokens.revoke(claims)  # rotation: each refresh token works once
        return user, create_token_pair(self.settings, user.id, user.role)

    async def logout(self, access_claims: TokenClaims, refresh_token: str | None) -> None:
        await self.tokens.revoke(access_claims)
        if not refresh_token:
            return
        try:
            await self.tokens.revoke(decode_token(self.settings, refresh_token, TokenType.REFRESH))
        except AppError:
            return  # an invalid or expired refresh token is already unusable

    async def authenticate(self, claims: TokenClaims) -> User:
        if await self.tokens.is_revoked(claims.jti):
            raise UnauthorizedError("Token has been revoked")
        return await self._active_user(claims.user_id)

    async def _active_user(self, user_id: int) -> User:
        user = await self.uow.users.get(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Account not found or disabled")
        return user
