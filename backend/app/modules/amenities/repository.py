from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.amenities.models import Amenity


class AmenityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def all(self) -> list[Amenity]:
        return list(await self.session.scalars(select(Amenity).order_by(Amenity.name, Amenity.id)))

    async def by_ids(self, ids: list[int]) -> list[Amenity]:
        if not ids:
            return []
        return list(await self.session.scalars(select(Amenity).where(Amenity.id.in_(ids))))
