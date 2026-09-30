from decimal import Decimal

from app.common.enums import Currency
from app.common.slug import slugify, unique_slug
from app.modules.currency.rates import CurrencyConverter, StaticRateProvider

converter = CurrencyConverter(StaticRateProvider())


def test_to_usd_rounds_to_cents() -> None:
    assert converter.to_usd(Decimal("9000000000"), Currency.VND) == Decimal("355500.00")
    assert converter.to_usd(Decimal("100"), Currency.USD) == Decimal("100.00")


def test_round_trip_is_stable() -> None:
    usd = converter.to_usd(Decimal("1000000"), Currency.AED)
    assert converter.from_usd(usd, Currency.AED) == Decimal("1000000.00")


def test_slugify_handles_vietnamese() -> None:
    assert slugify("Căn hộ Đẹp, Quận 1!") == "can-ho-dep-quan-1"


def test_unique_slug_adds_suffix() -> None:
    first, second = unique_slug("Villa"), unique_slug("Villa")
    assert first.startswith("villa-") and first != second
    assert unique_slug("!!!").startswith("listing-")
