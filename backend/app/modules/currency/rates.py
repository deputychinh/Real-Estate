"""Exchange rates behind a small interface (Strategy). The MVP uses a static table; a live provider can
replace it without touching callers."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from app.common.enums import Currency

CENT = Decimal("0.01")


class RateProvider(Protocol):
    source: str
    as_of: date

    def usd_per_unit(self, currency: Currency) -> Decimal: ...


class StaticRateProvider:
    """Demo rates (USD value of one unit). Good enough for display and range filters."""

    source = "static"
    as_of = date(2026, 9, 1)
    _RATES: dict[Currency, Decimal] = {
        Currency.USD: Decimal("1"),
        Currency.EUR: Decimal("1.08"),
        Currency.GBP: Decimal("1.27"),
        Currency.SGD: Decimal("0.74"),
        Currency.AED: Decimal("0.2723"),
        Currency.VND: Decimal("0.0000395"),
    }

    def usd_per_unit(self, currency: Currency) -> Decimal:
        return self._RATES[currency]


class CurrencyConverter:
    def __init__(self, provider: RateProvider) -> None:
        self.provider = provider

    def to_usd(self, amount: Decimal, currency: Currency) -> Decimal:
        return (amount * self.provider.usd_per_unit(currency)).quantize(CENT, rounding=ROUND_HALF_UP)

    def from_usd(self, amount_usd: Decimal, currency: Currency) -> Decimal:
        return (amount_usd / self.provider.usd_per_unit(currency)).quantize(CENT, rounding=ROUND_HALF_UP)

    def rates(self) -> dict[Currency, Decimal]:
        return {currency: self.provider.usd_per_unit(currency) for currency in Currency}
