from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.constants import SLUG_MAX_LENGTH, TITLE_MAX_LENGTH
from app.common.enums import AreaUnit, Currency, ListingPurpose, PropertyStatus, PropertyType
from app.db.base import Base, SoftDeleteMixin, TimestampMixin
from app.db.types import str_enum
from app.modules.amenities.models import Amenity
from app.modules.locations.models import City
from app.modules.users.models import User

property_amenities = Table(
    "property_amenities",
    Base.metadata,
    Column("property_id", ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True),
    Column("amenity_id", ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
)


class Property(TimestampMixin, SoftDeleteMixin, Base):
    """A listing. Relationships use lazy="raise": every query states what it loads, so N+1 is impossible."""

    __tablename__ = "properties"
    __table_args__ = (
        Index("ix_properties_search", "status", "purpose", "property_type", "city_id", "price_usd"),
        Index("ix_properties_agent_status", "agent_id", "status"),
        Index("ix_properties_featured", "is_featured", "published_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(SLUG_MAX_LENGTH), unique=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(Text)
    purpose: Mapped[ListingPurpose] = mapped_column(str_enum(ListingPurpose))
    property_type: Mapped[PropertyType] = mapped_column(str_enum(PropertyType))
    status: Mapped[PropertyStatus] = mapped_column(str_enum(PropertyStatus), default=PropertyStatus.DRAFT)
    price: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    currency: Mapped[Currency] = mapped_column(str_enum(Currency))
    # Price normalised to USD at write time, so filters and sorting work across currencies.
    price_usd: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    area: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    area_unit: Mapped[AreaUnit] = mapped_column(str_enum(AreaUnit), default=AreaUnit.SQM)
    bedrooms: Mapped[int] = mapped_column(default=0)
    bathrooms: Mapped[int] = mapped_column(default=0)
    year_built: Mapped[int | None] = mapped_column(default=None)
    address: Mapped[str] = mapped_column(String(255))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), default=None)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), default=None)
    is_featured: Mapped[bool] = mapped_column(default=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    city: Mapped[City] = relationship(lazy="raise")
    agent: Mapped[User] = relationship(lazy="raise")
    images: Mapped[list["PropertyImage"]] = relationship(
        lazy="raise", cascade="all, delete-orphan", order_by="PropertyImage.sort_order"
    )
    amenities: Mapped[list[Amenity]] = relationship(secondary=property_amenities, lazy="raise")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(default=0)
    is_cover: Mapped[bool] = mapped_column(default=False)
