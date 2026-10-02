import uuid
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Callable, Dict, List, Optional

from .models import Customer, Order, OrderLine
from .notifications import EmailSender
from .repository import InMemoryOrderRepository

TAX_RATES = {"DE": Decimal("0.19"), "AT": Decimal("0.20"), "FR": Decimal("0.20"), "CH": Decimal("0.081")}
FREE_SHIPPING_THRESHOLD = Decimal("50.00")
SHIPPING_FLAT = {"DE": Decimal("4.90"), "AT": Decimal("6.90"), "FR": Decimal("7.90"), "CH": Decimal("12.90")}
LOYALTY_DISCOUNT = Decimal("0.05")
MAX_QUANTITY_PER_LINE = 99
CANCELLATION_WINDOW = timedelta(hours=24)
CENT = Decimal("0.01")


class OrderError(Exception):
    pass


class OrderService:
    def __init__(
        self,
        repository: InMemoryOrderRepository,
        email_sender: EmailSender,
        clock: Callable[[], datetime] = datetime.utcnow,
    ) -> None:
        self._repository = repository
        self._email_sender = email_sender
        self._clock = clock

    # ------------------------------------------------------------------ placing

    def place_order(self, customer: Customer, lines: List[OrderLine]) -> Order:
        # validate
        if not lines:
            raise OrderError("an order needs at least one line")
        if customer.country not in TAX_RATES:
            raise OrderError(f"we do not ship to {customer.country}")
        seen = set()
        for line in lines:
            if line.quantity <= 0:
                raise OrderError(f"quantity for {line.sku} must be positive")
            if line.quantity > MAX_QUANTITY_PER_LINE:
                raise OrderError(f"quantity for {line.sku} exceeds {MAX_QUANTITY_PER_LINE}")
            if line.unit_price < 0:
                raise OrderError(f"price for {line.sku} must not be negative")
            if line.sku in seen:
                raise OrderError(f"duplicate line for {line.sku}")
            seen.add(line.sku)

        # price
        subtotal = sum((line.unit_price * line.quantity for line in lines), Decimal("0"))
        if customer.is_loyalty_member:
            subtotal = subtotal - (subtotal * LOYALTY_DISCOUNT)
        subtotal = subtotal.quantize(CENT, rounding=ROUND_HALF_UP)

        # shipping
        if subtotal >= FREE_SHIPPING_THRESHOLD:
            shipping = Decimal("0.00")
        else:
            shipping = SHIPPING_FLAT[customer.country]

        # tax
        tax = ((subtotal + shipping) * TAX_RATES[customer.country]).quantize(CENT, rounding=ROUND_HALF_UP)
        total = subtotal + shipping + tax

        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            lines=list(lines),
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            total=total,
            placed_at=self._clock(),
        )
        self._repository.add(order)

        # notify
        self._email_sender.send(
            customer.email,
            f"Your order {order.id[:8]}",
            self._format_confirmation(customer, order),
        )
        return order

    # --------------------------------------------------------------- cancelling

    def cancel_order(self, customer: Customer, order_id: str) -> Order:
        order = self._repository.get(order_id)
        if order is None or order.customer_id != customer.id:
            raise OrderError("order not found")
        if order.status != "placed":
            raise OrderError(f"order is {order.status}, cannot cancel")
        if self._clock() - order.placed_at > CANCELLATION_WINDOW:
            raise OrderError("cancellation window has passed")
        order.status = "cancelled"
        order.cancelled_at = self._clock()
        self._repository.update(order)
        self._email_sender.send(
            customer.email,
            f"Order {order.id[:8]} cancelled",
            f"Hello {customer.name},\n\nyour order {order.id[:8]} has been cancelled.\n"
            f"The amount of {order.total} EUR will be refunded within 5 days.\n",
        )
        return order

    # ---------------------------------------------------------------- refunding

    def refund(self, customer: Customer, order_id: str, amount: Decimal) -> Order:
        order = self._repository.get(order_id)
        if order is None or order.customer_id != customer.id:
            raise OrderError("order not found")
        if order.status not in ("placed", "shipped"):
            raise OrderError(f"order is {order.status}, cannot refund")
        if amount <= 0:
            raise OrderError("refund amount must be positive")
        if order.refunded_amount + amount > order.total:
            raise OrderError("refund exceeds order total")
        order.refunded_amount = (order.refunded_amount + amount).quantize(CENT)
        if order.refunded_amount == order.total:
            order.status = "refunded"
        self._repository.update(order)
        self._email_sender.send(
            customer.email,
            f"Refund for order {order.id[:8]}",
            f"Hello {customer.name},\n\nwe refunded {amount.quantize(CENT)} EUR for order {order.id[:8]}.\n",
        )
        return order

    # ---------------------------------------------------------------- reporting

    def order_history(self, customer: Customer) -> List[Order]:
        return sorted(self._repository.by_customer(customer.id), key=lambda o: o.placed_at, reverse=True)

    def lifetime_value(self, customer: Customer) -> Decimal:
        value = Decimal("0")
        for order in self._repository.by_customer(customer.id):
            if order.status == "cancelled":
                continue
            value += order.total - order.refunded_amount
        return value.quantize(CENT)

    def revenue_by_country(self, customers: Dict[str, Customer]) -> Dict[str, Decimal]:
        result: Dict[str, Decimal] = {}
        for customer in customers.values():
            result[customer.country] = result.get(customer.country, Decimal("0")) + self.lifetime_value(customer)
        return result

    # ----------------------------------------------------------------- helpers

    def _format_confirmation(self, customer: Customer, order: Order) -> str:
        rows = "\n".join(
            f"  {line.quantity:>3} x {line.sku:<12} {line.unit_price * line.quantity:>10.2f} EUR"
            for line in order.lines
        )
        loyalty = "  (includes 5% loyalty discount)\n" if customer.is_loyalty_member else ""
        return (
            f"Hello {customer.name},\n\n"
            f"thank you for your order {order.id[:8]}.\n\n"
            f"{rows}\n\n"
            f"  Subtotal: {order.subtotal:>10.2f} EUR\n"
            f"{loyalty}"
            f"  Shipping: {order.shipping:>10.2f} EUR\n"
            f"  Tax:      {order.tax:>10.2f} EUR\n"
            f"  Total:    {order.total:>10.2f} EUR\n"
        )

    def find_order(self, order_id: str) -> Optional[Order]:
        return self._repository.get(order_id)
