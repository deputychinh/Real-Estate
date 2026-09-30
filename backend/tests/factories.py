from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import Currency, ListingPurpose, PropertyStatus, PropertyType, UserRole
from app.core.security import hash_password
from app.modules.amenities.models import Amenity
from app.modules.currency.rates import CurrencyConverter, StaticRateProvider
from app.modules.locations.models import City, Country
from app.modules.properties.models import Property, PropertyImage
from app.modules.users.models import User

PASSWORD = "Passw0rd!"
_converter = CurrencyConverter(StaticRateProvider())


@dataclass
class World:
    city_hcm: City
    city_dubai: City
    amenities: list[Amenity]
    investor: User
    agent: User
    other_agent: User
    admin: User
    listings: dict[str, Property] = field(default_factory=dict)


def make_property(
    agent: User,
    city: City,
    slug: str,
    *,
    price: str = "250000",
    currency: Currency = Currency.USD,
    purpose: ListingPurpose = ListingPurpose.SALE,
    property_type: PropertyType = PropertyType.APARTMENT,
    status: PropertyStatus = PropertyStatus.PUBLISHED,
    bedrooms: int = 2,
    area: str = "80",
    featured: bool = False,
    age_days: int = 0,
) -> Property:
    amount = Decimal(price)
    return Property(
        slug=slug,
        title=f"Listing {slug}",
        description="A bright home close to parks, schools and transport.",
        purpose=purpose,
        property_type=property_type,
        status=status,
        price=amount,
        currency=currency,
        price_usd=_converter.to_usd(amount, currency),
        area=Decimal(area),
        bedrooms=bedrooms,
        bathrooms=1,
        address="1 Test Street",
        city_id=city.id,
        agent_id=agent.id,
        is_featured=featured,
        published_at=datetime.now(UTC) - timedelta(days=age_days)
        if status == PropertyStatus.PUBLISHED
        else None,
        images=[PropertyImage(url=f"https://img.example.com/{slug}.jpg", sort_order=0, is_cover=True)],
    )


async def build_world(session: AsyncSession) -> World:
    vn, ae = Country(code="VN", name="Vietnam"), Country(code="AE", name="United Arab Emirates")
    session.add_all([vn, ae])
    await session.flush()
    hcm = City(country_id=vn.id, name="Ho Chi Minh City", slug="ho-chi-minh-city")
    dubai = City(country_id=ae.id, name="Dubai", slug="dubai")
    amenities = [Amenity(code="pool", name="Pool", icon="pool"), Amenity(code="gym", name="Gym", icon="gym")]
    hashed = hash_password(PASSWORD)
    users = [
        User(
            email=f"{role.lower()}@test.com",
            hashed_password=hashed,
            full_name=f"{role.title()} One",
            role=role,
        )
        for role in (UserRole.INVESTOR, UserRole.AGENT, UserRole.ADMIN)
    ]
    other_agent = User(
        email="agent2@test.com", hashed_password=hashed, full_name="Agent Two", role=UserRole.AGENT
    )
    session.add_all([hcm, dubai, *amenities, *users, other_agent])
    await session.flush()
    investor, agent, admin = users

    listings = {
        "hcm-apartment": make_property(
            agent, hcm, "hcm-apartment", price="250000", featured=True, age_days=3
        ),
        "hcm-villa": make_property(
            agent, hcm, "hcm-villa", price="9000000000", currency=Currency.VND,  # ≈ 355,500 USD
            property_type=PropertyType.VILLA, bedrooms=4, area="300", age_days=2,
        ),
        "hcm-rent": make_property(
            agent, hcm, "hcm-rent", price="1200", purpose=ListingPurpose.RENT, bedrooms=1, age_days=1
        ),
        "dubai-apartment": make_property(
            other_agent, dubai, "dubai-apartment", price="1000000", currency=Currency.AED, age_days=0
        ),  # ≈ 272,300 USD
        "hcm-draft": make_property(agent, hcm, "hcm-draft", status=PropertyStatus.DRAFT),
    }  # fmt: skip
    session.add_all(listings.values())
    await session.commit()
    return World(hcm, dubai, amenities, investor, agent, other_agent, admin, listings)


async def login(client: AsyncClient, email: str, password: str = PASSWORD) -> dict[str, str]:
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def listing_payload(city_id: int, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": "Sunny apartment in District 2",
        "description": "Two bedrooms, river view, walking distance to the metro station.",
        "purpose": "SALE",
        "property_type": "APARTMENT",
        "price": "320000.00",
        "currency": "USD",
        "area": "95.5",
        "bedrooms": 2,
        "bathrooms": 2,
        "address": "12 Thao Dien",
        "city_id": city_id,
        "images": [
            {"url": "https://img.example.com/new-1.jpg"},
            {"url": "https://img.example.com/new-2.jpg"},
        ],
    }
    payload.update(overrides)
    return payload
