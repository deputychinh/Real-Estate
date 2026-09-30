"""Demo data: 6 countries, 14 cities, 10 amenities, 4 demo accounts and ~40 listings.

Run after migrations:  python -m scripts.seed          (adds data only when the database is empty)
                       python -m scripts.seed --reset  (deletes all rows first)
Deterministic (fixed random seed), so every environment shows the same catalogue.
"""

import argparse
import asyncio
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.models  # noqa: F401 - registers every table
from app.common.enums import Currency, ListingPurpose, PropertyStatus, PropertyType, UserRole
from app.common.slug import unique_slug
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import create_engine, create_session_factory
from app.modules.amenities.models import Amenity
from app.modules.currency.rates import CurrencyConverter, StaticRateProvider
from app.modules.locations.models import City, Country
from app.modules.properties.models import Property, PropertyImage
from app.modules.users.models import User

DEMO_PASSWORD = "Demo@1234"  # noqa: S105 - documented demo account, local data only
LISTINGS_PER_CITY = 3
converter = CurrencyConverter(StaticRateProvider())


@dataclass(frozen=True)
class Market:
    code: str
    name: str
    currency: Currency
    cities: dict[str, list[str]]  # city → districts used in titles
    sale_usd: tuple[int, int]  # typical sale price range in USD
    rent_usd: tuple[int, int]  # typical monthly rent in USD


MARKETS = [
    Market("VN", "Vietnam", Currency.VND, {
        "Ho Chi Minh City": ["Thao Dien", "District 1", "Phu My Hung"],
        "Hanoi": ["Tay Ho", "Ba Dinh", "Cau Giay"],
        "Da Nang": ["My Khe", "Son Tra", "Hai Chau"],
    }, (120_000, 900_000), (600, 3_500)),
    Market("SG", "Singapore", Currency.SGD, {
        "Singapore": ["Marina Bay", "Orchard", "Tiong Bahru"],
    }, (700_000, 4_000_000), (2_800, 9_000)),
    Market("AE", "United Arab Emirates", Currency.AED, {
        "Dubai": ["Downtown", "Dubai Marina", "Palm Jumeirah"],
        "Abu Dhabi": ["Saadiyat", "Al Reem Island", "Yas Island"],
    }, (300_000, 3_500_000), (1_800, 8_000)),
    Market("GB", "United Kingdom", Currency.GBP, {
        "London": ["Canary Wharf", "Chelsea", "Shoreditch"],
        "Manchester": ["Ancoats", "Spinningfields", "Salford Quays"],
    }, (350_000, 2_500_000), (1_800, 6_500)),
    Market("US", "United States", Currency.USD, {
        "New York": ["Brooklyn", "Upper West Side", "Tribeca"],
        "Miami": ["Brickell", "Coconut Grove", "Miami Beach"],
    }, (400_000, 3_000_000), (2_500, 9_500)),
    Market("PT", "Portugal", Currency.EUR, {
        "Lisbon": ["Chiado", "Alfama", "Parque das Nacoes"],
        "Porto": ["Ribeira", "Foz do Douro", "Boavista"],
    }, (250_000, 1_500_000), (1_300, 4_000)),
]  # fmt: skip

AMENITIES = [
    ("pool", "Swimming pool", "pool"),
    ("gym", "Gym", "dumbbell"),
    ("parking", "Parking", "car"),
    ("security", "24/7 security", "shield"),
    ("balcony", "Balcony", "sun"),
    ("garden", "Garden", "tree"),
    ("elevator", "Elevator", "arrow-up"),
    ("air_conditioning", "Air conditioning", "snowflake"),
    ("sea_view", "Sea view", "waves"),
    ("furnished", "Furnished", "sofa"),
]

TYPE_SHAPES: dict[PropertyType, tuple[tuple[int, int], tuple[int, int]]] = {
    # bedrooms range, area (m²) range
    PropertyType.APARTMENT: ((1, 3), (45, 140)),
    PropertyType.HOUSE: ((3, 5), (140, 320)),
    PropertyType.VILLA: ((4, 7), (280, 900)),
    PropertyType.OFFICE: ((0, 0), (80, 600)),
}
# Real estate photos (Unsplash, checked to return 200). Cover = exterior of the right type, then interiors.
UNSPLASH = "https://images.unsplash.com/photo-{}?w=1200&q=80&auto=format&fit=crop"
COVERS: dict[PropertyType, list[str]] = {
    PropertyType.APARTMENT: [
        "1545324418-cc1a3fa10c00",
        "1560448204-e02f11c3d0e2",
        "1522708323590-d24dbb6b0267",
    ],
    PropertyType.HOUSE: [
        "1564013799919-ab600027ffc6",
        "1570129477492-45c003edd2be",
        "1580587771525-78b9dba3b914",
    ],
    PropertyType.VILLA: [
        "1613490493576-7fde63acd811",
        "1613977257363-707ba9348227",
        "1512917774080-9991f1c4c750",
    ],
    PropertyType.OFFICE: [
        "1486406146926-c627a92ad1ab",
        "1497366216548-37526070297c",
        "1497366811353-6870744d04b2",
    ],
}
INTERIORS = [
    "1600596542815-ffad4c1539a9",
    "1600585154340-be6161a56a0c",
    "1600607687939-ce8a6c25118c",
    "1502672260266-1c1ef2d93688",
    "1493809842364-78817add7ffb",
    "1484154218962-a197022b5858",
    "1505691938895-1758d7feb511",
    "1600566753190-17f0baa2a6c3",
    "1600210492486-724fe5c67fb0",
    "1600047509807-ba8f99d2cdde",
]
ADJECTIVES = ["Bright", "Modern", "Quiet", "Spacious", "Renovated", "Elegant", "Sunny", "Cosy"]


