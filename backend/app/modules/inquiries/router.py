from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import AgentDep, CurrentUserDep, InquiryServiceDep, InvestorDep
from app.common.pagination import Page, PageParams
from app.common.responses import ERROR_RESPONSES, ApiResponse
from app.modules.inquiries.schemas import InquiryCreate, InquiryListParams, InquiryRead, InquiryStatusChange

router = APIRouter(tags=["inquiries"], responses=ERROR_RESPONSES)


@router.post(
    "/properties/{property_id}/inquiries",
    response_model=ApiResponse[InquiryRead],
    status_code=status.HTTP_201_CREATED,
    summary="Send an inquiry (investors, rate limited)",
)
async def create(
    property_id: int, payload: InquiryCreate, user: InvestorDep, service: InquiryServiceDep
) -> ApiResponse[InquiryRead]:
    return ApiResponse(data=await service.create(user, property_id, payload))


@router.get("/inquiries/mine", response_model=Page[InquiryRead], summary="Inquiries I sent")
async def mine(
    params: Annotated[PageParams, Query()], user: CurrentUserDep, service: InquiryServiceDep
) -> Page[InquiryRead]:
    return await service.mine(user, params)


@router.get("/agents/me/inquiries", response_model=Page[InquiryRead], summary="Inquiries on my listings")
async def for_agent(
    params: Annotated[InquiryListParams, Query()], agent: AgentDep, service: InquiryServiceDep
) -> Page[InquiryRead]:
    return await service.for_agent(agent, params)


@router.patch("/inquiries/{inquiry_id}", response_model=ApiResponse[InquiryRead])
async def change_status(
    inquiry_id: int, payload: InquiryStatusChange, agent: AgentDep, service: InquiryServiceDep
) -> ApiResponse[InquiryRead]:
    return ApiResponse(data=await service.change_status(agent, inquiry_id, payload.status))
