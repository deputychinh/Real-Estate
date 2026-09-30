from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.locations.models import City, Country


class LocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def countries(self) -> list[Country]:
        return list(await self.session.scalars(select(Country).order_by(Country.name, Country.id)))

    async def cities(self, country_code: str | None) -> list[City]:
        stmt = select(City).join(City.country).order_by(City.name, City.id)
        if country_code:
            stmt = stmt.where(Country.code == country_code.upper())
        return list(await self.session.scalars(stmt))

    async def get_city(self, city_id: int) -> City | None:
        return await self.session.get(City, city_id)
