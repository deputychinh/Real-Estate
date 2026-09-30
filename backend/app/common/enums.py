"""Every closed set in the domain. Stored as strings in MySQL and mirrored in frontend/enums."""

from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class UserRole(StrEnum):
    INVESTOR = "INVESTOR"
    AGENT = "AGENT"
    ADMIN = "ADMIN"


class ListingPurpose(StrEnum):
    SALE = "SALE"
    RENT = "RENT"


class PropertyType(StrEnum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    VILLA = "VILLA"
    OFFICE = "OFFICE"
    LAND = "LAND"
    COMMERCIAL = "COMMERCIAL"


class PropertyStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    SOLD = "SOLD"
    RENTED = "RENTED"
    ARCHIVED = "ARCHIVED"


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    VND = "VND"
    AED = "AED"
    SGD = "SGD"


class AreaUnit(StrEnum):
    SQM = "SQM"
    SQFT = "SQFT"


class InquiryStatus(StrEnum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    CLOSED = "CLOSED"


class PropertySort(StrEnum):
    NEWEST = "NEWEST"
    PRICE_ASC = "PRICE_ASC"
    PRICE_DESC = "PRICE_DESC"
    AREA_DESC = "AREA_DESC"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class ErrorCode(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
