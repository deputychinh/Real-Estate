"""ORM → API DTOs (adapter). The API shape can change without touching the tables, and back."""

from app.modules.amenities.schemas import AmenityRead
from app.modules.locations.models import City
from app.modules.locations.schemas import CityRead
from app.modules.properties.models import Property, PropertyImage
from app.modules.properties.schemas import AgentRead, ImageRead, PropertyDetail, PropertySummary


def city_read(city: City) -> CityRead:
    return CityRead(
        id=city.id,
        name=city.name,
        slug=city.slug,
        country_code=city.country.code,
        country_name=city.country.name,
    )


def cover_url(images: list[PropertyImage]) -> str | None:
    if not images:
        return None
    cover = next((image for image in images if image.is_cover), images[0])
    return cover.url


def to_summary(prop: Property) -> PropertySummary:
    return PropertySummary(
        id=prop.id,
        slug=prop.slug,
        title=prop.title,
        purpose=prop.purpose,
        property_type=prop.property_type,
        status=prop.status,
        price=prop.price,
        currency=prop.currency,
        price_usd=prop.price_usd,
        area=prop.area,
        area_unit=prop.area_unit,
        bedrooms=prop.bedrooms,
        bathrooms=prop.bathrooms,
        city=city_read(prop.city),
        cover_image_url=cover_url(prop.images),
        is_featured=prop.is_featured,
        published_at=prop.published_at,
    )


def to_detail(prop: Property) -> PropertyDetail:
    agent = prop.agent
    return PropertyDetail(
        **to_summary(prop).model_dump(),
        description=prop.description,
        address=prop.address,
        year_built=prop.year_built,
        latitude=prop.latitude,
        longitude=prop.longitude,
        images=[ImageRead(url=i.url, is_cover=i.is_cover, sort_order=i.sort_order) for i in prop.images],
        amenities=[AmenityRead.model_validate(a) for a in prop.amenities],
        agent=AgentRead(
            id=agent.id,
            full_name=agent.full_name,
            email=agent.email,
            phone=agent.phone,
            avatar_url=agent.avatar_url,
        ),
        created_at=prop.created_at,
        updated_at=prop.updated_at,
    )
