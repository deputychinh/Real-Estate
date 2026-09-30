from typing import Annotated

from fastapi import APIRouter, Cookie, Request, Response, status

from app.api.deps import AccessClaimsDep, AuthServiceDep, SettingsDep
from app.common.constants import REFRESH_COOKIE_NAME, REFRESH_COOKIE_PATH, SESSION_HINT_COOKIE_NAME
from app.common.responses import ERROR_RESPONSES, ApiResponse
from app.core.config import Settings
from app.core.security import TokenPair
from app.modules.auth.schemas import AccessTokenResponse, LoginRequest, RegisterRequest
from app.modules.users.models import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"], responses=ERROR_RESPONSES)
RefreshCookie = Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)]


def issue(
    response: Response, user: User, pair: TokenPair, settings: Settings
) -> ApiResponse[AccessTokenResponse]:
    """Access token in the body (kept in memory by the SPA); refresh token only in an httpOnly cookie."""
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        pair.refresh_token,
        max_age=pair.refresh_claims.seconds_left(),
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
    )
    response.set_cookie(
        SESSION_HINT_COOKIE_NAME,
        "1",
        max_age=pair.refresh_claims.seconds_left(),
        secure=settings.refresh_cookie_secure,
        samesite="lax",
    )
    return ApiResponse(
        data=AccessTokenResponse(
            access_token=pair.access_token,
            expires_in=pair.access_claims.seconds_left(),
            user=UserRead.model_validate(user),
        )
    )


@router.post("/register", response_model=ApiResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service: AuthServiceDep) -> ApiResponse[UserRead]:
    return ApiResponse(data=UserRead.model_validate(await service.register(payload)))


@router.post("/login", response_model=ApiResponse[AccessTokenResponse], summary="Rate limited per IP")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> ApiResponse[AccessTokenResponse]:
    client_ip = request.client.host if request.client else "unknown"
    user, pair = await service.login(payload, client_ip)
    return issue(response, user, pair, settings)


@router.post("/refresh", response_model=ApiResponse[AccessTokenResponse], summary="Rotate the token pair")
async def refresh(
    response: Response, service: AuthServiceDep, settings: SettingsDep, refresh_token: RefreshCookie = None
) -> ApiResponse[AccessTokenResponse]:
    user, pair = await service.refresh(refresh_token)
    return issue(response, user, pair, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response, claims: AccessClaimsDep, service: AuthServiceDep, refresh_token: RefreshCookie = None
) -> None:
    await service.logout(claims, refresh_token)
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)
    response.delete_cookie(SESSION_HINT_COOKIE_NAME)
