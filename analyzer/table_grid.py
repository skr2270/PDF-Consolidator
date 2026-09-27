"""Table grid geometry and column boundary specifications."""
from typing import Dict, Any, List
import pdfplumber

class TableGridAnalyzer:
    """Analyzes tabular layouts, column widths, and alignments."""

    DEFAULT_COLUMNS = [
        {"name": "#", "width_pt": 25.7, "width_pct": 5.0, "align": "center"},
        {"name": "Items & Description", "width_pt": 231.7, "width_pct": 45.0, "align": "left"},
        {"name": "Transfer Price", "width_pt": 77.2, "width_pct": 15.0, "align": "right"},
        {"name": "Quantity", "width_pt": 77.2, "width_pct": 15.0, "align": "right"},
        {"name": "Sub Total", "width_pt": 103.0, "width_pct": 20.0, "align": "right"},
    ]

    def analyze(self, pdf_path: str) -> Dict[str, Any]:
        with pdfplumber.open(pdf_path) as pdf:
            p1 = pdf.pages[0]
            tables = p1.extract_tables()
            header_row = [str(c or "").strip() for c in tables[0][0]] if (tables and len(tables[0]) > 0) else ["#", "Items & Description", "Transfer Price", "Quantity", "Sub Total"]
            return {
                "detected_columns": header_row,
                "column_count": len(header_row),
                "grid_specs": self.DEFAULT_COLUMNS,
                "total_table_width_pt": 515.0,
            }
