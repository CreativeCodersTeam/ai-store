import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from shop.models import Customer, OrderLine
from shop.notifications import EmailSender
from shop.repository import InMemoryOrderRepository
from shop.service import OrderError, OrderService


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


def make_service(now=datetime(2026, 5, 1, 12, 0)):
    clock = FakeClock(now)
    repo = InMemoryOrderRepository()
    mail = EmailSender()
    return OrderService(repo, mail, clock), repo, mail, clock


ALICE = Customer("c1", "Alice", "alice@example.com", "DE")
BOB = Customer("c2", "Bob", "bob@example.com", "AT", is_loyalty_member=True)


class PlaceOrderTests(unittest.TestCase):
    def test_small_order_pays_shipping_and_tax(self):
        service, _, _, _ = make_service()
        order = service.place_order(ALICE, [OrderLine("BOOK", 2, Decimal("10.00"))])
        self.assertEqual(order.subtotal, Decimal("20.00"))
        self.assertEqual(order.shipping, Decimal("4.90"))
        self.assertEqual(order.tax, Decimal("4.73"))
        self.assertEqual(order.total, Decimal("29.63"))

    def test_large_order_ships_free(self):
        service, _, _, _ = make_service()
        order = service.place_order(ALICE, [OrderLine("LAMP", 1, Decimal("60.00"))])
        self.assertEqual(order.shipping, Decimal("0.00"))

    def test_loyalty_member_gets_five_percent(self):
        service, _, _, _ = make_service()
        order = service.place_order(BOB, [OrderLine("LAMP", 1, Decimal("100.00"))])
        self.assertEqual(order.subtotal, Decimal("95.00"))

    def test_rejects_unknown_country(self):
        service, _, _, _ = make_service()
        with self.assertRaises(OrderError):
            service.place_order(Customer("c3", "Carl", "c@example.com", "US"), [OrderLine("X", 1, Decimal("1"))])

    def test_rejects_duplicate_sku(self):
        service, _, _, _ = make_service()
        with self.assertRaises(OrderError):
            service.place_order(ALICE, [OrderLine("X", 1, Decimal("1")), OrderLine("X", 2, Decimal("1"))])

    def test_sends_confirmation(self):
        service, _, mail, _ = make_service()
        service.place_order(ALICE, [OrderLine("BOOK", 1, Decimal("10.00"))])
        self.assertEqual(len(mail.sent), 1)
        self.assertEqual(mail.sent[0][0], "alice@example.com")
        self.assertIn("Total:", mail.sent[0][2])


class CancelAndRefundTests(unittest.TestCase):
    def test_cancel_within_window(self):
        service, _, _, clock = make_service()
        order = service.place_order(ALICE, [OrderLine("BOOK", 1, Decimal("10.00"))])
        clock.now += timedelta(hours=2)
        self.assertEqual(service.cancel_order(ALICE, order.id).status, "cancelled")

    def test_cancel_after_window_fails(self):
        service, _, _, clock = make_service()
        order = service.place_order(ALICE, [OrderLine("BOOK", 1, Decimal("10.00"))])
        clock.now += timedelta(hours=25)
        with self.assertRaises(OrderError):
            service.cancel_order(ALICE, order.id)

    def test_full_refund_marks_refunded(self):
        service, _, _, _ = make_service()
        order = service.place_order(ALICE, [OrderLine("BOOK", 1, Decimal("10.00"))])
        self.assertEqual(service.refund(ALICE, order.id, order.total).status, "refunded")

    def test_lifetime_value_ignores_cancelled(self):
        service, _, _, _ = make_service()
        kept = service.place_order(ALICE, [OrderLine("BOOK", 1, Decimal("10.00"))])
        dropped = service.place_order(ALICE, [OrderLine("PEN", 1, Decimal("5.00"))])
        service.cancel_order(ALICE, dropped.id)
        self.assertEqual(service.lifetime_value(ALICE), kept.total)


if __name__ == "__main__":
    unittest.main()
