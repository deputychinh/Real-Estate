"""initial schema

Revision ID: 2652db47d4e2
Revises:
Create Date: 2026-09-30 01:30:34.464731
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "2652db47d4e2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "amenities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("icon", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_amenities")),
        sa.UniqueConstraint("code", name=op.f("uq_amenities_code")),
    )
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_countries")),
        sa.UniqueConstraint("code", name=op.f("uq_countries_code")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column(
            "role",
            sa.Enum("INVESTOR", "AGENT", "ADMIN", name="userrole", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["country_id"], ["countries.id"], name=op.f("fk_cities_country_id_countries")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cities")),
        sa.UniqueConstraint("slug", name=op.f("uq_cities_slug")),
    )
    op.create_index(op.f("ix_cities_country_id"), "cities", ["country_id"], unique=False)
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "purpose",
            sa.Enum("SALE", "RENT", name="listingpurpose", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            "property_type",
            sa.Enum(
                "APARTMENT",
                "HOUSE",
                "VILLA",
                "OFFICE",
                "LAND",
                "COMMERCIAL",
                name="propertytype",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PUBLISHED",
                "SOLD",
                "RENTED",
                "ARCHIVED",
                name="propertystatus",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column(
            "currency",
            sa.Enum("USD", "EUR", "GBP", "VND", "AED", "SGD", name="currency", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("price_usd", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("area", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "area_unit", sa.Enum("SQM", "SQFT", name="areaunit", native_enum=False, length=20), nullable=False
        ),
        sa.Column("bedrooms", sa.Integer(), nullable=False),
        sa.Column("bathrooms", sa.Integer(), nullable=False),
        sa.Column("year_built", sa.Integer(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("city_id", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["users.id"], name=op.f("fk_properties_agent_id_users")),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], name=op.f("fk_properties_city_id_cities")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_properties")),
        sa.UniqueConstraint("slug", name=op.f("uq_properties_slug")),
    )
    op.create_index("ix_properties_agent_status", "properties", ["agent_id", "status"], unique=False)
    op.create_index("ix_properties_featured", "properties", ["is_featured", "published_at"], unique=False)
    op.create_index(
        "ix_properties_search",
        "properties",
        ["status", "purpose", "property_type", "city_id", "price_usd"],
        unique=False,
    )
    op.create_table(
        "favorites",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_favorites_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_favorites_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "property_id", name=op.f("pk_favorites")),
    )
    op.create_table(
        "inquiries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column(
            "status",
            sa.Enum("NEW", "CONTACTED", "CLOSED", name="inquirystatus", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_inquiries_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_inquiries_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inquiries")),
    )
    op.create_index(op.f("ix_inquiries_property_id"), "inquiries", ["property_id"], unique=False)
    op.create_index(op.f("ix_inquiries_user_id"), "inquiries", ["user_id"], unique=False)
    op.create_table(
        "property_amenities",
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("amenity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["amenity_id"],
            ["amenities.id"],
            name=op.f("fk_property_amenities_amenity_id_amenities"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_property_amenities_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("property_id", "amenity_id", name=op.f("pk_property_amenities")),
    )
    op.create_table(
        "property_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_cover", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_property_images_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_property_images")),
    )
    op.create_index(op.f("ix_property_images_property_id"), "property_images", ["property_id"], unique=False)


def downgrade() -> None:
    # Drop tables child-first. No explicit drop_index: MySQL refuses to drop an index a foreign key
    # still uses (error 1553), and dropping the table removes its indexes anyway.
    for table in (
        "property_images",
        "property_amenities",
        "inquiries",
        "favorites",
        "properties",
        "cities",
        "users",
        "countries",
        "amenities",
    ):
        op.drop_table(table)
