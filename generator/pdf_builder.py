"""Vector PDF Generator using ReportLab with NumberedCanvas."""
import os
from typing import List, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from consolidator.item_grouper import ConsignmentSummary
from consolidator.currency_words import IndianCurrencyWords

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic 'Page X of Y' numbering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#777777"))
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 40, 25, page_str)
        
        compliance_text = "Transit Movement Document - GST Rule 55 Compliant | PDF Consolidator"
        self.drawString(40, 25, compliance_text)
        
        self.setStrokeColor(colors.HexColor("#D3D3D3"))
        self.setLineWidth(0.5)
        self.line(40, 36, A4[0] - 40, 36)
        self.restoreState()

class PDFBuilder:
    """Builds presentation-grade multi-page transfer order PDFs."""

    def __init__(self, logo_path: str = None, font_path: str = None):
        self.logo_path = logo_path
        self.font_path = font_path
        self._register_fonts()

    def _register_fonts(self):
        self.regular_font = "Helvetica"
        self.bold_font = "Helvetica-Bold"
        
        default_ubuntu = os.path.join(r"C:\Saikumar\Projects\PDF Consolidator", "assets", "fonts", "Ubuntu-Regular.ttf")
        default_bold = os.path.join(r"C:\Saikumar\Projects\PDF Consolidator", "assets", "fonts", "Ubuntu-Bold.ttf")
        
        reg_to_use = self.font_path or default_ubuntu
        if os.path.exists(reg_to_use) and os.path.exists(default_bold):
            try:
                pdfmetrics.registerFont(TTFont("Ubuntu", reg_to_use))
                pdfmetrics.registerFont(TTFont("Ubuntu-Bold", default_bold))
                self.regular_font = "Ubuntu"
                self.bold_font = "Ubuntu-Bold"
            except Exception:
                pass

    def build_consignment_pdf(self, summary: ConsignmentSummary, output_path: str, doc_number: str = "HCT-TO-CONSOLIDATED"):
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
        title_style = ParagraphStyle("DocTitle", fontName=self.bold_font, fontSize=16, leading=19, textColor=colors.HexColor("#1A1A1A"))
        company_style = ParagraphStyle("CompName", fontName=self.bold_font, fontSize=12, leading=15, textColor=colors.HexColor("#222222"))
        meta_label_style = ParagraphStyle("MetaLbl", fontName=self.bold_font, fontSize=8.5, leading=11, textColor=colors.HexColor("#444444"))
        meta_val_style = ParagraphStyle("MetaVal", fontName=self.regular_font, fontSize=8.5, leading=11, textColor=colors.HexColor("#222222"))
        th_style = ParagraphStyle("TH", fontName=self.bold_font, fontSize=8, leading=10, textColor=colors.white)
        td_style = ParagraphStyle("TD", fontName=self.regular_font, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#1A1A1A"))
        td_bold_style = ParagraphStyle("TDBold", fontName=self.bold_font, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#1A1A1A"))
        words_style = ParagraphStyle("Words", fontName=self.regular_font, fontSize=8, leading=11, textColor=colors.HexColor("#333333"))

        story = []

        effective_logo = self.logo_path or os.path.join(r"C:\Saikumar\Projects\PDF Consolidator", "assets", "logo.png")
        if os.path.exists(effective_logo):
            try:
                logo_elem = Image(effective_logo, width=120, height=45)
            except Exception:
                logo_elem = Paragraph("<b>THC RETAIL</b>", company_style)
        else:
            logo_elem = Paragraph("<b>THE CHENNAI MOBILES</b>", company_style)

        title_para = Paragraph("<b>TRANSFER ORDER</b>", title_style)

        header_table = Table([[logo_elem, title_para]], colWidths=[260, 255])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        meta_data = [
            [
                Paragraph("<b>Source Warehouse:</b>", meta_label_style),
                Paragraph(f"<b>{summary.store_name}</b><br/>Andhra Pradesh, India", meta_val_style),
                Paragraph("<b>Destination Warehouse:</b>", meta_label_style),
                Paragraph(f"<b>{summary.destination}</b><br/>Telangana, India", meta_val_style),
            ],
            [
                Paragraph("<b>Transfer Order#:</b>", meta_label_style),
                Paragraph(doc_number, meta_val_style),
                Paragraph("<b>Date:</b>", meta_label_style),
                Paragraph(summary.dispatch_date, meta_val_style),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[110, 150, 120, 135])
        meta_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 12))

        th_align_right = ParagraphStyle("THRight", parent=th_style, alignment=2)
        td_align_right = ParagraphStyle("TDRight", parent=td_style, alignment=2)
        td_align_center = ParagraphStyle("TDCenter", parent=td_style, alignment=1)

        table_rows = [
            [
                Paragraph("<b>#</b>", ParagraphStyle("THC", parent=th_style, alignment=1)),
                Paragraph("<b>Items & Description</b>", th_style),
                Paragraph("<b>Transfer Price</b>", th_align_right),
                Paragraph("<b>Quantity</b>", th_align_right),
                Paragraph("<b>Sub Total</b>", th_align_right),
            ]
        ]

        for idx, it in enumerate(summary.items, 1):
            name_text = f"<b>{it.item_name}</b><br/><font color='#555555' size='6.5'>SKU: {it.sku} | Bags: {len(it.bags)}</font>"
            table_rows.append([
                Paragraph(str(idx), td_align_center),
                Paragraph(name_text, td_style),
                Paragraph(f"{it.cost_price:,.2f}", td_align_right),
                Paragraph(str(it.quantity), td_align_right),
                Paragraph(f"{it.subtotal:,.2f}", td_align_right),
            ])

        items_table = Table(table_rows, colWidths=[26, 232, 77, 77, 103], repeatRows=1)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3C3D3A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E3E3E3")),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 10))

        words_text = IndianCurrencyWords.to_words(summary.total_value)
        words_para = Paragraph(f"<b>Amount in Words:</b><br/>{words_text}", words_style)

        totals_summary_data = [
            [Paragraph("<b>Total Quantity:</b>", td_bold_style), Paragraph(f"<b>{summary.total_pieces}</b>", td_align_right)],
            [Paragraph("<b>Consolidated Value:</b>", td_bold_style), Paragraph(f"<b>₹{summary.total_value:,.2f}</b>", td_align_right)],
            [Paragraph("<b>Total Bags / Orders:</b>", td_bold_style), Paragraph(f"<b>{summary.total_bags} Bags</b>", td_align_right)],
        ]
        totals_table = Table(totals_summary_data, colWidths=[120, 100])
        totals_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E3E3E3")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))

        split_summary = Table([[words_para, totals_table]], colWidths=[290, 225])
        split_summary.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        sig_data = [
            [
                Paragraph("<b>Prepared By:</b><br/><br/>______________________<br/>Store Executive", td_style),
                Paragraph("<b>Dispatched By:</b><br/><br/>______________________<br/>Logistics Officer", td_style),
                Paragraph("<b>Authorized Signatory:</b><br/><br/>______________________<br/>For The Chennai Mobiles", td_style),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[171, 171, 173])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ]))

        summary_block = KeepTogether([
            split_summary,
            Spacer(1, 15),
            sig_table
        ])
        story.append(summary_block)

        doc.build(story, canvasmaker=NumberedCanvas)
        return output_path
