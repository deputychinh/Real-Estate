from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PageParams
from app.modules.favorites.models import Favorite
from app.modules.properties.models import Property
from app.modules.properties.repository import SUMMARY_LOAD
from app.repositories.base import paginate


class FavoriteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: int, property_id: int) -> Favorite | None:
        return await self.session.get(Favorite, (user_id, property_id))

    async def add(self, favorite: Favorite) -> None:
        self.session.add(favorite)
        await self.session.flush()

    async def delete(self, favorite: Favorite) -> None:
        await self.session.delete(favorite)
        await self.session.flush()

    async def property_ids(self, user_id: int) -> list[int]:
        stmt = select(Favorite.property_id).where(Favorite.user_id == user_id).order_by(Favorite.property_id)
        return list(await self.session.scalars(stmt))

    async def page(self, user_id: int, params: PageParams) -> tuple[list[Property], int]:
        stmt = (
            select(Property)
            .join(Favorite, Favorite.property_id == Property.id)
            .where(Favorite.user_id == user_id, Property.deleted_at.is_(None))
            .order_by(Favorite.created_at.desc(), Property.id.desc())
        )
        return await paginate(self.session, stmt, params, *SUMMARY_LOAD)
