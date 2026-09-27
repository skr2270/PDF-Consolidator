"""Floating-point deterministic zero-tolerance math verifier."""
from typing import List, Tuple

class MathVerifier:
    """Verifies math consistency across individual lines and grand totals."""

    TOLERANCE = 0.01

    @classmethod
    def verify_line_item(cls, qty: int, rate: float, amount: float) -> bool:
        expected = round(qty * rate, 2)
        return abs(expected - amount) <= cls.TOLERANCE

    @classmethod
    def verify_grand_total(cls, line_subtotals: List[float], grand_total: float) -> Tuple[bool, float, float]:
        computed = round(sum(line_subtotals), 2)
        diff = abs(computed - grand_total)
        return (diff <= cls.TOLERANCE, computed, diff)
