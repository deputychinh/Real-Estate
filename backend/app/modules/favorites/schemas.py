from pydantic import BaseModel


class FavoriteStatus(BaseModel):
    property_id: int
    is_favorite: bool
