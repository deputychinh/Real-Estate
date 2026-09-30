from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.common.enums import Currency


class RatesRead(BaseModel):
    base: Currency = Currency.USD
    usd_per_unit: dict[Currency, Decimal]
    as_of: date
    source: str
