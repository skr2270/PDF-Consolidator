"""Page dimensions, printable margins, and spatial layout zones."""
from typing import Dict, Any, List
import pdfplumber

class GeometryAnalyzer:
    """Extracts page geometry, printable margins, and standard 6 layout zones."""

    A4_WIDTH = 595.28
    A4_HEIGHT = 841.89

    def analyze(self, pdf_path: str) -> Dict[str, Any]:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                raise ValueError(f"Empty PDF: {pdf_path}")
            p1 = pdf.pages[0]
            w = float(p1.width)
            h = float(p1.height)
            words = p1.extract_words()
            if words:
                min_x = min(item["x0"] for item in words)
                max_x = max(item["x1"] for item in words)
                min_y = min(item["top"] for item in words)
                max_y = max(item["bottom"] for item in words)
                margin_left = round(min_x, 2)
                margin_right = round(w - max_x, 2)
                margin_top = round(min_y, 2)
                margin_bottom = round(h - max_y, 2)
                printable_width = round(max_x - min_x, 2)
            else:
                margin_left = margin_right = 40.0
                margin_top = margin_bottom = 36.0
                printable_width = w - 80.0

            zones = {
                "header": {"top": 0.0, "bottom": 140.0, "description": "Logo, Title, Company Name"},
                "meta": {"top": 140.0, "bottom": 260.0, "description": "Order No, Date, Source/Dest Warehouses"},
                "table_header": {"top": 260.0, "bottom": 290.0, "description": "Dark charcoal header bar"},
                "table_body": {"top": 290.0, "bottom": h - 160.0, "description": "Line items & descriptions"},
                "totals_section": {"top": h - 160.0, "bottom": h - 60.0, "description": "Totals, Words, Signatures"},
                "footer": {"top": h - 60.0, "bottom": h, "description": "Running footer & page numbers"}
            }

            return {
                "page_count": len(pdf.pages),
                "width": round(w, 2),
                "height": round(h, 2),
                "is_a4": abs(w - self.A4_WIDTH) < 3.0 and abs(h - self.A4_HEIGHT) < 3.0,
                "orientation": "portrait" if h >= w else "landscape",
                "margins": {
                    "left": margin_left,
                    "right": margin_right,
                    "top": margin_top,
                    "bottom": margin_bottom,
                },
                "printable_width": printable_width,
                "zones": zones,
            }
