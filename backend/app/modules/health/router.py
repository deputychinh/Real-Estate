from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import RedisDep, SessionDep

router = APIRouter(tags=["health"])


class HealthRead(BaseModel):
    status: str
    database: str
    redis: str


@router.get("/health", response_model=HealthRead, summary="Liveness + dependency check for the load balancer")
async def health(response: Response, session: SessionDep, redis: RedisDep) -> HealthRead:
    try:
        await session.execute(text("SELECT 1"))
        database = "ok"
    except SQLAlchemyError:
        database = "down"
    try:
        await redis.ping()
        redis_state = "ok"
    except RedisError:
        redis_state = "down"
    healthy = database == "ok" and redis_state == "ok"
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthRead(status="ok" if healthy else "degraded", database=database, redis=redis_state)
