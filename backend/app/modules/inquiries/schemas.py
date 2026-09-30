from datetime import datetime

from pydantic import BaseModel, Field

from app.common.constants import INQUIRY_MESSAGE_MAX_LENGTH
from app.common.enums import InquiryStatus
from app.common.pagination import PageParams
from app.modules.auth.schemas import PHONE_PATTERN


class InquiryCreate(BaseModel):
    message: str = Field(min_length=10, max_length=INQUIRY_MESSAGE_MAX_LENGTH)
    phone: str | None = Field(None, pattern=PHONE_PATTERN)


class InquiryStatusChange(BaseModel):
    status: InquiryStatus


class InquiryListParams(PageParams):
    status: InquiryStatus | None = None


class InquiryProperty(BaseModel):
    id: int
    slug: str
    title: str


class InquiryInvestor(BaseModel):
    id: int
    full_name: str
    email: str


class InquiryRead(BaseModel):
    id: int
    status: InquiryStatus
    message: str
    phone: str | None
    created_at: datetime
    property: InquiryProperty
    investor: InquiryInvestor
