from pydantic import BaseModel, ConfigDict, EmailStr

from app.common.enums import UserRole


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    phone: str | None
    role: UserRole
    avatar_url: str | None
