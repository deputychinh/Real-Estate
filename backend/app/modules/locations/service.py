from app.cache import keys
from app.cache.cache_service import CacheService
from app.common.constants import CACHE_TTL_LOOKUP_SECONDS
from app.db.unit_of_work import UnitOfWork
from app.modules.amenities.schemas import AmenityRead
from app.modules.locations.schemas import CityRead, CountryRead
from app.modules.properties.mappers import city_read


class LookupService:
    """Reference data that rarely changes (countries, cities, amenities), cached for an hour."""

    def __init__(self, uow: UnitOfWork, cache: CacheService) -> None:
        self.uow = uow
        self.cache = cache

    async def countries(self) -> list[CountryRead]:
        key = keys.lookup("countries")
        if (cached := await self.cache.get_json(key)) is not None:
            return [CountryRead.model_validate(item) for item in cached]
        items = [CountryRead.model_validate(country) for country in await self.uow.locations.countries()]
        await self.cache.set_json(key, [item.model_dump() for item in items], CACHE_TTL_LOOKUP_SECONDS)
        return items

    async def cities(self, country_code: str | None) -> list[CityRead]:
        key = keys.lookup(f"cities:{(country_code or 'all').upper()}")
        if (cached := await self.cache.get_json(key)) is not None:
            return [CityRead.model_validate(item) for item in cached]
        items = [city_read(city) for city in await self.uow.locations.cities(country_code)]
        await self.cache.set_json(key, [item.model_dump() for item in items], CACHE_TTL_LOOKUP_SECONDS)
        return items

    async def amenities(self) -> list[AmenityRead]:
        key = keys.lookup("amenities")
        if (cached := await self.cache.get_json(key)) is not None:
            return [AmenityRead.model_validate(item) for item in cached]
        items = [AmenityRead.model_validate(amenity) for amenity in await self.uow.amenities.all()]
        await self.cache.set_json(key, [item.model_dump() for item in items], CACHE_TTL_LOOKUP_SECONDS)
        return items
