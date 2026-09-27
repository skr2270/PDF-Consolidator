"""Command-Line Interface for PDF Consolidator."""
import os
import sys
import argparse
from parsers.guard import CircularIngestionGuard
from parsers.zoho_parser import ZohoInventoryParser
from consolidator.item_grouper import ItemGrouper
from generator.pdf_builder import PDFBuilder
from generator.excel_exporter import ExcelExporter
from analyzer.geometry import GeometryAnalyzer
from analyzer.audit_checker import AuditChecker

def pick_folder_dynamically() -> str:
    """Prompt user for folder or open native file dialog if available."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select Transfer Orders Folder")
        root.destroy()
        if folder:
            return folder
    except Exception:
        pass
    val = input("Enter path to Transfer Orders directory: ").strip()
    return val

def main():
    parser = argparse.ArgumentParser(description="PDF Consolidator CLI")
    parser.add_argument("--input-dir", "-i", type=str, help="Directory containing source PDFs")
    parser.add_argument("--output-dir", "-o", type=str, default="output", help="Directory for generated outputs")
    parser.add_argument("--store-name", "-s", type=str, default="Source Store", help="Source store name")
    parser.add_argument("--mode", "-m", choices=["consolidate", "analyze", "audit"], default="consolidate")
    args = parser.parse_args()

    input_dir = args.input_dir
    if not input_dir:
        print("No input directory provided. Opening directory picker...")
        input_dir = pick_folder_dynamically()
        if not input_dir or not os.path.exists(input_dir):
            print("Error: Valid directory not selected.")
            sys.exit(1)

    print(f"Working on directory: {input_dir}")

    if args.mode == "analyze":
        files = CircularIngestionGuard.filter_directory(input_dir)
        if not files:
            print("No valid source PDFs found to analyze.")
            return
        sample = files[0]
        print(f"Analyzing layout architecture on: {sample}")
        g = GeometryAnalyzer().analyze(sample)
        print(f"Page Count: {g['page_count']} | Dimensions: {g['width']} x {g['height']} pt | Orientation: {g['orientation']}")
        print(f"Printable Width: {g['printable_width']} pt | Margins: {g['margins']}")

    elif args.mode == "audit":
        files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]
        for f in files:
            res = AuditChecker().audit(f)
            print(f"Audit {os.path.basename(f)}: Score {res['score']} | Passed: {res['all_passed']}")

    elif args.mode == "consolidate":
        files = CircularIngestionGuard.filter_directory(input_dir)
        print(f"Found {len(files)} clean source transfer orders.")
        if not files:
            print("No files matched the ingestion criteria.")
            return

        parser_inst = ZohoInventoryParser()
        orders = []
        for f in files:
            orders.append(parser_inst.parse(f))

        summary = ItemGrouper.consolidate(orders, store_name=args.store_name)
        print(f"Consolidated: {summary.total_orders} Orders | {summary.total_skus} SKUs | {summary.total_pieces} Pieces | ₹{summary.total_value:,.2f}")

        os.makedirs(args.output_dir, exist_ok=True)
        out_pdf = os.path.join(args.output_dir, f"Consolidated_{args.store_name.replace(' ', '_')}.pdf")
        out_xlsx = os.path.join(args.output_dir, f"Checklist_{args.store_name.replace(' ', '_')}.xlsx")

        PDFBuilder().build_consignment_pdf(summary, out_pdf)
        ExcelExporter.export(summary, out_xlsx)
        print(f"Generated Vector PDF: {out_pdf}")
        print(f"Generated Excel Checklist: {out_xlsx}")

if __name__ == "__main__":
    main()
