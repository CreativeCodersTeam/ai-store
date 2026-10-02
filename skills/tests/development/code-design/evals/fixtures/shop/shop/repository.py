from typing import Dict, List, Optional

from .models import Order


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    def add(self, order: Order) -> None:
        self._orders[order.id] = order

    def get(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def update(self, order: Order) -> None:
        self._orders[order.id] = order

    def by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._orders.values() if o.customer_id == customer_id]
