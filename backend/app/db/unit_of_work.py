from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.amenities.repository import AmenityRepository
from app.modules.favorites.repository import FavoriteRepository
from app.modules.inquiries.repository import InquiryRepository
from app.modules.locations.repository import LocationRepository
from app.modules.properties.repository import PropertyRepository
from app.modules.users.repository import UserRepository


class UnitOfWork:
    """One transaction per use case. Services read through the repositories and call commit() once."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.properties = PropertyRepository(session)
        self.locations = LocationRepository(session)
        self.amenities = AmenityRepository(session)
        self.favorites = FavoriteRepository(session)
        self.inquiries = InquiryRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
