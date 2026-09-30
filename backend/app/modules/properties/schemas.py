import hashlib
from datetime import date, datetime
from decimal import Decimal
from typing import Self

from pydantic import AnyHttpUrl, BaseModel, Field, model_validator

from app.common.constants import MAX_IMAGES_PER_PROPERTY, SEARCH_QUERY_MAX_LENGTH, TITLE_MAX_LENGTH
from app.common.enums import (
    AreaUnit,
    Currency,
    ListingPurpose,
    PropertySort,
    PropertyStatus,
    PropertyType,
)
from app.common.pagination import PageParams
from app.modules.amenities.schemas import AmenityRead
from app.modules.locations.schemas import CityRead

Price = Decimal
Money = Field(gt=0, max_digits=15, decimal_places=2)


# ── Query ──


class PropertySearchParams(PageParams):
    """Search filters. Price range is given in `price_currency` and compared on the USD-normalised price."""

    purpose: ListingPurpose | None = None
    property_type: PropertyType | None = None
    country: str | None = Field(None, min_length=2, max_length=2, description="ISO country code")
    city: str | None = Field(None, max_length=100, description="City slug")
    price_min: Decimal | None = Field(None, ge=0)
    price_max: Decimal | None = Field(None, ge=0)
    price_currency: Currency = Currency.USD
    bedrooms_min: int | None = Field(None, ge=0, le=20)
    area_min: Decimal | None = Field(None, ge=0)
    area_max: Decimal | None = Field(None, ge=0)
    q: str | None = Field(None, max_length=SEARCH_QUERY_MAX_LENGTH, description="Text in the title")
    sort: PropertySort = PropertySort.NEWEST

    @model_validator(mode="after")
    def ranges_are_ordered(self) -> Self:
        if self.price_min is not None and self.price_max is not None and self.price_min > self.price_max:
            raise ValueError("price_min must not be greater than price_max")
        if self.area_min is not None and self.area_max is not None and self.area_min > self.area_max:
            raise ValueError("area_min must not be greater than area_max")
        return self

    def cache_digest(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()[:32]


# ── Output ──


class ImageRead(BaseModel):
    url: str
    is_cover: bool
    sort_order: int


class AgentRead(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    avatar_url: str | None


class PropertySummary(BaseModel):
    """What a listing card needs. Money is serialised as a string to keep exact decimals."""

    id: int
    slug: str
    title: str
    purpose: ListingPurpose
    property_type: PropertyType
    status: PropertyStatus
    price: Decimal
    currency: Currency
    price_usd: Decimal
    area: Decimal
    area_unit: AreaUnit
    bedrooms: int
    bathrooms: int
    city: CityRead
    cover_image_url: str | None
    is_featured: bool
    published_at: datetime | None


class PropertyDetail(PropertySummary):
    description: str
    address: str
    year_built: int | None
    latitude: Decimal | None
    longitude: Decimal | None
    images: list[ImageRead]
    amenities: list[AmenityRead]
    agent: AgentRead
    created_at: datetime
    updated_at: datetime


# ── Input ──


class ImageIn(BaseModel):
    url: AnyHttpUrl
    is_cover: bool = False


class _PropertyFields(BaseModel):
    @model_validator(mode="after")
    def at_most_one_cover(self) -> Self:
        images: list[ImageIn] | None = getattr(self, "images", None)
        if images and sum(image.is_cover for image in images) > 1:
            raise ValueError("only one image can be the cover")
        return self


class PropertyCreate(_PropertyFields):
    title: str = Field(min_length=5, max_length=TITLE_MAX_LENGTH)
    description: str = Field(min_length=20, max_length=10_000)
    purpose: ListingPurpose
    property_type: PropertyType
    price: Price = Money
    currency: Currency
    area: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    area_unit: AreaUnit = AreaUnit.SQM
    bedrooms: int = Field(0, ge=0, le=50)
    bathrooms: int = Field(0, ge=0, le=50)
    year_built: int | None = Field(None, ge=1800, le=date.today().year + 5)
    address: str = Field(min_length=3, max_length=255)
    city_id: int = Field(gt=0)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    amenity_ids: list[int] = Field(default_factory=list, max_length=50)
    images: list[ImageIn] = Field(default_factory=list, max_length=MAX_IMAGES_PER_PROPERTY)


class PropertyUpdate(_PropertyFields):
    """Partial update: only the fields that are sent change. Lists replace the old list."""

    title: str | None = Field(None, min_length=5, max_length=TITLE_MAX_LENGTH)
    description: str | None = Field(None, min_length=20, max_length=10_000)
    purpose: ListingPurpose | None = None
    property_type: PropertyType | None = None
    price: Price | None = Field(None, gt=0, max_digits=15, decimal_places=2)
    currency: Currency | None = None
    area: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    area_unit: AreaUnit | None = None
    bedrooms: int | None = Field(None, ge=0, le=50)
    bathrooms: int | None = Field(None, ge=0, le=50)
    year_built: int | None = Field(None, ge=1800, le=date.today().year + 5)
    address: str | None = Field(None, min_length=3, max_length=255)
    city_id: int | None = Field(None, gt=0)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    amenity_ids: list[int] | None = Field(None, max_length=50)
    images: list[ImageIn] | None = Field(None, max_length=MAX_IMAGES_PER_PROPERTY)


class StatusChange(BaseModel):
    status: PropertyStatus


class AgentListingParams(PageParams):
    status: PropertyStatus | None = None
