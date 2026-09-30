from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import UserRole
from app.db.base import Base, TimestampMixin
from app.db.types import str_enum


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(32), default=None)
    role: Mapped[UserRole] = mapped_column(str_enum(UserRole))
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
