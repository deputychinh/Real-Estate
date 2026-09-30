"""Search as a specification object: each filter is one small, readable clause."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import Select
from sqlalchemy.sql.elements import ColumnElement, UnaryExpression

from app.common.enums import PropertySort, PropertyStatus
from app.modules.locations.models import City, Country
from app.modules.properties.models import Property
from app.modules.properties.schemas import PropertySearchParams

SORT_ORDER: dict[PropertySort, tuple[UnaryExpression[Any], ...]] = {
    PropertySort.NEWEST: (Property.published_at.desc(), Property.id.desc()),
    PropertySort.PRICE_ASC: (Property.price_usd.asc(), Property.id.asc()),
    PropertySort.PRICE_DESC: (Property.price_usd.desc(), Property.id.desc()),
    PropertySort.AREA_DESC: (Property.area.desc(), Property.id.desc()),
}


def public_listing() -> list[ColumnElement[bool]]:
    return [Property.status == PropertyStatus.PUBLISHED, Property.deleted_at.is_(None)]


@dataclass(frozen=True)
class PropertyFilter:
    params: PropertySearchParams
    price_min_usd: Decimal | None = None
    price_max_usd: Decimal | None = None

    def conditions(self) -> list[ColumnElement[bool]]:
        p = self.params
        clauses = public_listing()
        if p.purpose:
            clauses.append(Property.purpose == p.purpose)
        if p.property_type:
            clauses.append(Property.property_type == p.property_type)
        if p.country:
            clauses.append(Country.code == p.country.upper())
        if p.city:
            clauses.append(City.slug == p.city)
        if self.price_min_usd is not None:
            clauses.append(Property.price_usd >= self.price_min_usd)
        if self.price_max_usd is not None:
            clauses.append(Property.price_usd <= self.price_max_usd)
        if p.bedrooms_min is not None:
            clauses.append(Property.bedrooms >= p.bedrooms_min)
        if p.area_min is not None:
            clauses.append(Property.area >= p.area_min)
        if p.area_max is not None:
            clauses.append(Property.area <= p.area_max)
        if p.q:
            clauses.append(Property.title.icontains(p.q, autoescape=True))
        return clauses

    def apply(self, stmt: Select[Property]) -> Select[Property]:
        return stmt.join(Property.city).join(City.country).where(*self.conditions())

    def order_by(self) -> tuple[UnaryExpression[Any], ...]:
        return SORT_ORDER[self.params.sort]
