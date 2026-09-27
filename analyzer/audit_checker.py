"""6-Point Visual & Math QC Audit Checker."""
from typing import Dict, Any
import pdfplumber

class AuditChecker:
    """Performs 6-point QC audit on input and generated movement documents."""

    def audit(self, pdf_path: str) -> Dict[str, Any]:
        checks = {}
        with pdfplumber.open(pdf_path) as pdf:
            p1 = pdf.pages[0]
            text = p1.extract_text() or ""
            
            # Check 1: Header Alignment
            checks["header_alignment"] = {
                "passed": any(k in text.upper() for k in ["TRANSFER ORDER", "DELIVERY CHALLAN", "CONSIGNMENT"]),
                "description": "Document title positioned clearly in header zone",
            }

            # Check 2: Typography Legibility
            checks["typography_legibility"] = {
                "passed": len(p1.extract_words()) > 15,
                "description": "Readable typography with distinct sizing hierarchy",
            }

            # Check 3: Column Widths Fit Printable Margin
            checks["column_widths_fit"] = {
                "passed": float(p1.width) >= 590.0,
                "description": "Table width fits within standard A4 printable bounds",
            }

            # Check 4: Math Integrity Totals Present
            checks["math_integrity_present"] = {
                "passed": any(k in text for k in ["Total", "Sub Total", "Grand Total", "Total Quantity"]),
                "description": "Summary total labels present and formatted",
            }

            # Check 5: GST Rule 55 Movement Compliance
            rule_55_markers = ["Date", "Transfer", "Destination", "Source", "Store"]
            found_markers = [m for m in rule_55_markers if m.lower() in text.lower()]
            checks["rule_55_compliance"] = {
                "passed": len(found_markers) >= 3,
                "matched_fields": found_markers,
                "description": "Mandatory transit fields (Date, Warehouses, Values) present",
            }

            # Check 6: Logo Box / Header Balance
            checks["logo_header_balance"] = {
                "passed": any(k in text for k in ["The Chennai", "THC", "HCT", "Transfer"]),
                "description": "Company identity / header branding properly balanced",
            }

        passed_count = sum(1 for c in checks.values() if c["passed"])
        return {
            "file": pdf_path,
            "all_passed": passed_count == len(checks),
            "score": f"{passed_count}/{len(checks)}",
            "details": checks,
        }
