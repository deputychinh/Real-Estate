from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import InquiryStatus
from app.db.base import Base, TimestampMixin
from app.db.types import str_enum
from app.modules.properties.models import Property
from app.modules.users.models import User


class Inquiry(TimestampMixin, Base):
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(32), default=None)
    status: Mapped[InquiryStatus] = mapped_column(str_enum(InquiryStatus), default=InquiryStatus.NEW)

    property: Mapped[Property] = relationship(lazy="raise")
    user: Mapped[User] = relationship(lazy="raise")
