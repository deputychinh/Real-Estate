from datetime import UTC, datetime

from app.cache import keys
from app.cache.cache_service import CacheService
from app.common.constants import (
    CACHE_TTL_FEATURED_SECONDS,
    CACHE_TTL_PROPERTY_DETAIL_SECONDS,
    CACHE_TTL_SEARCH_SECONDS,
    FEATURED_LIMIT,
    SIMILAR_LIMIT,
    SIMILAR_PRICE_RANGE,
)
from app.common.enums import PropertyStatus, UserRole
from app.common.pagination import Page
from app.common.slug import unique_slug
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.db.unit_of_work import UnitOfWork
from app.modules.amenities.models import Amenity
from app.modules.currency.rates import CurrencyConverter
from app.modules.properties.filters import PropertyFilter
from app.modules.properties.mappers import to_detail, to_summary
from app.modules.properties.models import Property, PropertyImage
from app.modules.properties.schemas import (
    AgentListingParams,
    ImageIn,
    PropertyCreate,
    PropertyDetail,
    PropertySearchParams,
    PropertySummary,
    PropertyUpdate,
)
from app.modules.properties.state_machine import ensure_transition, publish_blockers
from app.modules.users.models import User

_SCALAR_FIELDS = (
    "title", "description", "purpose", "property_type", "price", "currency", "area", "area_unit",
    "bedrooms", "bathrooms", "year_built", "address", "latitude", "longitude",
)  # fmt: skip


def ensure_can_manage(user: User, prop: Property) -> None:
    if user.role != UserRole.ADMIN and prop.agent_id != user.id:
        raise ForbiddenError("Only the listing's agent or an admin can change it")


def build_images(images: list[ImageIn]) -> list[PropertyImage]:
    """Keep the given order; the first image is the cover unless one is marked."""
    has_cover = any(image.is_cover for image in images)
    return [
        PropertyImage(
            url=str(image.url), sort_order=index, is_cover=image.is_cover or (not has_cover and index == 0)
        )
        for index, image in enumerate(images)
    ]


