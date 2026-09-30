from httpx import AsyncClient

from app.common.constants import REFRESH_COOKIE_NAME, SESSION_HINT_COOKIE_NAME
from tests.factories import PASSWORD, World, login

AUTH = "/api/v1/auth"


async def test_register_then_login(client: AsyncClient, world: World) -> None:
    body = {"email": "New@Example.com", "password": "Secret123", "full_name": "New Investor"}
    created = await client.post(f"{AUTH}/register", json=body)
    assert created.status_code == 201
    assert created.json()["data"]["email"] == "new@example.com"
    assert "hashed_password" not in created.json()["data"]

    headers = await login(client, "new@example.com", "Secret123")
    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.json()["data"]["role"] == "INVESTOR"


async def test_register_rejects_duplicate_email_and_weak_password(client: AsyncClient, world: World) -> None:
    duplicate = await client.post(
        f"{AUTH}/register", json={"email": "agent@test.com", "password": "Secret123", "full_name": "Dup"}
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "CONFLICT"

    weak = await client.post(
        f"{AUTH}/register", json={"email": "x@test.com", "password": "onlyletters", "full_name": "X"}
    )
    assert weak.status_code == 422
    assert weak.json()["error"]["details"][0]["field"] == "password"

    admin = await client.post(
        f"{AUTH}/register",
        json={"email": "y@test.com", "password": "Secret123", "full_name": "Y", "role": "ADMIN"},
    )
    assert admin.status_code == 422


async def test_wrong_password_and_unknown_email_look_the_same(client: AsyncClient, world: World) -> None:
    wrong = await client.post(f"{AUTH}/login", json={"email": "agent@test.com", "password": "nope"})
    unknown = await client.post(f"{AUTH}/login", json={"email": "ghost@test.com", "password": "nope"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["error"]["message"] == unknown.json()["error"]["message"]


async def test_login_is_rate_limited_per_ip(client: AsyncClient, world: World) -> None:
    for _ in range(5):
        await client.post(f"{AUTH}/login", json={"email": "agent@test.com", "password": "nope"})
    blocked = await client.post(f"{AUTH}/login", json={"email": "agent@test.com", "password": PASSWORD})
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"
    assert int(blocked.headers["Retry-After"]) > 0


async def test_refresh_rotates_and_old_refresh_token_stops_working(client: AsyncClient, world: World) -> None:
    await login(client, "investor@test.com")
    old_refresh = client.cookies.get(REFRESH_COOKIE_NAME)
    assert old_refresh
    assert client.cookies.get(SESSION_HINT_COOKIE_NAME) == "1"

    rotated = await client.post(f"{AUTH}/refresh")
    assert rotated.status_code == 200
    assert client.cookies.get(REFRESH_COOKIE_NAME) != old_refresh

    client.cookies.set(REFRESH_COOKIE_NAME, old_refresh)
    reused = await client.post(f"{AUTH}/refresh")
    assert reused.status_code == 401


async def test_logout_revokes_access_token(client: AsyncClient, world: World) -> None:
    headers = await login(client, "investor@test.com")
    assert (await client.post(f"{AUTH}/logout", headers=headers)).status_code == 204
    assert client.cookies.get(SESSION_HINT_COOKIE_NAME) is None
    after = await client.get("/api/v1/users/me", headers=headers)
    assert after.status_code == 401
    assert (await client.post(f"{AUTH}/refresh")).status_code == 401


async def test_missing_token_is_401_and_wrong_role_is_403(client: AsyncClient, world: World) -> None:
    assert (await client.get("/api/v1/agents/me/properties")).status_code == 401
    investor = await login(client, "investor@test.com")
    forbidden = await client.get("/api/v1/agents/me/properties", headers=investor)
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"
