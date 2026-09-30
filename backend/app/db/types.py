from enum import StrEnum

from sqlalchemy import Enum as SAEnum


def str_enum(enum_cls: type[StrEnum]) -> SAEnum:
    """Store a StrEnum as VARCHAR of its values (portable, no native ENUM migrations)."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=20,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )
