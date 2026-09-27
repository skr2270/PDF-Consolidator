"""Delta processor: detects late-added bags and creates delta consignments."""
from typing import List, Set
from .item_grouper import ItemGrouper, ConsignmentSummary
from parsers.base_parser import ParsedOrder

class DeltaProcessor:
    """Identifies newly added orders and computes incremental delta consignments."""

    @classmethod
    def compute_delta(
        cls,
        all_orders: List[ParsedOrder],
        baseline_order_numbers: Set[str],
        store_name: str = ""
    ) -> ConsignmentSummary:
        delta_orders = [o for o in all_orders if o.metadata.order_number not in baseline_order_numbers]
        return ItemGrouper.consolidate(delta_orders, store_name=store_name)
