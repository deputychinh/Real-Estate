"""Listing lifecycle. Pure functions, so every rule is unit-tested without a database."""

from app.common.enums import PropertyStatus
from app.core.exceptions import ConflictError

ALLOWED_TRANSITIONS: dict[PropertyStatus, frozenset[PropertyStatus]] = {
    PropertyStatus.DRAFT: frozenset({PropertyStatus.PUBLISHED, PropertyStatus.ARCHIVED}),
    PropertyStatus.PUBLISHED: frozenset(
        {PropertyStatus.DRAFT, PropertyStatus.SOLD, PropertyStatus.RENTED, PropertyStatus.ARCHIVED}
    ),
    PropertyStatus.RENTED: frozenset({PropertyStatus.PUBLISHED, PropertyStatus.ARCHIVED}),
    PropertyStatus.SOLD: frozenset({PropertyStatus.ARCHIVED}),
    PropertyStatus.ARCHIVED: frozenset({PropertyStatus.DRAFT}),
}

PUBLIC_STATUSES = frozenset({PropertyStatus.PUBLISHED})


def ensure_transition(current: PropertyStatus, target: PropertyStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ConflictError(
            f"Cannot change status from {current} to {target}",
            details={"allowed": sorted(ALLOWED_TRANSITIONS[current])},
        )


def publish_blockers(image_count: int) -> list[str]:
    """Reasons a listing cannot be published yet (empty list = ready)."""
    blockers = []
    if image_count == 0:
        blockers.append("add at least one image")
    return blockers
