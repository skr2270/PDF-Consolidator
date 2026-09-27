"""SKU standardization, casing, and whitespace normalization."""
import re

class SKUSanitizer:
    """Normalizes SKU strings across multi-branch ERP systems."""

    @staticmethod
    def sanitize(sku: str, item_name: str = "") -> str:
        if not sku or not str(sku).strip():
            clean_name = re.sub(r"[^A-Za-z0-9]", "", item_name).upper()
            return f"SKU-{clean_name[:12]}" if clean_name else "SKU-UNKNOWN"

        clean = str(sku).strip()
        clean = re.sub(r"[\u200b\u200c\u200d\uFEFF]", "", clean)
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip().upper()
