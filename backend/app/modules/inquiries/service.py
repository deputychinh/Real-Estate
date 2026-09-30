from app.cache import keys
from app.cache.rate_limiter import RateLimiter
from app.common.constants import RATE_LIMIT_INQUIRY_PER_HOUR, RATE_LIMIT_INQUIRY_WINDOW_SECONDS
from app.common.enums import InquiryStatus, PropertyStatus, UserRole
from app.common.pagination import Page, PageParams
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.db.unit_of_work import UnitOfWork
from app.modules.inquiries.models import Inquiry
from app.modules.inquiries.schemas import (
    InquiryCreate,
    InquiryInvestor,
    InquiryListParams,
    InquiryProperty,
    InquiryRead,
)
from app.modules.users.models import User

INQUIRY_TRANSITIONS: dict[InquiryStatus, frozenset[InquiryStatus]] = {
    InquiryStatus.NEW: frozenset({InquiryStatus.CONTACTED, InquiryStatus.CLOSED}),
    InquiryStatus.CONTACTED: frozenset({InquiryStatus.CLOSED}),
    InquiryStatus.CLOSED: frozenset(),
}


def to_read(inquiry: Inquiry) -> InquiryRead:
    return InquiryRead(
        id=inquiry.id,
        status=inquiry.status,
        message=inquiry.message,
        phone=inquiry.phone,
        created_at=inquiry.created_at,
        property=InquiryProperty(
            id=inquiry.property.id, slug=inquiry.property.slug, title=inquiry.property.title
        ),
        investor=InquiryInvestor(
            id=inquiry.user.id, full_name=inquiry.user.full_name, email=inquiry.user.email
        ),
    )


class InquiryService:
    def __init__(self, uow: UnitOfWork, limiter: RateLimiter) -> None:
        self.uow = uow
        self.limiter = limiter

    async def create(self, user: User, property_id: int, data: InquiryCreate) -> InquiryRead:
        await self.limiter.hit(
            keys.rate_limit("inquiry", str(user.id)),
            RATE_LIMIT_INQUIRY_PER_HOUR,
            RATE_LIMIT_INQUIRY_WINDOW_SECONDS,
        )
        prop = await self.uow.properties.get(property_id)
        if prop is None or prop.deleted_at is not None or prop.status != PropertyStatus.PUBLISHED:
            raise NotFoundError("Listing not found")
        inquiry = Inquiry(
            property_id=prop.id, user_id=user.id, message=data.message, phone=data.phone or user.phone
        )
        await self.uow.inquiries.add(inquiry)
        await self.uow.commit()
        return await self._read(inquiry.id)

    async def for_agent(self, agent: User, params: InquiryListParams) -> Page[InquiryRead]:
        items, total = await self.uow.inquiries.for_agent(agent.id, params, params.status)
        return Page[InquiryRead].build([to_read(item) for item in items], total, params)

    async def mine(self, user: User, params: PageParams) -> Page[InquiryRead]:
        items, total = await self.uow.inquiries.for_user(user.id, params)
        return Page[InquiryRead].build([to_read(item) for item in items], total, params)

    async def change_status(self, user: User, inquiry_id: int, target: InquiryStatus) -> InquiryRead:
        inquiry = await self.uow.inquiries.get_loaded(inquiry_id)
        if inquiry is None:
            raise NotFoundError("Inquiry not found")
        if user.role != UserRole.ADMIN and inquiry.property.agent_id != user.id:
            raise ForbiddenError("Only the listing's agent can update this inquiry")
        if target not in INQUIRY_TRANSITIONS[inquiry.status]:
            raise ConflictError(f"Cannot change inquiry from {inquiry.status} to {target}")
        inquiry.status = target
        await self.uow.commit()
        return await self._read(inquiry.id)

    async def _read(self, inquiry_id: int) -> InquiryRead:
        self.uow.session.expire_all()  # reload server defaults (created_at) and relationships
        inquiry = await self.uow.inquiries.get_loaded(inquiry_id)
        if inquiry is None:  # pragma: no cover - just written in the same request
            raise NotFoundError("Inquiry not found")
        return to_read(inquiry)
