from sqlalchemy.exc import IntegrityError

from app.common.enums import PropertyStatus
from app.common.pagination import Page, PageParams
from app.core.exceptions import NotFoundError
from app.db.unit_of_work import UnitOfWork
from app.modules.favorites.models import Favorite
from app.modules.favorites.schemas import FavoriteStatus
from app.modules.properties.mappers import to_summary
from app.modules.properties.schemas import PropertySummary
from app.modules.users.models import User


class FavoriteService:
    """Add and remove are idempotent: repeating them returns the same result, never 409."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def add(self, user: User, property_id: int) -> FavoriteStatus:
        prop = await self.uow.properties.get(property_id)
        if prop is None or prop.deleted_at is not None or prop.status != PropertyStatus.PUBLISHED:
            raise NotFoundError("Listing not found")
        if await self.uow.favorites.get(user.id, property_id) is None:
            try:
                await self.uow.favorites.add(Favorite(user_id=user.id, property_id=property_id))
                await self.uow.commit()
            except IntegrityError:  # a parallel request added it first: same end state
                await self.uow.rollback()
        return FavoriteStatus(property_id=property_id, is_favorite=True)

    async def remove(self, user: User, property_id: int) -> FavoriteStatus:
        favorite = await self.uow.favorites.get(user.id, property_id)
        if favorite is not None:
            await self.uow.favorites.delete(favorite)
            await self.uow.commit()
        return FavoriteStatus(property_id=property_id, is_favorite=False)

    async def page(self, user: User, params: PageParams) -> Page[PropertySummary]:
        items, total = await self.uow.favorites.page(user.id, params)
        return Page[PropertySummary].build([to_summary(item) for item in items], total, params)

    async def ids(self, user: User) -> list[int]:
        return await self.uow.favorites.property_ids(user.id)
