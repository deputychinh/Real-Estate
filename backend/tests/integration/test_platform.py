from httpx import AsyncClient

from tests.factories import World

API = "/api/v1"


async def test_health_reports_dependencies(client: AsyncClient) -> None:
    response = await client.get(f"{API}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "redis": "ok"}


async def test_unknown_route_uses_error_envelope_and_request_id(client: AsyncClient) -> None:
    response = await client.get(f"{API}/nope", headers={"X-Request-ID": "trace-123"})
    assert response.status_code == 404
    assert response.headers["X-Request-ID"] == "trace-123"
    assert response.json()["error"] == {
        "code": "NOT_FOUND",
        "message": "Not Found",
        "details": None,
        "request_id": "trace-123",
    }


async def test_unsafe_request_id_is_replaced(client: AsyncClient) -> None:
    response = await client.get(f"{API}/health", headers={"X-Request-ID": "bad id;rm"})
    assert response.headers["X-Request-ID"] != "bad id;rm"


async def test_lookups_and_rates(client: AsyncClient, world: World) -> None:
    countries = (await client.get(f"{API}/locations/countries")).json()["data"]
    assert [country["code"] for country in countries] == ["AE", "VN"]
    cities = (await client.get(f"{API}/locations/cities", params={"country": "vn"})).json()["data"]
    assert [city["slug"] for city in cities] == ["ho-chi-minh-city"]
    amenities = (await client.get(f"{API}/amenities")).json()["data"]
    assert {amenity["code"] for amenity in amenities} == {"pool", "gym"}
    rates = (await client.get(f"{API}/currencies/rates")).json()["data"]
    assert rates["base"] == "USD" and rates["usd_per_unit"]["USD"] == "1"
