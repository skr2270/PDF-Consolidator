"""Unit tests for CircularIngestionGuard."""
import pytest
from parsers.guard import CircularIngestionGuard

def test_guard_filters_generated_files():
    assert CircularIngestionGuard.is_allowed("Consolidated.pdf") is False
    assert CircularIngestionGuard.is_allowed("Transfer_Order_Gajuwaka.pdf") is False
    assert CircularIngestionGuard.is_allowed("HCT-TO-SJN-260927.pdf") is False
    assert CircularIngestionGuard.is_allowed("master_manifest.pdf") is False

def test_guard_accepts_clean_source_orders():
    assert CircularIngestionGuard.is_allowed("HCT-637.pdf") is True
    assert CircularIngestionGuard.is_allowed("HCT-731.pdf") is True
    assert CircularIngestionGuard.is_allowed("HCT-12.pdf") is True
