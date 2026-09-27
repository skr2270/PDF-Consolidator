"""Generic table extraction fallback parser."""
import pdfplumber
import os
from .base_parser import BaseParser, LineItem, OrderMetadata, ParsedOrder

class GenericTableParser(BaseParser):
    """Fallback parser that inspects tabular grids spatially for unknown ERP formats."""

    def can_parse(self, pdf_path: str) -> bool:
        return True

    def parse(self, pdf_path: str) -> ParsedOrder:
        items = []
        with pdfplumber.open(pdf_path) as pdf:
            pages = len(pdf.pages)
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:
                        clean_row = [str(c or "").strip() for c in row if str(c or "").strip()]
                        if len(clean_row) >= 4:
                            try:
                                name = clean_row[0]
                                qty = int(clean_row[-2].replace(",", ""))
                                rate = float(clean_row[-3].replace(",", "").replace("₹", ""))
                                sub = float(clean_row[-1].replace(",", "").replace("₹", ""))
                                items.append(LineItem(
                                    item_name=name,
                                    sku=name[:15].upper(),
                                    cost_price=rate,
                                    quantity=qty,
                                    subtotal=sub,
                                ))
                            except Exception:
                                continue

        total_qty = sum(i.quantity for i in items)
        total_amt = round(sum(i.subtotal for i in items), 2)
        base = os.path.splitext(os.path.basename(pdf_path))[0]

        return ParsedOrder(
            metadata=OrderMetadata(
                order_number=base,
                order_date="27/09/2026",
                source_warehouse="Source Warehouse",
                destination_warehouse="Destination Warehouse",
                total_quantity=total_qty,
                sub_total=total_amt,
                grand_total=total_amt,
            ),
            items=items,
            file_path=pdf_path,
            page_count=pages,
        )
