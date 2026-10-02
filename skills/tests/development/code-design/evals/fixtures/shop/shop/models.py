from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    email: str
    country: str
    is_loyalty_member: bool = False


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: Decimal


@dataclass
class Order:
    id: str
    customer_id: str
    lines: List[OrderLine]
    subtotal: Decimal
    tax: Decimal
    shipping: Decimal
    total: Decimal
    status: str = "placed"
    placed_at: datetime = field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    refunded_amount: Decimal = Decimal("0")
