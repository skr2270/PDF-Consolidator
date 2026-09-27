"""Master Multi-Branch Fleet Vehicle Manifest PDF Generator."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .pdf_builder import NumberedCanvas

class ManifestBuilder:
    """Builds consolidated Master Fleet Manifest across multiple branch dispatches."""

    @classmethod
    def build_manifest(cls, branch_summaries: list, output_path: str, vehicle_no: str = "AP 39 TK 8821"):
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=36,
            bottomMargin=45
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("MTitle", fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=colors.HexColor("#1A1A1A"))
        meta_style = ParagraphStyle("MMeta", fontName="Helvetica", fontSize=9, leading=12)
        th_style = ParagraphStyle("MTH", fontName="Helvetica-Bold", fontSize=8.5, leading=10, textColor=colors.white)
        td_style = ParagraphStyle("MTD", fontName="Helvetica", fontSize=8, leading=10)
        td_right = ParagraphStyle("MTDRight", parent=td_style, alignment=2)
        td_bold_right = ParagraphStyle("MTDBRight", fontName="Helvetica-Bold", fontSize=8, leading=10, alignment=2)

        story = []
        story.append(Paragraph("<b>MASTER FLEET CONSIGNMENT MANIFEST</b>", title_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Vehicle Reg No:</b> {vehicle_no} | <b>Date:</b> 27/09/2026 | <b>Destination:</b> Vanasthalipuram Store, Hyderabad", meta_style))
        story.append(Spacer(1, 15))

        table_rows = [
            [
                Paragraph("<b>#</b>", th_style),
                Paragraph("<b>Source Branch</b>", th_style),
                Paragraph("<b>Bags / Orders</b>", th_style),
                Paragraph("<b>SKU Count</b>", th_style),
                Paragraph("<b>Total Pieces</b>", th_style),
                Paragraph("<b>Branch Value (INR)</b>", th_style),
            ]
        ]

        total_orders = sum(s.total_orders for s in branch_summaries)
        total_skus = sum(s.total_skus for s in branch_summaries)
        total_pieces = sum(s.total_pieces for s in branch_summaries)
        total_val = sum(s.total_value for s in branch_summaries)

        for idx, s in enumerate(branch_summaries, 1):
            table_rows.append([
                Paragraph(str(idx), td_style),
                Paragraph(f"<b>{s.store_name}</b>", td_style),
                Paragraph(str(s.total_orders), td_right),
                Paragraph(str(s.total_skus), td_right),
                Paragraph(str(s.total_pieces), td_right),
                Paragraph(f"{s.total_value:,.2f}", td_right),
            ])

        table_rows.append([
            Paragraph("<b>TOTAL</b>", td_style),
            Paragraph("<b>ALL BRANCHES CONSOLIDATED</b>", td_style),
            Paragraph(f"<b>{total_orders} Bags</b>", td_bold_right),
            Paragraph(f"<b>{total_skus}</b>", td_bold_right),
            Paragraph(f"<b>{total_pieces}</b>", td_bold_right),
            Paragraph(f"<b>₹{total_val:,.2f}</b>", td_bold_right),
        ])

        manifest_table = Table(table_rows, colWidths=[25, 175, 75, 75, 75, 90])
        manifest_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3C3D3A")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E3E3E3")),
            ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor("#3C3D3A")),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F5F5F5")),
        ]))
        story.append(manifest_table)
        doc.build(story, canvasmaker=NumberedCanvas)
        return output_path
