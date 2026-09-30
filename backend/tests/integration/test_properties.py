from httpx import AsyncClient

from tests.factories import World, listing_payload, login

API = "/api/v1"


async def slugs(client: AsyncClient, **params: object) -> list[str]:
    response = await client.get(f"{API}/properties", params=params)
    assert response.status_code == 200, response.text
    return [item["slug"] for item in response.json()["data"]]


async def test_search_returns_only_published_newest_first(client: AsyncClient, world: World) -> None:
    body = (await client.get(f"{API}/properties")).json()
    assert [item["slug"] for item in body["data"]] == [
        "dubai-apartment",
        "hcm-rent",
        "hcm-villa",
        "hcm-apartment",
    ]
    assert body["meta"] == {"page": 1, "size": 12, "total": 4, "pages": 1}
    assert body["data"][0]["city"]["country_code"] == "AE"


async def test_search_filters(client: AsyncClient, world: World) -> None:
    assert await slugs(client, purpose="RENT") == ["hcm-rent"]
    assert await slugs(client, property_type="VILLA") == ["hcm-villa"]
    assert await slugs(client, country="ae") == ["dubai-apartment"]
    assert await slugs(client, city="ho-chi-minh-city", bedrooms_min=3) == ["hcm-villa"]
    assert await slugs(client, q="villa") == ["hcm-villa"]
    assert await slugs(client, q="%") == []  # LIKE wildcards are escaped


async def test_price_filter_and_sort_work_across_currencies(client: AsyncClient, world: World) -> None:
    # 250,000 USD · VND villa ≈ 355,500 USD · AED apartment ≈ 272,300 USD
    assert await slugs(client, purpose="SALE", sort="PRICE_ASC") == [
        "hcm-apartment",
        "dubai-apartment",
        "hcm-villa",
    ]
    assert await slugs(client, purpose="SALE", price_min=260000, price_max=300000) == ["dubai-apartment"]
    in_aed = await slugs(client, purpose="SALE", price_min=1_200_000, price_currency="AED")  # ≥ 326,760 USD
    assert in_aed == ["hcm-villa"]


async def test_pagination_meta(client: AsyncClient, world: World) -> None:
    body = (await client.get(f"{API}/properties", params={"size": 3, "page": 2})).json()
    assert body["meta"] == {"page": 2, "size": 3, "total": 4, "pages": 2}
    assert len(body["data"]) == 1


async def test_invalid_search_params_return_422_envelope(client: AsyncClient) -> None:
    for params in ({"price_min": 10, "price_max": 5}, {"purpose": "LEASE"}, {"size": 500}):
        response = await client.get(f"{API}/properties", params=params)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_detail_featured_and_similar(client: AsyncClient, world: World) -> None:
    detail = await client.get(f"{API}/properties/hcm-apartment")
    assert detail.status_code == 200
    data = detail.json()["data"]
    assert data["agent"]["email"] == "agent@test.com" and data["images"][0]["is_cover"] is True
    assert data["price"] == "250000.00"  # money stays exact (string)

    featured = (await client.get(f"{API}/properties/featured")).json()["data"]
    assert [item["slug"] for item in featured] == ["hcm-apartment"]

    assert (await client.get(f"{API}/properties/hcm-draft")).status_code == 404
    assert (await client.get(f"{API}/properties/nope/similar")).status_code == 404


async def test_agent_creates_draft_then_publishes(client: AsyncClient, world: World) -> None:
    agent = await login(client, "agent@test.com")
    payload = listing_payload(world.city_hcm.id, amenity_ids=[a.id for a in world.amenities])
    created = await client.post(f"{API}/properties", json=payload, headers=agent)
    assert created.status_code == 201, created.text
    listing = created.json()["data"]
    assert listing["status"] == "DRAFT" and len(listing["amenities"]) == 2
    assert listing["cover_image_url"] == "https://img.example.com/new-1.jpg"
    assert (await client.get(f"{API}/properties/{listing['slug']}")).status_code == 404

    published = await client.post(f"{API}/properties/{listing['id']}/publish", headers=agent)
    assert published.status_code == 200
    assert published.json()["data"]["published_at"] is not None
    assert listing["slug"] in await slugs(client)


