"""Password hashing and JWT creation/validation."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache

import bcrypt
import jwt
from pydantic import BaseModel, ValidationError

from app.common.constants import ACCESS_TOKEN_TTL_MINUTES, REFRESH_TOKEN_TTL_DAYS
from app.common.enums import TokenType, UserRole
from app.core.config import Settings
from app.core.exceptions import UnauthorizedError

TOKEN_TTL: dict[TokenType, timedelta] = {
    TokenType.ACCESS: timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
    TokenType.REFRESH: timedelta(days=REFRESH_TOKEN_TTL_DAYS),
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


@lru_cache
def dummy_password_hash() -> str:
    """Checked when the email is unknown, so login takes the same time either way (no user enumeration)."""
    return hash_password(uuid.uuid4().hex)


class TokenClaims(BaseModel):
    sub: str
    role: UserRole
    type: TokenType
    jti: str
    iat: datetime
    exp: datetime

    @property
    def user_id(self) -> int:
        return int(self.sub)

    def seconds_left(self) -> int:
        return max(int((self.exp - datetime.now(UTC)).total_seconds()), 1)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_claims: TokenClaims
    refresh_claims: TokenClaims


def create_token(
    settings: Settings, user_id: int, role: UserRole, token_type: TokenType
) -> tuple[str, TokenClaims]:
    now = datetime.now(UTC)
    claims = TokenClaims(
        sub=str(user_id),
        role=role,
        type=token_type,
        jti=uuid.uuid4().hex,
        iat=now,
        exp=now + TOKEN_TTL[token_type],
    )
    payload = claims.model_dump(mode="json") | {
        "iat": int(now.timestamp()),
        "exp": int(claims.exp.timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)
    return token, claims


def create_token_pair(settings: Settings, user_id: int, role: UserRole) -> TokenPair:
    access, access_claims = create_token(settings, user_id, role, TokenType.ACCESS)
    refresh, refresh_claims = create_token(settings, user_id, role, TokenType.REFRESH)
    return TokenPair(access, refresh, access_claims, refresh_claims)


def decode_token(settings: Settings, token: str, expected_type: TokenType) -> TokenClaims:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "iat", "jti"]},
        )
        claims = TokenClaims.model_validate(payload)
    except (jwt.PyJWTError, ValidationError) as error:
        raise UnauthorizedError("Invalid or expired token") from error
    if claims.type != expected_type:
        raise UnauthorizedError("Wrong token type")
    return claims
