"""Multi-branch consignment fleet orchestrator."""
from typing import List, Dict, Any
from consolidator.item_grouper import ConsignmentSummary

class FleetManager:
    """Aggregates multiple store consignments for a single vehicle dispatch."""

    def __init__(self, vehicle_id: str = "AP-39-TK-8821"):
        self.vehicle_id = vehicle_id
        self.branch_summaries: List[ConsignmentSummary] = []

    def add_branch_consignment(self, summary: ConsignmentSummary):
        self.branch_summaries.append(summary)

    def get_fleet_totals(self) -> Dict[str, Any]:
        return {
            "vehicle_id": self.vehicle_id,
            "branch_count": len(self.branch_summaries),
            "total_orders": sum(s.total_orders for s in self.branch_summaries),
            "total_bags": sum(s.total_bags for s in self.branch_summaries),
            "total_skus": sum(s.total_skus for s in self.branch_summaries),
            "total_pieces": sum(s.total_pieces for s in self.branch_summaries),
            "total_value": round(sum(s.total_value for s in self.branch_summaries), 2),
        }
