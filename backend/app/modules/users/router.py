from fastapi import APIRouter

from app.api.deps import CurrentUserDep
from app.common.responses import ERROR_RESPONSES, ApiResponse
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"], responses=ERROR_RESPONSES)


@router.get("/me", response_model=ApiResponse[UserRead])
async def me(user: CurrentUserDep) -> ApiResponse[UserRead]:
    return ApiResponse(data=UserRead.model_validate(user))
