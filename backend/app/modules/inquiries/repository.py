from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption

from app.common.enums import InquiryStatus
from app.common.pagination import PageParams
from app.modules.inquiries.models import Inquiry
from app.modules.properties.models import Property
from app.repositories.base import BaseRepository, paginate

INQUIRY_LOAD: tuple[ExecutableOption, ...] = (selectinload(Inquiry.property), selectinload(Inquiry.user))


class InquiryRepository(BaseRepository[Inquiry]):
    model = Inquiry

    async def get_loaded(self, inquiry_id: int) -> Inquiry | None:
        stmt = select(Inquiry).where(Inquiry.id == inquiry_id).options(*INQUIRY_LOAD)
        return await self.session.scalar(stmt)

    async def for_agent(
        self, agent_id: int, params: PageParams, status: InquiryStatus | None
    ) -> tuple[list[Inquiry], int]:
        stmt = select(Inquiry).join(Inquiry.property).where(Property.agent_id == agent_id)
        if status:
            stmt = stmt.where(Inquiry.status == status)
        stmt = stmt.order_by(Inquiry.created_at.desc(), Inquiry.id.desc())
        return await paginate(self.session, stmt, params, *INQUIRY_LOAD)

    async def for_user(self, user_id: int, params: PageParams) -> tuple[list[Inquiry], int]:
        stmt = (
            select(Inquiry)
            .where(Inquiry.user_id == user_id)
            .order_by(Inquiry.created_at.desc(), Inquiry.id.desc())
        )
        return await paginate(self.session, stmt, params, *INQUIRY_LOAD)
