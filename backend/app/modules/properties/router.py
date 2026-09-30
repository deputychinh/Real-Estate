from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import AgentDep, PropertyServiceDep
from app.common.enums import PropertyStatus
from app.common.pagination import Page
from app.common.responses import ERROR_RESPONSES, ApiResponse
from app.modules.properties.schemas import (
    AgentListingParams,
    PropertyCreate,
    PropertyDetail,
    PropertySearchParams,
    PropertySummary,
    PropertyUpdate,
    StatusChange,
)

router = APIRouter(prefix="/properties", tags=["properties"], responses=ERROR_RESPONSES)
agent_router = APIRouter(prefix="/agents/me", tags=["agent"], responses=ERROR_RESPONSES)


@router.get("", response_model=Page[PropertySummary], summary="Search published listings")
async def search(
    params: Annotated[PropertySearchParams, Query()], service: PropertyServiceDep
) -> Page[PropertySummary]:
    return await service.search(params)


@router.get("/featured", response_model=ApiResponse[list[PropertySummary]])
async def featured(service: PropertyServiceDep) -> ApiResponse[list[PropertySummary]]:
    return ApiResponse(data=await service.featured())


@router.get("/{slug}", response_model=ApiResponse[PropertyDetail], summary="Published listing by slug")
async def get_by_slug(slug: str, service: PropertyServiceDep) -> ApiResponse[PropertyDetail]:
    return ApiResponse(data=await service.get_published(slug))


@router.get("/{slug}/similar", response_model=ApiResponse[list[PropertySummary]])
async def similar(slug: str, service: PropertyServiceDep) -> ApiResponse[list[PropertySummary]]:
    return ApiResponse(data=await service.similar(slug))


@router.post("", response_model=ApiResponse[PropertyDetail], status_code=status.HTTP_201_CREATED)
async def create(
    payload: PropertyCreate, agent: AgentDep, service: PropertyServiceDep
) -> ApiResponse[PropertyDetail]:
    return ApiResponse(data=await service.create(agent, payload))


@router.patch("/{property_id}", response_model=ApiResponse[PropertyDetail])
async def update(
    property_id: int, payload: PropertyUpdate, user: AgentDep, service: PropertyServiceDep
) -> ApiResponse[PropertyDetail]:
    return ApiResponse(data=await service.update(user, property_id, payload))


@router.post(
    "/{property_id}/publish", response_model=ApiResponse[PropertyDetail], summary="DRAFT → PUBLISHED"
)
async def publish(
    property_id: int, user: AgentDep, service: PropertyServiceDep
) -> ApiResponse[PropertyDetail]:
    return ApiResponse(data=await service.change_status(user, property_id, PropertyStatus.PUBLISHED))


@router.patch("/{property_id}/status", response_model=ApiResponse[PropertyDetail])
async def change_status(
    property_id: int, payload: StatusChange, user: AgentDep, service: PropertyServiceDep
) -> ApiResponse[PropertyDetail]:
    return ApiResponse(data=await service.change_status(user, property_id, payload.status))


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete")
async def delete(property_id: int, user: AgentDep, service: PropertyServiceDep) -> None:
    await service.delete(user, property_id)


@agent_router.get("/properties", response_model=Page[PropertySummary], summary="My listings, any status")
async def my_listings(
    params: Annotated[AgentListingParams, Query()], agent: AgentDep, service: PropertyServiceDep
) -> Page[PropertySummary]:
    return await service.agent_listings(agent, params)


@agent_router.get("/properties/{property_id}", response_model=ApiResponse[PropertyDetail])
async def my_listing(
    property_id: int, agent: AgentDep, service: PropertyServiceDep
) -> ApiResponse[PropertyDetail]:
    return ApiResponse(data=await service.get_for_owner(agent, property_id))
