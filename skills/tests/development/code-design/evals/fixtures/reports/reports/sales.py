from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Sale:
    day: date
    region: str
    product: str
    quantity: int
    unit_price: Decimal
    cancelled: bool = False
