from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.common.constants import BCRYPT_MAX_BYTES, PASSWORD_MIN_LENGTH
from app.common.enums import UserRole
from app.modules.users.schemas import UserRead

PHONE_PATTERN = r"^\+?[0-9 ()-]{6,32}$"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=64)
    full_name: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(None, pattern=PHONE_PATTERN)
    role: Literal[UserRole.INVESTOR, UserRole.AGENT] = UserRole.INVESTOR

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def strong_enough(cls, value: str) -> str:
        if not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("password needs at least one letter and one digit")
        if len(value.encode()) > BCRYPT_MAX_BYTES:
            raise ValueError(f"password must be at most {BCRYPT_MAX_BYTES} bytes")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        return value.lower()


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 - OAuth2 token type, not a secret
    expires_in: int
    user: UserRead
