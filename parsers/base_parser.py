"""Base parser abstractions and data schemas."""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class LineItem:
    item_name: str
    sku: str
    cost_price: float
    quantity: int
    subtotal: float
    hsn: str = ""
    raw_text: str = ""

@dataclass
class OrderMetadata:
    order_number: str
    order_date: str
    source_warehouse: str
    destination_warehouse: str
    source_address: str = ""
    dest_address: str = ""
    total_quantity: int = 0
    sub_total: float = 0.0
    grand_total: float = 0.0
    raw_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParsedOrder:
    metadata: OrderMetadata
    items: List[LineItem]
    file_path: str
    page_count: int

class BaseParser(ABC):
    @abstractmethod
    def can_parse(self, pdf_path: str) -> bool:
        """Return True if this parser can handle the given PDF."""
        pass

    @abstractmethod
    def parse(self, pdf_path: str) -> ParsedOrder:
        """Parse the PDF into a structured ParsedOrder."""
        pass
