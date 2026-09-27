"""Unit tests for MathVerifier."""
import pytest
from consolidator.math_verifier import MathVerifier

def test_line_item_math():
    assert MathVerifier.verify_line_item(qty=10, rate=150.25, amount=1502.50) is True
    assert MathVerifier.verify_line_item(qty=3, rate=333.33, amount=999.99) is True
    assert MathVerifier.verify_line_item(qty=2, rate=100.0, amount=250.0) is False

def test_grand_total_math():
    subtotals = [100.50, 200.25, 300.00]
    ok, computed, diff = MathVerifier.verify_grand_total(subtotals, 600.75)
    assert ok is True
    assert computed == 600.75
    assert diff == 0.0
