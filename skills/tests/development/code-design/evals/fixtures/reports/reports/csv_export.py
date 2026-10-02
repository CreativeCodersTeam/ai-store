from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from .sales import Sale


def export_monthly_csv(sales: List[Sale], year: int, month: int) -> str:
    """Monthly sales report as CSV (semicolon-separated, German number format)."""
    rows = [s for s in sales if s.day.year == year and s.day.month == month and not s.cancelled]
    rows.sort(key=lambda s: (s.day, s.region, s.product))

    lines = ["Datum;Region;Produkt;Menge;Umsatz"]
    total_quantity = 0
    total_revenue = Decimal("0")
    by_region: Dict[str, Decimal] = {}
    for s in rows:
        revenue = (s.unit_price * s.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_quantity += s.quantity
        total_revenue += revenue
        by_region[s.region] = by_region.get(s.region, Decimal("0")) + revenue
        amount = f"{revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lines.append(f"{s.day.strftime('%d.%m.%Y')};{s.region};{s.product};{s.quantity};{amount} €")

    total = f"{total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    lines.append(f"Summe;;;{total_quantity};{total} €")
    for region in sorted(by_region):
        amount = f"{by_region[region]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lines.append(f"Region {region};;;;{amount} €")
    return "\n".join(lines) + "\n"