def slug_of(name: str) -> str:
    return name.lower().replace(" ", "-")


def round_price(amount: Decimal) -> Decimal:
    """Round to a price an agent would actually ask (3 significant figures)."""
    digits = len(str(int(amount)))
    step = Decimal(10) ** max(digits - 3, 0)
    return (amount / step).quantize(Decimal(1)) * step


def listing(
    rng: random.Random, market: Market, city: City, district: str, *, agent: User, index: int
) -> Property:
    property_type = rng.choice(list(TYPE_SHAPES))
    purpose = ListingPurpose.RENT if rng.random() < 0.3 else ListingPurpose.SALE
    (bed_low, bed_high), (area_low, area_high) = TYPE_SHAPES[property_type]
    bedrooms = rng.randint(bed_low, bed_high)
    area = Decimal(rng.randint(area_low, area_high))
    usd_low, usd_high = market.sale_usd if purpose == ListingPurpose.SALE else market.rent_usd
    price = round_price(converter.from_usd(Decimal(rng.randint(usd_low, usd_high)), market.currency))
    title = f"{rng.choice(ADJECTIVES)} {property_type.value.lower()} in {district}, {city.name}"
    status = PropertyStatus.DRAFT if index % 11 == 0 else PropertyStatus.PUBLISHED
    slug = unique_slug(title)
    rooms = f"{bedrooms} bedroom{'s' if bedrooms != 1 else ''}" if bedrooms else "Open-plan space"
    audience = "owner-occupiers or investors" if purpose == ListingPurpose.SALE else "tenants"
    return Property(
        slug=slug,
        title=title,
        description=(
            f"{title}. {rooms} over {area} m², close to transport, schools and shops in {district}. "
            f"Well managed building with clear legal documents, ready for {audience}."
        ),
        purpose=purpose,
        property_type=property_type,
        status=status,
        price=price,
        currency=market.currency,
        price_usd=converter.to_usd(price, market.currency),
        area=area,
        bedrooms=bedrooms,
        bathrooms=max(1, bedrooms - rng.randint(0, 1)),
        year_built=rng.randint(1995, 2025),
        address=f"{rng.randint(1, 250)} {district} Street",
        city_id=city.id,
        agent_id=agent.id,
        is_featured=status == PropertyStatus.PUBLISHED and index % 5 == 0,
        published_at=datetime.now(UTC) - timedelta(days=index)
        if status == PropertyStatus.PUBLISHED
        else None,
        images=[
            PropertyImage(url=UNSPLASH.format(photo), sort_order=n, is_cover=n == 0)
            for n, photo in enumerate([rng.choice(COVERS[property_type]), *rng.sample(INTERIORS, k=2)])
        ],
    )


async def seed(session: AsyncSession) -> int:
    rng = random.Random(42)
    amenities = [Amenity(code=code, name=name, icon=icon) for code, name, icon in AMENITIES]
    hashed = hash_password(DEMO_PASSWORD)
    admin = User(email="admin@demo.com", full_name="Alex Admin", role=UserRole.ADMIN, hashed_password=hashed)
    agent = User(
        email="agent@demo.com",
        full_name="Linh Nguyen",
        phone="+84 90 111 2222",
        role=UserRole.AGENT,
        hashed_password=hashed,
        avatar_url="https://i.pravatar.cc/200?img=47",
    )
    agent2 = User(
        email="agent2@demo.com",
        full_name="Omar Haddad",
        phone="+971 50 123 4567",
        role=UserRole.AGENT,
        hashed_password=hashed,
        avatar_url="https://i.pravatar.cc/200?img=12",
    )
    investor = User(
        email="investor@demo.com", full_name="Sam Investor", role=UserRole.INVESTOR, hashed_password=hashed
    )
    session.add_all([*amenities, admin, agent, agent2, investor])

    index = 1
    for market in MARKETS:
        country = Country(code=market.code, name=market.name)
        session.add(country)
        await session.flush()
        for city_name, districts in market.cities.items():
            city = City(country_id=country.id, name=city_name, slug=slug_of(city_name))
            session.add(city)
            await session.flush()
            for district in districts[:LISTINGS_PER_CITY]:
                owner = agent if market.code in {"VN", "SG", "PT"} else agent2
                prop = listing(rng, market, city, district, agent=owner, index=index)
                prop.amenities = rng.sample(amenities, k=rng.randint(3, 6))
                session.add(prop)
                index += 1
    await session.commit()
    return index - 1


async def main(reset: bool) -> None:
    engine = create_engine(get_settings())
    try:
        async with create_session_factory(engine)() as session:
            if reset:
                for table in reversed(Base.metadata.sorted_tables):
                    await session.execute(delete(table))
                await session.commit()
            if await session.scalar(select(func.count()).select_from(Country)):
                print("Database already has data; use --reset to recreate it.")
                return
            count = await seed(session)
            print(f"Seeded {count} listings. Demo accounts use password {DEMO_PASSWORD}.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="delete all rows before seeding")
    asyncio.run(main(parser.parse_args().reset))
