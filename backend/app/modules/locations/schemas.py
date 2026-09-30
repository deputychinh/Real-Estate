from pydantic import BaseModel, ConfigDict


class CountryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class CityRead(BaseModel):
    id: int
    name: str
    slug: str
    country_code: str
    country_name: str
