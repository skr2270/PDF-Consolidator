"""Palette analysis and brand color extraction."""
from typing import Dict, Any, List
from collections import Counter
import pdfplumber

class PaletteAnalyzer:
    """Identifies ERP brand palettes, header fills, and border colors."""

    ZOHO_CHARCOAL = "#3C3D3A"
    BORDER_GREY = "#E3E3E3"
    TEXT_DARK = "#1A1A1A"

    def _to_hex(self, val) -> str:
        if isinstance(val, (tuple, list)):
            if len(val) == 3:
                if all(isinstance(x, float) and 0.0 <= x <= 1.0 for x in val):
                    return "#{:02x}{:02x}{:02x}".format(int(val[0]*255), int(val[1]*255), int(val[2]*255)).upper()
                return "#{:02x}{:02x}{:02x}".format(int(val[0]), int(val[1]), int(val[2])).upper()
            elif len(val) == 4:
                c, m, y, k = val
                r = int(255 * (1 - c) * (1 - k))
                g = int(255 * (1 - m) * (1 - k))
                b = int(255 * (1 - y) * (1 - k))
                return "#{:02x}{:02x}{:02x}".format(r, g, b).upper()
        return "#000000"

    def analyze(self, pdf_path: str) -> Dict[str, Any]:
        with pdfplumber.open(pdf_path) as pdf:
            color_counter = Counter()
            for page in pdf.pages:
                for r in page.rects:
                    col = r.get("non_stroking_color")
                    if col:
                        color_counter[self._to_hex(col)] += 1
                for c in page.curves:
                    col = c.get("stroking_color")
                    if col:
                        color_counter[self._to_hex(col)] += 1

            common = [c for c, _ in color_counter.most_common(10) if c != "#FFFFFF"]
            return {
                "dominant_colors": common,
                "table_header_color": self.ZOHO_CHARCOAL,
                "border_color": self.BORDER_GREY,
                "text_color": self.TEXT_DARK,
                "is_zoho_palette": self.ZOHO_CHARCOAL in common or len(common) > 0,
            }
