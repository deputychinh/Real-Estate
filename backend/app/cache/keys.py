"""The only place cache keys are built. Search and featured keys embed a version number: a write bumps
the version, which makes every older key unreachable at once (no KEYS scan), and TTL cleans them up."""

SEARCH_VERSION_KEY = "property:search:version"


def property_detail(slug: str) -> str:
    return f"property:detail:{slug}"


def property_search(version: int, digest: str) -> str:
    return f"property:search:v{version}:{digest}"


def property_featured(version: int) -> str:
    return f"property:featured:v{version}"


def lookup(name: str) -> str:
    return f"lookup:{name}"


def fx_rates() -> str:
    return "fx:rates"


def rate_limit(scope: str, subject: str) -> str:
    return f"ratelimit:{scope}:{subject}"


def revoked_token(jti: str) -> str:
    return f"auth:revoked:{jti}"
