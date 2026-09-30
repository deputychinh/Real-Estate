import re
import unicodedata
import uuid

from app.common.constants import SLUG_MAX_LENGTH

_SUFFIX_LENGTH = 6


# Letters NFKD does not decompose into ASCII (Vietnamese đ).
_EXTRA = str.maketrans({"đ": "d", "Đ": "D"})


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text.translate(_EXTRA)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def unique_slug(title: str) -> str:
    """Readable slug with a short random suffix, so two listings with the same title never collide."""
    base = slugify(title)[: SLUG_MAX_LENGTH - _SUFFIX_LENGTH - 1].rstrip("-") or "listing"
    return f"{base}-{uuid.uuid4().hex[:_SUFFIX_LENGTH]}"
