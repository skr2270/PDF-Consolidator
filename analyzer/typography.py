"""Typography hierarchy, font detection, and sizing."""
from typing import Dict, Any
from collections import Counter
import pdfplumber

class TypographyAnalyzer:
    """Extracts typography hierarchy and verifies font family consistency."""

    def analyze(self, pdf_path: str) -> Dict[str, Any]:
        with pdfplumber.open(pdf_path) as pdf:
            fonts = Counter()
            sizes = Counter()
            for page in pdf.pages:
                for c in page.chars:
                    f_name = c.get("fontname", "Unknown")
                    size = round(float(c.get("size", 0.0)), 1)
                    fonts[f_name] += 1
                    sizes[size] += 1

            primary_font = fonts.most_common(1)[0][0] if fonts else "Helvetica"
            sorted_sizes = sorted(sizes.keys(), reverse=True)

            hierarchy = {
                "title_size": sorted_sizes[0] if sorted_sizes else 18.0,
                "header_size": sorted_sizes[1] if len(sorted_sizes) > 1 else 10.0,
                "body_size": sizes.most_common(1)[0][0] if sizes else 8.0,
                "caption_size": sorted_sizes[-1] if sorted_sizes else 7.0,
            }

            return {
                "primary_font": primary_font,
                "font_distribution": dict(fonts.most_common(8)),
                "size_distribution": dict(sizes.most_common(8)),
                "hierarchy": hierarchy,
                "has_ubuntu": any("ubuntu" in f.lower() for f in fonts.keys()),
            }
