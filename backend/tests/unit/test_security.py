from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import SecretStr

from app.common.enums import Environment, TokenType, UserRole
from app.core.config import LOCAL_JWT_SECRET, Settings
from app.core.exceptions import UnauthorizedError
from app.core.security import create_token_pair, decode_token, hash_password, verify_password

SETTINGS = Settings(
    environment=Environment.TEST, jwt_secret=SecretStr("unit-secret-0123456789abcdef0123456789")
)


def test_password_hash_round_trip() -> None:
    hashed = hash_password("Passw0rd!")
    assert verify_password("Passw0rd!", hashed)
    assert not verify_password("wrong", hashed)


def test_token_pair_decodes_with_expected_type() -> None:
    pair = create_token_pair(SETTINGS, user_id=7, role=UserRole.AGENT)
    claims = decode_token(SETTINGS, pair.access_token, TokenType.ACCESS)
    assert claims.user_id == 7 and claims.role == UserRole.AGENT
    assert pair.access_claims.jti != pair.refresh_claims.jti


def test_refresh_token_is_rejected_as_access_token() -> None:
    pair = create_token_pair(SETTINGS, user_id=7, role=UserRole.AGENT)
    with pytest.raises(UnauthorizedError, match="Wrong token type"):
        decode_token(SETTINGS, pair.refresh_token, TokenType.ACCESS)


def test_tampered_and_expired_tokens_are_rejected() -> None:
    pair = create_token_pair(SETTINGS, user_id=7, role=UserRole.AGENT)
    with pytest.raises(UnauthorizedError):
        decode_token(SETTINGS, pair.access_token[:-2] + "xx", TokenType.ACCESS)

    past = datetime.now(UTC) - timedelta(hours=1)
    payload = {"sub": "7", "role": "AGENT", "type": "access", "jti": "x", "iat": past, "exp": past}
    expired = jwt.encode(payload, SETTINGS.jwt_secret.get_secret_value(), algorithm="HS256")
    with pytest.raises(UnauthorizedError):
        decode_token(SETTINGS, expired, TokenType.ACCESS)


def test_default_secret_is_refused_in_production() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(environment=Environment.PRODUCTION, jwt_secret=SecretStr(LOCAL_JWT_SECRET))
