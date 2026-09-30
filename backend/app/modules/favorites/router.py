from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUserDep, FavoriteServiceDep
from app.common.pagination import Page, PageParams
from app.common.responses import ERROR_RESPONSES, ApiResponse
from app.modules.favorites.schemas import FavoriteStatus
from app.modules.properties.schemas import PropertySummary

router = APIRouter(prefix="/favorites", tags=["favorites"], responses=ERROR_RESPONSES)


@router.get("", response_model=Page[PropertySummary], summary="My watchlist")
async def list_favorites(
    params: Annotated[PageParams, Query()], user: CurrentUserDep, service: FavoriteServiceDep
) -> Page[PropertySummary]:
    return await service.page(user, params)


@router.get("/ids", response_model=ApiResponse[list[int]], summary="Ids only, to colour the hearts on cards")
async def favorite_ids(user: CurrentUserDep, service: FavoriteServiceDep) -> ApiResponse[list[int]]:
    return ApiResponse(data=await service.ids(user))


@router.post("/{property_id}", response_model=ApiResponse[FavoriteStatus], summary="Idempotent add")
async def add(
    property_id: int, user: CurrentUserDep, service: FavoriteServiceDep
) -> ApiResponse[FavoriteStatus]:
    return ApiResponse(data=await service.add(user, property_id))


@router.delete("/{property_id}", response_model=ApiResponse[FavoriteStatus], summary="Idempotent remove")
async def remove(
    property_id: int, user: CurrentUserDep, service: FavoriteServiceDep
) -> ApiResponse[FavoriteStatus]:
    return ApiResponse(data=await service.remove(user, property_id))
