from fastapi import APIRouter

from app.api.deps import ConverterDep
from app.common.responses import ApiResponse
from app.modules.currency.schemas import RatesRead

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("/rates", response_model=ApiResponse[RatesRead], summary="Exchange rates used for display")
async def get_rates(converter: ConverterDep) -> ApiResponse[RatesRead]:
    provider = converter.provider
    return ApiResponse(
        data=RatesRead(usd_per_unit=converter.rates(), as_of=provider.as_of, source=provider.source)
    )
