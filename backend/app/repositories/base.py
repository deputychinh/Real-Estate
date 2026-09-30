from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.common.pagination import PageParams
from app.db.base import Base


async def paginate[RowT](
    session: AsyncSession, stmt: Select[RowT], params: PageParams, *load: ExecutableOption
) -> tuple[list[RowT], int]:
    """Count + one page. The statement must already have a deterministic ORDER BY (ends with an id)."""
    total = await session.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    rows = await session.scalars(stmt.options(*load).offset(params.offset).limit(params.size))
    return list(rows), total or 0


class BaseRepository[ModelT: Base]:
    """Generic data access for one model. Repositories never commit; the Unit of Work does."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity_id: int) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()
