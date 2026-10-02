import unittest
from decimal import Decimal

from pricing.display import price_line
from pricing.models import Customer, Product
from pricing.prices import gross_price, volume_discount

LAMP = Product("L1", "Desk Lamp", Decimal("30.00"))
DE = Customer("c1", "DE")
US = Customer("c2", "US", currency="USD")


class PriceTests(unittest.TestCase):
    def test_volume_discount_tiers(self):
        self.assertEqual(volume_discount(9), Decimal("0"))
        self.assertEqual(volume_discount(10), Decimal("0.05"))
        self.assertEqual(volume_discount(50), Decimal("0.10"))

    def test_gross_price_includes_vat(self):
        self.assertEqual(gross_price(LAMP, 3, DE), Decimal("107.10"))

    def test_gross_price_without_vat(self):
        self.assertEqual(gross_price(LAMP, 10, US), Decimal("285.00"))


class DisplayTests(unittest.TestCase):
    def test_price_line_in_eur(self):
        self.assertEqual(price_line(LAMP, 3, DE), "3 x Desk Lamp: 107.10 EUR")


if __name__ == "__main__":
    unittest.main()
