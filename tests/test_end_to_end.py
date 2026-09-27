"""End-to-End integration test for the complete PDF Consolidator suite."""
import os
import pytest
from parsers.base_parser import ParsedOrder, OrderMetadata, LineItem
from consolidator.item_grouper import ItemGrouper
from generator.pdf_builder import PDFBuilder
from generator.excel_exporter import ExcelExporter
from generator.manifest_builder import ManifestBuilder
from analyzer.geometry import GeometryAnalyzer
from analyzer.typography import TypographyAnalyzer
from analyzer.palette import PaletteAnalyzer
from analyzer.table_grid import TableGridAnalyzer
from analyzer.audit_checker import AuditChecker
from fleet.fleet_manager import FleetManager
from db.database import DatabaseManager

def test_full_pipeline_end_to_end(tmp_path):
    order1 = ParsedOrder(
        metadata=OrderMetadata(
            order_number="HCT-101",
            order_date="27/09/2026",
            source_warehouse="Gajuwaka Store",
            destination_warehouse="Vanasthalipuram Store",
            total_quantity=5,
            sub_total=5000.0,
            grand_total=5000.0,
        ),
        items=[
            LineItem(item_name="Samsung Galaxy S24 Ultra", sku="SAM-S24U-256", cost_price=1000.0, quantity=5, subtotal=5000.0)
        ],
        file_path="HCT-101.pdf",
        page_count=1,
    )

    order2 = ParsedOrder(
        metadata=OrderMetadata(
            order_number="HCT-102",
            order_date="27/09/2026",
            source_warehouse="Gajuwaka Store",
            destination_warehouse="Vanasthalipuram Store",
            total_quantity=3,
            sub_total=3000.0,
            grand_total=3000.0,
        ),
        items=[
            LineItem(item_name="Samsung Galaxy S24 Ultra", sku="SAM-S24U-256", cost_price=1000.0, quantity=3, subtotal=3000.0)
        ],
        file_path="HCT-102.pdf",
        page_count=1,
    )

    summary = ItemGrouper.consolidate([order1, order2], store_name="Gajuwaka Store")
    assert summary.total_orders == 2
    assert summary.total_bags == 2
    assert summary.total_skus == 1
    assert summary.total_pieces == 8
    assert summary.total_value == 8000.0

    pdf_out = os.path.join(tmp_path, "HCT-TO-GWK-CONSOLIDATED.pdf")
    PDFBuilder().build_consignment_pdf(summary, pdf_out)
    assert os.path.exists(pdf_out)
    assert os.path.getsize(pdf_out) > 1000

    xlsx_out = os.path.join(tmp_path, "Checklist_Gajuwaka.xlsx")
    ExcelExporter.export(summary, xlsx_out)
    assert os.path.exists(xlsx_out)
    assert os.path.getsize(xlsx_out) > 1000

    geo = GeometryAnalyzer().analyze(pdf_out)
    assert geo["page_count"] >= 1
    assert geo["orientation"] == "portrait"
    assert geo["printable_width"] > 400

    typo = TypographyAnalyzer().analyze(pdf_out)
    assert typo["hierarchy"]["title_size"] >= 14.0

    palette = PaletteAnalyzer().analyze(pdf_out)
    assert palette["table_header_color"] == "#3C3D3A"

    grid = TableGridAnalyzer().analyze(pdf_out)
    assert grid["column_count"] >= 5

    audit = AuditChecker().audit(pdf_out)
    assert audit["score"] in ["5/6", "6/6"]

    fleet = FleetManager(vehicle_id="AP-39-TK-8821")
    fleet.add_branch_consignment(summary)
    totals = fleet.get_fleet_totals()
    assert totals["total_orders"] == 2
    assert totals["total_pieces"] == 8
    assert totals["total_value"] == 8000.0

    manifest_pdf = os.path.join(tmp_path, "Master_Fleet_Manifest.pdf")
    ManifestBuilder.build_manifest([summary], manifest_pdf)
    assert os.path.exists(manifest_pdf)

    db = DatabaseManager(os.path.join(tmp_path, "test.db"))
    db.log_action("CONSOLIDATION_COMPLETED", "Gajuwaka store consolidated 2 orders.")