class PropertyService:
    def __init__(self, uow: UnitOfWork, cache: CacheService, converter: CurrencyConverter) -> None:
        self.uow = uow
        self.cache = cache
        self.converter = converter

    # ── Public reads (cache-aside) ──

    async def search(self, params: PropertySearchParams) -> Page[PropertySummary]:
        key = keys.property_search(await self.cache.search_version(), params.cache_digest())
        if (cached := await self.cache.get_json(key)) is not None:
            return Page[PropertySummary].model_validate(cached)

        to_usd = self.converter.to_usd
        spec = PropertyFilter(
            params=params,
            price_min_usd=to_usd(params.price_min, params.price_currency)
            if params.price_min is not None
            else None,
            price_max_usd=to_usd(params.price_max, params.price_currency)
            if params.price_max is not None
            else None,
        )
        items, total = await self.uow.properties.search(spec)
        page = Page[PropertySummary].build([to_summary(item) for item in items], total, params)
        await self.cache.set_json(key, page.model_dump(mode="json"), CACHE_TTL_SEARCH_SECONDS)
        return page

    async def featured(self) -> list[PropertySummary]:
        key = keys.property_featured(await self.cache.search_version())
        if (cached := await self.cache.get_json(key)) is not None:
            return [PropertySummary.model_validate(item) for item in cached]
        items = [to_summary(prop) for prop in await self.uow.properties.featured(FEATURED_LIMIT)]
        await self.cache.set_json(
            key, [item.model_dump(mode="json") for item in items], CACHE_TTL_FEATURED_SECONDS
        )
        return items

    async def get_published(self, slug: str) -> PropertyDetail:
        key = keys.property_detail(slug)
        if (cached := await self.cache.get_json(key)) is not None:
            return PropertyDetail.model_validate(cached)
        prop = await self.uow.properties.get_published_by_slug(slug)
        if prop is None:
            raise NotFoundError("Listing not found")
        detail = to_detail(prop)
        await self.cache.set_json(key, detail.model_dump(mode="json"), CACHE_TTL_PROPERTY_DETAIL_SECONDS)
        return detail

    async def similar(self, slug: str) -> list[PropertySummary]:
        prop = await self.uow.properties.get_published_by_slug(slug)
        if prop is None:
            raise NotFoundError("Listing not found")
        return [
            to_summary(item)
            for item in await self.uow.properties.similar(prop, SIMILAR_PRICE_RANGE, SIMILAR_LIMIT)
        ]

    # ── Agent writes ──

    async def create(self, agent: User, data: PropertyCreate) -> PropertyDetail:
        await self._ensure_city(data.city_id)
        prop = Property(
            slug=unique_slug(data.title),
            agent_id=agent.id,
            city_id=data.city_id,
            status=PropertyStatus.DRAFT,
            price_usd=self.converter.to_usd(data.price, data.currency),
            images=build_images(data.images),
            amenities=await self._amenities(data.amenity_ids),
            **data.model_dump(include=set(_SCALAR_FIELDS)),
        )
        await self.uow.properties.add(prop)
        await self.uow.commit()
        return await self._detail(prop.id)

    async def update(self, user: User, property_id: int, data: PropertyUpdate) -> PropertyDetail:
        prop = await self._manageable(user, property_id)
        changes = data.model_dump(exclude_unset=True)
        for field in _SCALAR_FIELDS:
            if field in changes:
                setattr(prop, field, changes[field])
        if "city_id" in changes:
            await self._ensure_city(changes["city_id"])
            prop.city_id = changes["city_id"]
        if data.images is not None:
            prop.images = build_images(data.images)
        if data.amenity_ids is not None:
            prop.amenities = await self._amenities(data.amenity_ids)
        prop.price_usd = self.converter.to_usd(prop.price, prop.currency)
        if prop.status == PropertyStatus.PUBLISHED and not prop.images:
            raise ConflictError("A published listing needs at least one image")
        await self.uow.commit()
        await self._invalidate(prop)
        return await self._detail(prop.id)

    async def change_status(self, user: User, property_id: int, target: PropertyStatus) -> PropertyDetail:
        prop = await self._manageable(user, property_id)
        ensure_transition(prop.status, target)
        if target == PropertyStatus.PUBLISHED:
            if blockers := publish_blockers(len(prop.images)):
                raise ConflictError("Listing is not ready to publish", details={"missing": blockers})
            prop.published_at = prop.published_at or datetime.now(UTC)
        prop.status = target
        await self.uow.commit()
        await self._invalidate(prop)
        return await self._detail(prop.id)

    async def delete(self, user: User, property_id: int) -> None:
        prop = await self._manageable(user, property_id)
        prop.deleted_at = datetime.now(UTC)
        await self.uow.commit()
        await self._invalidate(prop)

    async def agent_listings(self, agent: User, params: AgentListingParams) -> Page[PropertySummary]:
        items, total = await self.uow.properties.list_by_agent(agent.id, params, params.status)
        return Page[PropertySummary].build([to_summary(item) for item in items], total, params)

    async def get_for_owner(self, user: User, property_id: int) -> PropertyDetail:
        return to_detail(await self._manageable(user, property_id))

    # ── Helpers ──

    async def _manageable(self, user: User, property_id: int) -> Property:
        prop = await self.uow.properties.get_detail(property_id)
        if prop is None:
            raise NotFoundError("Listing not found")
        ensure_can_manage(user, prop)
        return prop

    async def _detail(self, property_id: int) -> PropertyDetail:
        prop = await self.uow.properties.get_detail(property_id)
        if prop is None:  # pragma: no cover - just written in the same request
            raise NotFoundError("Listing not found")
        return to_detail(prop)

    async def _ensure_city(self, city_id: int) -> None:
        if await self.uow.locations.get_city(city_id) is None:
            raise ValidationFailedError(
                "Unknown city", details=[{"field": "city_id", "message": "not found"}]
            )

    async def _amenities(self, amenity_ids: list[int]) -> list[Amenity]:
        amenities = await self.uow.amenities.by_ids(sorted(set(amenity_ids)))
        if len(amenities) != len(set(amenity_ids)):
            raise ValidationFailedError(
                "Unknown amenity", details=[{"field": "amenity_ids", "message": "one or more ids not found"}]
            )
        return amenities

    async def _invalidate(self, prop: Property) -> None:
        await self.cache.delete(keys.property_detail(prop.slug))
        await self.cache.bump_search_version()
