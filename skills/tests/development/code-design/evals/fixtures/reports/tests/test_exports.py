import unittest
from datetime import date
from decimal import Decimal

from reports.csv_export import export_monthly_csv
from reports.html_export import export_monthly_html
from reports.sales import Sale

SALES = [
    Sale(date(2026, 3, 2), "Süd", "Lampe", 2, Decimal("49.99")),
    Sale(date(2026, 3, 1), "Nord", "Tisch", 1, Decimal("1299.00")),
    Sale(date(2026, 3, 1), "Nord", "Stuhl", 4, Decimal("89.50")),
    Sale(date(2026, 3, 5), "Süd", "Tisch", 1, Decimal("1299.00"), cancelled=True),
    Sale(date(2026, 4, 1), "Nord", "Lampe", 1, Decimal("49.99")),
]


class CsvExportTests(unittest.TestCase):
    def test_full_report(self):
        self.assertEqual(
            export_monthly_csv(SALES, 2026, 3),
            "Datum;Region;Produkt;Menge;Umsatz\n"
            "01.03.2026;Nord;Stuhl;4;358,00 €\n"
            "01.03.2026;Nord;Tisch;1;1.299,00 €\n"
            "02.03.2026;Süd;Lampe;2;99,98 €\n"
            "Summe;;;7;1.756,98 €\n"
            "Region Nord;;;;1.657,00 €\n"
            "Region Süd;;;;99,98 €\n",
        )

    def test_empty_month(self):
        self.assertEqual(export_monthly_csv(SALES, 2026, 1), "Datum;Region;Produkt;Menge;Umsatz\nSumme;;;0;0,00 €\n")


class HtmlExportTests(unittest.TestCase):
    def test_totals_and_regions(self):
        out = export_monthly_html(SALES, 2026, 3)
        self.assertIn("<h1>Umsatz 03/2026</h1>", out)
        self.assertIn("<td>01.03.2026</td><td>Nord</td><td>Tisch</td><td>1</td><td>1.299,00&nbsp;€</td>", out)
        self.assertIn("<td>Summe</td><td></td><td></td><td>7</td><td>1.756,98&nbsp;€</td>", out)
        self.assertIn("<li>Süd: 99,98&nbsp;€</li>", out)
        self.assertNotIn("05.03.2026", out)

    def test_escapes_names(self):
        out = export_monthly_html([Sale(date(2026, 3, 1), "A&B", "<Tisch>", 1, Decimal("1"))], 2026, 3)
        self.assertIn("A&amp;B", out)
        self.assertIn("&lt;Tisch&gt;", out)


if __name__ == "__main__":
    unittest.main()
