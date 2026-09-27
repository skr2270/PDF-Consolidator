"""3-Tuple (SKU, Cost Price, HSN) grouping engine."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from .sku_sanitizer import SKUSanitizer
from .math_verifier import MathVerifier
from parsers.base_parser import ParsedOrder

@dataclass
class ConsolidatedItem:
    item_name: str
    sku: str
    cost_price: float
    quantity: int
    subtotal: float
    hsn: str = ""
    bags: List[str] = field(default_factory=list)

@dataclass
class ConsignmentSummary:
    store_name: str
    destination: str
    dispatch_date: str
    total_orders: int
    total_bags: int
    total_skus: int
    total_pieces: int
    total_value: float
    items: List[ConsolidatedItem]
    orders: List[ParsedOrder]

class ItemGrouper:
    """Consolidates orders by grouping on (SKU, Cost Price, HSN)."""

    @classmethod
    def consolidate(cls, orders: List[ParsedOrder], store_name: str = "", dest_name: str = "") -> ConsignmentSummary:
        grouped: Dict[Tuple[str, float, str], Dict[str, Any]] = {}

        for order in orders:
            order_no = order.metadata.order_number
            for it in order.items:
                clean_sku = SKUSanitizer.sanitize(it.sku, it.item_name)
                key = (clean_sku, it.cost_price, it.hsn)

                if key not in grouped:
                    grouped[key] = {
                        "name": it.item_name,
                        "sku": clean_sku,
                        "cost_price": it.cost_price,
                        "quantity": 0,
                        "hsn": it.hsn,
                        "bags": set(),
                    }
                grouped[key]["quantity"] += it.quantity
                grouped[key]["bags"].add(order_no)

        consolidated_items: List[ConsolidatedItem] = []
        for key, val in grouped.items():
            qty = val["quantity"]
            rate = val["cost_price"]
            sub = round(qty * rate, 2)
            consolidated_items.append(ConsolidatedItem(
                item_name=val["name"],
                sku=val["sku"],
                cost_price=rate,
                quantity=qty,
                subtotal=sub,
                hsn=val["hsn"],
                bags=sorted(list(val["bags"])),
            ))

        consolidated_items.sort(key=lambda x: x.sku)

        total_pieces = sum(i.quantity for i in consolidated_items)
        total_value = round(sum(i.subtotal for i in consolidated_items), 2)
        total_orders = len(orders)

        source = store_name or (orders[0].metadata.source_warehouse if orders else "Store")
        dest = dest_name or (orders[0].metadata.destination_warehouse if orders else "Vanasthalipuram Store")
        date_str = orders[0].metadata.order_date if orders else "27/09/2026"

        return ConsignmentSummary(
            store_name=source,
            destination=dest,
            dispatch_date=date_str,
            total_orders=total_orders,
            total_bags=total_orders,
            total_skus=len(consolidated_items),
            total_pieces=total_pieces,
            total_value=total_value,
            items=consolidated_items,
            orders=orders,
        )
