"""Tally Prime Stock Journal Voucher Parser."""
import re
import pdfplumber
from .base_parser import BaseParser, LineItem, OrderMetadata, ParsedOrder

class TallyStockJournalParser(BaseParser):
    """Parses Tally Prime stock journal / transfer vouchers."""

    def can_parse(self, pdf_path: str) -> bool:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                txt = (pdf.pages[0].extract_text() or "").upper()
                return "STOCK JOURNAL" in txt or "TRANSFER OF MATERIALS" in txt or "TALLY" in txt
        except Exception:
            return False

    def parse(self, pdf_path: str) -> ParsedOrder:
        all_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for p in pdf.pages:
                all_text += (p.extract_text() or "") + "\n"

        m_vch = re.search(r"Voucher\s*No\.?\s*:\s*([^\n\r]+)", all_text, re.IGNORECASE)
        vch_no = m_vch.group(1).strip() if m_vch else "TALLY-001"

        m_date = re.search(r"Date\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})", all_text, re.IGNORECASE)
        vch_date = m_date.group(1).strip() if m_date else "27/09/2026"

        items = []
        pattern = re.compile(r"^\s*([A-Za-z0-9\s\-]+?)\s+(\d+)\s+Nos\s+([\d\.]+)\s+([\d\.]+)", re.MULTILINE)
        for m in pattern.finditer(all_text):
            name, qty, rate, amt = m.groups()
            items.append(LineItem(
                item_name=name.strip(),
                sku=name.strip().replace(" ", "-").upper()[:20],
                cost_price=float(rate),
                quantity=int(qty),
                subtotal=float(amt),
            ))

        total_qty = sum(i.quantity for i in items)
        total_amt = round(sum(i.subtotal for i in items), 2)

        return ParsedOrder(
            metadata=OrderMetadata(
                order_number=vch_no,
                order_date=vch_date,
                source_warehouse="Tally Source Godown",
                destination_warehouse="Tally Dest Godown",
                total_quantity=total_qty,
                sub_total=total_amt,
                grand_total=total_amt,
            ),
            items=items,
            file_path=pdf_path,
            page_count=1,
        )
