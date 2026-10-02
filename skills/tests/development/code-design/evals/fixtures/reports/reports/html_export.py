import html
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from .sales import Sale


def export_monthly_html(sales: List[Sale], year: int, month: int) -> str:
    """Monthly sales report as an HTML table (German number format)."""
    rows = [s for s in sales if s.day.year == year and s.day.month == month and not s.cancelled]
    rows.sort(key=lambda s: (s.day, s.region, s.product))

    out = [
        f"<h1>Umsatz {month:02d}/{year}</h1>",
        "<table>",
        "<tr><th>Datum</th><th>Region</th><th>Produkt</th><th>Menge</th><th>Umsatz</th></tr>",
    ]
    total_quantity = 0
    total_revenue = Decimal("0")
    by_region: Dict[str, Decimal] = {}
    for s in rows:
        revenue = (s.unit_price * s.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_quantity += s.quantity
        total_revenue += revenue
        by_region[s.region] = by_region.get(s.region, Decimal("0")) + revenue
        amount = f"{revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        out.append(
            f"<tr><td>{s.day.strftime('%d.%m.%Y')}</td><td>{html.escape(s.region)}</td>"
            f"<td>{html.escape(s.product)}</td><td>{s.quantity}</td><td>{amount}&nbsp;€</td></tr>"
        )

    total = f"{total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    out.append(f"<tr class=\"total\"><td>Summe</td><td></td><td></td><td>{total_quantity}</td><td>{total}&nbsp;€</td></tr>")
    out.append("</table>")
    out.append("<ul class=\"regions\">")
    for region in sorted(by_region):
        amount = f"{by_region[region]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        out.append(f"<li>{html.escape(region)}: {amount}&nbsp;€</li>")
    out.append("</ul>")
    return "\n".join(out) + "\n"
