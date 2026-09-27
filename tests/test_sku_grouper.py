"""Unit tests for SKUSanitizer and ItemGrouper."""
import pytest
from consolidator.sku_sanitizer import SKUSanitizer
from consolidator.item_grouper import ItemGrouper
from parsers.base_parser import ParsedOrder, OrderMetadata, LineItem

def test_sku_sanitization():
    assert SKUSanitizer.sanitize("  abc-123  ") == "ABC-123"
    assert SKUSanitizer.sanitize("sku  spaced  out") == "SKU SPACED OUT"
    assert "SKU-" in SKUSanitizer.sanitize("", "Noise Smartwatch 2")

def test_item_consolidation():
    order1 = ParsedOrder(
        metadata=OrderMetadata("HCT-001", "27/09/2026", "Store A", "Store B", total_quantity=5, grand_total=500.0),
        items=[LineItem("Item X", "SKU-X", 100.0, 5, 500.0)],
        file_path="HCT-001.pdf",
        page_count=1,
    )
    order2 = ParsedOrder(
        metadata=OrderMetadata("HCT-002", "27/09/2026", "Store A", "Store B", total_quantity=3, grand_total=300.0),
        items=[LineItem("Item X", "SKU-X", 100.0, 3, 300.0)],
        file_path="HCT-002.pdf",
        page_count=1,
    )
    summary = ItemGrouper.consolidate([order1, order2], store_name="Store A")
    assert summary.total_pieces == 8
    assert summary.total_value == 800.0
    assert len(summary.items) == 1
    assert summary.items[0].quantity == 8
    assert summary.items[0].bags == ["HCT-001", "HCT-002"]
