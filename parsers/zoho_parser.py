"""Zoho Inventory Transfer Order Parser (multi-page)."""
import re
import os
import pdfplumber
from typing import List, Optional
from .base_parser import BaseParser, LineItem, OrderMetadata, ParsedOrder

class ZohoInventoryParser(BaseParser):
    """Parses native Zoho Inventory Transfer Order PDFs."""

    def can_parse(self, pdf_path: str) -> bool:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    return False
                t = (pdf.pages[0].extract_text() or "").upper()
                return "TRANSFER ORDER" in t or "SOURCE WAREHOUSE" in t or "HCT-" in t
        except Exception:
            return False

    def parse(self, pdf_path: str) -> ParsedOrder:
        all_text = ""
        pages_count = 0
        items: List[LineItem] = []

        with pdfplumber.open(pdf_path) as pdf:
            pages_count = len(pdf.pages)
            for page in pdf.pages:
                txt = page.extract_text() or ""
                all_text += txt + "\n"

        # 1. Metadata Extraction
        m_order = re.search(r"Transfer\s*Order#\s*:\s*([A-Za-z0-9\-]+)", all_text, re.IGNORECASE)
        if not m_order:
            m_order = re.search(r"(HCT-\d+)", os.path.basename(pdf_path))
        order_no = m_order.group(1).strip() if m_order else os.path.splitext(os.path.basename(pdf_path))[0]

        m_date = re.search(r"Date\s*:\s*(\d{2}/\d{2}/\d{4})", all_text, re.IGNORECASE)
        order_date = m_date.group(1).strip() if m_date else "27/09/2026"

        m_src = re.search(r"Source\s*Warehouse\s*:\s*([^\n\r]+)", all_text, re.IGNORECASE)
        source_wh = m_src.group(1).strip() if m_src else "Source Warehouse"

        m_dst = re.search(r"Destination\s*Warehouse\s*:\s*([^\n\r]+)", all_text, re.IGNORECASE)
        dest_wh = m_dst.group(1).strip() if m_dst else "Vanasthalipuram Store"

        m_qty = re.search(r"Total\s*Quantity\s*:\s*(\d+)", all_text, re.IGNORECASE)
        total_qty = int(m_qty.group(1)) if m_qty else 0

        m_sub = re.search(r"Sub\s*Total\s+([\d,]+\.\d{2})", all_text, re.IGNORECASE)
        sub_total = float(m_sub.group(1).replace(",", "")) if m_sub else 0.0

        m_grand = re.search(r"Total\s+[₹INR\s]*([\d,]+\.\d{2})", all_text, re.IGNORECASE)
        grand_total = float(m_grand.group(1).replace(",", "")) if m_grand else sub_total

        # 2. Line Items Extraction
        item_pattern = re.compile(
            r"^\s*(\d+)\s+([A-Za-z0-9\s\-\(\)\/\.\&]+?)\s+([A-Z0-9\-\.\/]+)\s+([\d,]+\.\d{2})\s+(\d+)\s+([\d,]+\.\d{2})",
            re.MULTILINE
        )

        for match in item_pattern.finditer(all_text):
            idx, raw_name, raw_sku, rate_str, qty_str, sub_str = match.groups()
            rate = float(rate_str.replace(",", ""))
            qty = int(qty_str)
            sub = float(sub_str.replace(",", ""))
            items.append(LineItem(
                item_name=raw_name.strip(),
                sku=raw_sku.strip(),
                cost_price=rate,
                quantity=qty,
                subtotal=sub,
                hsn="",
                raw_text=match.group(0).strip(),
            ))

        # Fallback to table extraction if regex missed items
        if not items:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for t in tables:
                        for row in t[1:]:
                            if len(row) >= 5 and row[0] and row[0].isdigit():
                                try:
                                    name_sku = str(row[1] or "").split("\n")
                                    name = name_sku[0].strip()
                                    sku = name_sku[1].strip() if len(name_sku) > 1 else name[:15]
                                    rate = float(str(row[2]).replace(",", "").replace("₹", "").strip())
                                    qty = int(str(row[3]).strip())
                                    sub = float(str(row[4]).replace(",", "").replace("₹", "").strip())
                                    items.append(LineItem(
                                        item_name=name,
                                        sku=sku,
                                        cost_price=rate,
                                        quantity=qty,
                                        subtotal=sub,
                                    ))
                                except Exception:
                                    continue

        calc_qty = sum(it.quantity for it in items)
        calc_total = round(sum(it.subtotal for it in items), 2)
        if total_qty == 0:
            total_qty = calc_qty
        if grand_total == 0.0:
            grand_total = calc_total
            sub_total = calc_total

        metadata = OrderMetadata(
            order_number=order_no,
            order_date=order_date,
            source_warehouse=source_wh,
            destination_warehouse=dest_wh,
            total_quantity=total_qty,
            sub_total=sub_total,
            grand_total=grand_total,
        )

        return ParsedOrder(
            metadata=metadata,
            items=items,
            file_path=pdf_path,
            page_count=pages_count,
        )
