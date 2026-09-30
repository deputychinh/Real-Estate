"""Imports every model so Base.metadata is complete (Alembic autogenerate, test create_all)."""

from app.modules.amenities.models import Amenity
from app.modules.favorites.models import Favorite
from app.modules.inquiries.models import Inquiry
from app.modules.locations.models import City, Country
from app.modules.properties.models import Property, PropertyImage, property_amenities
from app.modules.users.models import User

__all__ = [
    "Amenity",
    "City",
    "Country",
    "Favorite",
    "Inquiry",
    "Property",
    "PropertyImage",
    "User",
    "property_amenities",
]
