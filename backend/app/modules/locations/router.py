from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import LookupServiceDep
from app.common.responses import ApiResponse
from app.modules.amenities.schemas import AmenityRead
from app.modules.locations.schemas import CityRead, CountryRead

router = APIRouter(tags=["lookups"])


@router.get("/locations/countries", response_model=ApiResponse[list[CountryRead]])
async def countries(service: LookupServiceDep) -> ApiResponse[list[CountryRead]]:
    return ApiResponse(data=await service.countries())


@router.get("/locations/cities", response_model=ApiResponse[list[CityRead]])
async def cities(
    service: LookupServiceDep,
    country: Annotated[str | None, Query(min_length=2, max_length=2, description="ISO country code")] = None,
) -> ApiResponse[list[CityRead]]:
    return ApiResponse(data=await service.cities(country))


@router.get("/amenities", response_model=ApiResponse[list[AmenityRead]])
async def amenities(service: LookupServiceDep) -> ApiResponse[list[AmenityRead]]:
    return ApiResponse(data=await service.amenities())