async def test_create_validates_input(client: AsyncClient, world: World) -> None:
    agent = await login(client, "agent@test.com")
    bad_city = await client.post(f"{API}/properties", json=listing_payload(9999), headers=agent)
    assert bad_city.status_code == 422
    bad_amenity = await client.post(
        f"{API}/properties", json=listing_payload(world.city_hcm.id, amenity_ids=[9999]), headers=agent
    )
    assert bad_amenity.status_code == 422
    negative = await client.post(
        f"{API}/properties", json=listing_payload(world.city_hcm.id, price="-1"), headers=agent
    )
    assert negative.status_code == 422
    investor = await login(client, "investor@test.com")
    assert (
        await client.post(f"{API}/properties", json=listing_payload(1), headers=investor)
    ).status_code == 403


async def test_publish_without_images_is_409(client: AsyncClient, world: World) -> None:
    agent = await login(client, "agent@test.com")
    created = await client.post(
        f"{API}/properties", json=listing_payload(world.city_hcm.id, images=[]), headers=agent
    )
    response = await client.post(f"{API}/properties/{created.json()['data']['id']}/publish", headers=agent)
    assert response.status_code == 409
    assert response.json()["error"]["details"]["missing"] == ["add at least one image"]


async def test_only_owner_or_admin_can_change_a_listing(client: AsyncClient, world: World) -> None:
    listing_id = world.listings["hcm-apartment"].id
    other = await login(client, "agent2@test.com")
    denied = await client.patch(
        f"{API}/properties/{listing_id}", json={"title": "Hijacked title"}, headers=other
    )
    assert denied.status_code == 403

    admin = await login(client, "admin@test.com")
    allowed = await client.patch(
        f"{API}/properties/{listing_id}", json={"title": "Renamed by admin"}, headers=admin
    )
    assert allowed.status_code == 200
    assert allowed.json()["data"]["title"] == "Renamed by admin"


async def test_update_invalidates_cached_search_and_detail(client: AsyncClient, world: World) -> None:
    await client.get(f"{API}/properties")  # warm the caches
    await client.get(f"{API}/properties/hcm-apartment")
    agent = await login(client, "agent@test.com")
    listing_id = world.listings["hcm-apartment"].id
    await client.patch(
        f"{API}/properties/{listing_id}", json={"price": "999", "currency": "USD"}, headers=agent
    )

    detail = (await client.get(f"{API}/properties/hcm-apartment")).json()["data"]
    assert detail["price"] == "999.00"
    assert await slugs(client, price_max=1000) == ["hcm-apartment"]


async def test_status_changes_and_soft_delete(client: AsyncClient, world: World) -> None:
    agent = await login(client, "agent@test.com")
    listing_id = world.listings["hcm-villa"].id
    sold = await client.patch(f"{API}/properties/{listing_id}/status", json={"status": "SOLD"}, headers=agent)
    assert sold.status_code == 200
    back = await client.patch(
        f"{API}/properties/{listing_id}/status", json={"status": "PUBLISHED"}, headers=agent
    )
    assert back.status_code == 409
    assert "hcm-villa" not in await slugs(client)

    rent_id = world.listings["hcm-rent"].id
    assert (await client.delete(f"{API}/properties/{rent_id}", headers=agent)).status_code == 204
    assert (await client.get(f"{API}/properties/hcm-rent")).status_code == 404
    assert (await client.delete(f"{API}/properties/{rent_id}", headers=agent)).status_code == 404


async def test_agent_sees_own_listings_in_any_status(client: AsyncClient, world: World) -> None:
    agent = await login(client, "agent@test.com")
    body = (await client.get(f"{API}/agents/me/properties", headers=agent)).json()
    assert body["meta"]["total"] == 4
    drafts = (
        await client.get(f"{API}/agents/me/properties", params={"status": "DRAFT"}, headers=agent)
    ).json()
    assert [item["slug"] for item in drafts["data"]] == ["hcm-draft"]

    draft_id = world.listings["hcm-draft"].id
    assert (await client.get(f"{API}/agents/me/properties/{draft_id}", headers=agent)).status_code == 200
    other = await login(client, "agent2@test.com")
    assert (await client.get(f"{API}/agents/me/properties/{draft_id}", headers=other)).status_code == 403
