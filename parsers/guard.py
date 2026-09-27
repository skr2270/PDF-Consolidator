"""Circular ingestion guard: prevents processing already generated files."""
import re
import os
from typing import List

class CircularIngestionGuard:
    """Filters files to ensure only source transfer orders are ingested."""

    FORBIDDEN_PATTERNS = [
        r"^Consolidated",
        r"^Transfer_Order_",
        r"^HCT-TO-",
        r"manifest",
        r"checklist",
        r"^delta_",
    ]
    DEFAULT_ALLOW_PATTERN = r"^HCT-\d+\.pdf$"

    @classmethod
    def is_allowed(cls, filename: str, custom_allow_pattern: str = None) -> bool:
        base = os.path.basename(filename)
        for forbidden in cls.FORBIDDEN_PATTERNS:
            if re.search(forbidden, base, re.IGNORECASE):
                return False
        pattern = custom_allow_pattern or cls.DEFAULT_ALLOW_PATTERN
        return bool(re.search(pattern, base, re.IGNORECASE))

    @classmethod
    def filter_directory(cls, dir_path: str, custom_allow_pattern: str = None) -> List[str]:
        if not os.path.exists(dir_path):
            return []
        files = []
        for f in os.listdir(dir_path):
            full = os.path.join(dir_path, f)
            if os.path.isfile(full) and cls.is_allowed(f, custom_allow_pattern):
                files.append(full)
        return sorted(files)
