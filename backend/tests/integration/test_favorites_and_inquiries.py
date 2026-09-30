from httpx import AsyncClient

from tests.factories import World, login

API = "/api/v1"


async def test_favorites_are_idempotent(client: AsyncClient, world: World) -> None:
    investor = await login(client, "investor@test.com")
    listing_id = world.listings["hcm-apartment"].id
    for _ in range(2):
        added = await client.post(f"{API}/favorites/{listing_id}", headers=investor)
        assert added.status_code == 200 and added.json()["data"]["is_favorite"] is True

    assert (await client.get(f"{API}/favorites/ids", headers=investor)).json()["data"] == [listing_id]
    page = (await client.get(f"{API}/favorites", headers=investor)).json()
    assert page["meta"]["total"] == 1 and page["data"][0]["slug"] == "hcm-apartment"

    for _ in range(2):
        removed = await client.delete(f"{API}/favorites/{listing_id}", headers=investor)
        assert removed.json()["data"]["is_favorite"] is False
    assert (await client.get(f"{API}/favorites/ids", headers=investor)).json()["data"] == []


async def test_cannot_favorite_draft_or_without_login(client: AsyncClient, world: World) -> None:
    investor = await login(client, "investor@test.com")
    draft_id = world.listings["hcm-draft"].id
    assert (await client.post(f"{API}/favorites/{draft_id}", headers=investor)).status_code == 404
    assert (await client.post(f"{API}/favorites/{world.listings['hcm-apartment'].id}")).status_code == 401


async def test_inquiry_flow_from_investor_to_agent(client: AsyncClient, world: World) -> None:
    investor = await login(client, "investor@test.com")
    listing_id = world.listings["hcm-apartment"].id
    sent = await client.post(
        f"{API}/properties/{listing_id}/inquiries",
        json={"message": "Is the price negotiable?", "phone": "+84 90 123 4567"},
        headers=investor,
    )
    assert sent.status_code == 201, sent.text
    inquiry = sent.json()["data"]
    assert inquiry["status"] == "NEW" and inquiry["property"]["slug"] == "hcm-apartment"

    agent = await login(client, "agent@test.com")
    inbox = (await client.get(f"{API}/agents/me/inquiries", headers=agent)).json()
    assert [item["id"] for item in inbox["data"]] == [inquiry["id"]]
    other = await login(client, "agent2@test.com")
    assert (await client.get(f"{API}/agents/me/inquiries", headers=other)).json()["data"] == []

    url = f"{API}/inquiries/{inquiry['id']}"
    assert (await client.patch(url, json={"status": "CONTACTED"}, headers=other)).status_code == 403
    contacted = await client.patch(url, json={"status": "CONTACTED"}, headers=agent)
    assert contacted.json()["data"]["status"] == "CONTACTED"
    assert (await client.patch(url, json={"status": "NEW"}, headers=agent)).status_code == 409

    mine = (await client.get(f"{API}/inquiries/mine", headers=investor)).json()
    assert mine["data"][0]["status"] == "CONTACTED"


async def test_inquiry_rules(client: AsyncClient, world: World) -> None:
    body = {"message": "Hello, is this still available?"}
    listing_id = world.listings["hcm-apartment"].id
    agent = await login(client, "agent@test.com")
    as_agent = await client.post(f"{API}/properties/{listing_id}/inquiries", json=body, headers=agent)
    assert as_agent.status_code == 403

    investor = await login(client, "investor@test.com")
    draft = world.listings["hcm-draft"].id
    assert (
        await client.post(f"{API}/properties/{draft}/inquiries", json=body, headers=investor)
    ).status_code == 404
    short = await client.post(
        f"{API}/properties/{listing_id}/inquiries", json={"message": "hi"}, headers=investor
    )
    assert short.status_code == 422


async def test_inquiries_are_rate_limited_to_ten_per_hour(client: AsyncClient, world: World) -> None:
    investor = await login(client, "investor@test.com")
    url = f"{API}/properties/{world.listings['hcm-apartment'].id}/inquiries"
    body = {"message": "Hello, is this still available?"}
    statuses = [(await client.post(url, json=body, headers=investor)).status_code for _ in range(11)]
    assert statuses == [201] * 10 + [429]
