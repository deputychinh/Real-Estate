import math

from pydantic import BaseModel, Field

from app.common.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PageMeta(BaseModel):
    page: int
    size: int
    total: int
    pages: int


class Page[T](BaseModel):
    """List response envelope: `{"data": [...], "meta": {...}}`."""

    data: list[T]
    meta: PageMeta

    @classmethod
    def build(cls, items: list[T], total: int, params: PageParams) -> "Page[T]":
        pages = math.ceil(total / params.size) if total else 0
        return cls(data=items, meta=PageMeta(page=params.page, size=params.size, total=total, pages=pages))
