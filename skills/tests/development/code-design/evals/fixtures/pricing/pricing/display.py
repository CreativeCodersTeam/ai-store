"""Formats prices for the product page."""
from decimal import Decimal

from .models import Customer, Product
from .prices import gross_price


def format_eur(amount: Decimal) -> str:
    return f"{amount:,.2f} EUR"


def price_line(product: Product, quantity: int, customer: Customer) -> str:
    """The line shown under a product: '3 x Desk Lamp: 107.10 EUR'."""
    return f"{quantity} x {product.name}: {format_eur(gross_price(product, quantity, customer))}"
