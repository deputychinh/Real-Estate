from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption

from app.common.enums import PropertyStatus
from app.common.pagination import PageParams
from app.modules.properties.filters import PropertyFilter, public_listing
from app.modules.properties.models import Property
from app.repositories.base import BaseRepository, paginate

SUMMARY_LOAD: tuple[ExecutableOption, ...] = (selectinload(Property.city), selectinload(Property.images))
DETAIL_LOAD: tuple[ExecutableOption, ...] = (
    *SUMMARY_LOAD,
    selectinload(Property.amenities),
    selectinload(Property.agent),
)


class PropertyRepository(BaseRepository[Property]):
    model = Property

    async def search(self, spec: PropertyFilter) -> tuple[list[Property], int]:
        stmt = spec.apply(select(Property)).order_by(*spec.order_by())
        return await paginate(self.session, stmt, spec.params, *SUMMARY_LOAD)

    async def featured(self, limit: int) -> list[Property]:
        stmt = (
            select(Property)
            .where(*public_listing(), Property.is_featured.is_(True))
            .order_by(Property.published_at.desc(), Property.id.desc())
            .options(*SUMMARY_LOAD)
            .limit(limit)
        )
        return list(await self.session.scalars(stmt))

    async def get_published_by_slug(self, slug: str) -> Property | None:
        stmt = select(Property).where(*public_listing(), Property.slug == slug).options(*DETAIL_LOAD)
        return await self.session.scalar(stmt)

    async def get_detail(self, property_id: int) -> Property | None:
        """Any status, not deleted. Callers check who may see it."""
        stmt = (
            select(Property)
            .where(Property.id == property_id, Property.deleted_at.is_(None))
            .options(*DETAIL_LOAD)
            .execution_options(populate_existing=True)
        )
        return await self.session.scalar(stmt)

    async def similar(self, prop: Property, price_range: Decimal, limit: int) -> list[Property]:
        low, high = prop.price_usd * (1 - price_range), prop.price_usd * (1 + price_range)
        stmt = (
            select(Property)
            .where(
                *public_listing(),
                Property.id != prop.id,
                Property.city_id == prop.city_id,
                Property.property_type == prop.property_type,
                Property.purpose == prop.purpose,
                Property.price_usd.between(low, high),
            )
            .order_by(func.abs(Property.price_usd - prop.price_usd), Property.id)
            .options(*SUMMARY_LOAD)
            .limit(limit)
        )
        return list(await self.session.scalars(stmt))

    async def list_by_agent(
        self, agent_id: int, params: PageParams, status: PropertyStatus | None
    ) -> tuple[list[Property], int]:
        stmt = select(Property).where(Property.agent_id == agent_id, Property.deleted_at.is_(None))
        if status:
            stmt = stmt.where(Property.status == status)
        stmt = stmt.order_by(Property.updated_at.desc(), Property.id.desc())
        return await paginate(self.session, stmt, params, *SUMMARY_LOAD)
