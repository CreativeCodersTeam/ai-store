"""Price rules for the product pages. All prices are kept in EUR."""
from decimal import ROUND_HALF_UP, Decimal

from .models import Customer, Product

VAT = {"DE": Decimal("0.19"), "AT": Decimal("0.20"), "CH": Decimal("0.081"), "US": Decimal("0")}
VOLUME_TIERS = [(50, Decimal("0.10")), (10, Decimal("0.05"))]
CENT = Decimal("0.01")


def volume_discount(quantity: int) -> Decimal:
    for minimum, rate in VOLUME_TIERS:
        if quantity >= minimum:
            return rate
    return Decimal("0")


def gross_price(product: Product, quantity: int, customer: Customer) -> Decimal:
    """Total gross price in EUR for `quantity` units, after volume discount and VAT."""
    net = product.net_price_eur * quantity * (1 - volume_discount(quantity))
    return (net * (1 + VAT[customer.country])).quantize(CENT, rounding=ROUND_HALF_UP)
