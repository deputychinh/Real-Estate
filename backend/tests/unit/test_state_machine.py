import pytest

from app.common.enums import PropertyStatus as S
from app.core.exceptions import ConflictError
from app.modules.properties.state_machine import ensure_transition, publish_blockers


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (S.DRAFT, S.PUBLISHED),
        (S.PUBLISHED, S.SOLD),
        (S.PUBLISHED, S.RENTED),
        (S.RENTED, S.PUBLISHED),
        (S.SOLD, S.ARCHIVED),
    ],
)
def test_allowed_transitions(current: S, target: S) -> None:
    ensure_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"), [(S.DRAFT, S.SOLD), (S.SOLD, S.PUBLISHED), (S.ARCHIVED, S.PUBLISHED)]
)
def test_forbidden_transitions(current: S, target: S) -> None:
    with pytest.raises(ConflictError) as error:
        ensure_transition(current, target)
    assert error.value.details["allowed"]


def test_publish_needs_an_image() -> None:
    assert publish_blockers(image_count=0) == ["add at least one image"]
    assert publish_blockers(image_count=1) == []
