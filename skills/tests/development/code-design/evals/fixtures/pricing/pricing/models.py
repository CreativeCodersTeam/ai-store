from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    net_price_eur: Decimal


@dataclass(frozen=True)
class Customer:
    id: str
    country: str
    currency: str = "EUR"
