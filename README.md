# PDF Consolidator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Compliance: GST Rule 55](https://img.shields.io/badge/Compliance-GST%20Rule%2055-green.svg)](#statutory-compliance)

**PDF Consolidator** is an enterprise-grade document intelligence, layout analysis, and logistics consolidation platform. It automates **Document Layout & Format Architecture Analysis** and synthesizes fragmented, bag-wise retail Transfer Orders / Delivery Challans from **any ERP (Zoho, Tally, Busy, SAP, Marg, or custom engines)** into unified, statutory-compliant transit documents carrying today's date, verified arithmetic, brand typography, and interactive warehouse unloading checklists.

---

## The Operational Challenge

* **Incremental Store Packing**: Ground staff pack merchandise into physical containers (bags, boxes, cartons) over several days, creating dozens of bag-wise transfer orders in POS/ERP systems.
* **Bulk Vehicle Movement**: All inventory physically departs together in a single transport vehicle. Carrying 80–140 individual printouts causes administrative chaos and checkpost delays.
* **ERP Immutability**: Cloud ERPs lock created transfer orders. You cannot easily re-date or batch-merge them into a single consolidated delivery challan without re-entering hundreds of items manually.
* **Continuous Late Additions**: Staff frequently add last-minute bags right up until vehicle departure (e.g., adding +8 bags, then +5 bags). The system must handle incremental delta re-consolidation seamlessly.
* **Unloading Reconciliation**: Destination warehouse staff need both aggregate product quantities for inventory intake and bag-by-bag unpacking checklists for physical audit.

---

## Key Capabilities

1. **Document Layout & Architecture Analyzer**:
   * Inspects geometry, page bounds (A4/Letter), margins, and coordinate zone boundaries across single and multi-page documents.
   * Discovers embedded font families, typographic hierarchy, font weights, and leading.
   * Extracts design color tokens (header fills, divider rules, font colors).
   * Detects table columns, relative percentage widths, and alignments.
   * Comprehensive Quality Control Audit: Flags row math discrepancies (Qty x Rate != Amount), sequence gaps (missing order IDs), inverted container numbering, catalog prefixes (`*`, `#`), and cross-order duplicate SKUs.

2. **Universal Multi-ERP Parsing with Circular Ingestion Guard**:
   * Out-of-the-box adapters for **Zoho** (Books, Inventory, POS), **Tally Prime / ERP 9**, and a **Spatial Table Parser** for arbitrary PDFs.
   * Circular Ingestion Guard strictly excludes previously generated consolidated documents (`Transfer_Order_*.pdf`, `Consolidated.pdf`, `.xlsx`) to prevent data corruption upon re-runs.
   * Multi-page order parsing: Aggregates rows across all pages of dense orders.
   * Cloud-drive hydration checks for Google Drive / OneDrive on-demand files.

3. **Intelligent SKU Consolidation & Incremental Delta Updates**:
   * Groups items by 3-tuple `(SKU, Cost Price, HSN)` to aggregate quantities without inventory valuation drift.
   * Full incremental update support: Dynamically incorporates newly added orders and displays a clear delta audit (+Pieces, +Value, +Bags).
   * Interactive bag de-selection for held-back or damaged containers.
   * Translates grand totals into formal Indian currency words (`Crores / Lakhs / Thousands / Paise`).

4. **Publication-Ready PDF Generation**:
   * High-fidelity ReportLab engine matching original ERP styling.
   * Multi-page flow with automatic repeated table headers (`repeatRows=1`).
   * Dynamic two-pass page numbering (`NumberedCanvas`).
   * Proportional logo bounding-box scaling ($130 \times 50\text{ pt}$) preserving aspect ratio.
   * Bundled offline font fallback (`Ubuntu` $\rightarrow$ `Helvetica`).
   * Dual location mirroring: Saves to branch folder and parent consignment folder.

5. **Multi-Branch Fleet Vehicle Manifest**:
   * Processes multiple dispatching stores (e.g. Gajuwaka, Beach Road, Sujatha Nagar) and compiles a Master Fleet Summary for the transport vehicle.

6. **Interactive Warehouse Unloading Checklist (`.xlsx`)**:
   * Generates a 3-tab workbook: Consignment Overview, Master Product Checklist with check-off boxes, and Bag-by-Bag Unpacking Annexure.

7. **Dual Interfaces**:
   * **CLI**: Fast command-line batch runner (`analyze`, `consolidate`, `fleet`) with native folder picker dialogs.
   * **Web Dashboard**: Interactive browser UI with live layout preview and one-click downloads.

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/your-org/pdf-consolidator.git
cd "PDF Consolidator"
python -m pip install -r requirements.txt
```

### 2. Analyze Document Layout Architecture

```bash
python cli.py analyze --input "./sample_orders/Gajuwaka"
```

### 3. Generate Consolidated Transit Document

```bash
python cli.py consolidate \
  --input "./sample_orders/Sujatha_Nagar" \
  --output "./output/Transfer_Order_Sujatha_Nagar.pdf" \
  --date "today" \
  --order-id "HCT-TO-SJN-260927"
```

### 4. Process Multi-Branch Fleet Consignment

```bash
python cli.py fleet --input-root "./sample_orders" --date "today"
```

### 5. Launch Interactive Web Dashboard

```bash
python app.py
```

---

## Project Structure

```
PDF Consolidator/
├── README.md                      # Master project overview & quickstart
├── requirements.txt               # Dependencies (reportlab, pdfplumber, openpyxl, etc.)
├── config.yaml                    # Company metadata, GSTINs, and style defaults
├── cli.py                         # Command-line interface
├── app.py                         # Interactive browser dashboard
│
├── assets/                        # Bundled offline assets
│   ├── logo.png                   # Official transparent company logo
│   └── fonts/                     # Bundled Ubuntu TrueType fonts
│       ├── Ubuntu-Regular.ttf
│       └── Ubuntu-Bold.ttf
│
├── docs/                          # In-depth architectural & technical documentation
│   ├── architecture.md            # System design & data pipeline architecture
│   ├── layout_analysis_spec.md    # Layout & format architecture analyzer specification
│   ├── parsers_spec.md            # Multi-ERP ingestion & parser strategy design
│   ├── consolidation_rules.md     # SKU grouping, arithmetic & currency words rules
│   ├── output_generation_spec.md  # ReportLab PDF & Excel checklist specifications
│   └── user_guide.md              # Detailed user workflows, CLI commands & troubleshooting
│
├── analyzer/                      # Document layout & format architecture engine
│   ├── geometry.py                # Page sizes, margins, coordinate zone detection
│   ├── typography.py              # Font inspection, size classification, weights
│   ├── palette.py                 # Hex/RGB color token extraction
│   ├── table_grid.py              # Column boundary detection, width %, alignment
│   └── audit_checker.py           # Arithmetic checks, missing sequences, bag anomalies
│
├── parsers/                       # Generalized multi-ERP ingestion engine
│   ├── guard.py                   # Circular ingestion guard (filters generated files)
│   ├── hydration.py               # Cloud drive on-demand file hydration check
│   ├── base_parser.py             # Abstract document parser interface (multi-page)
│   ├── generic_table_parser.py    # Spatial table extractor for arbitrary PDFs
│   ├── zoho_parser.py             # Optimized extractor for Zoho POS / Books
│   ├── tally_parser.py            # Optimized extractor for Tally Prime / ERP 9
│   └── ocr_fallback.py            # OCR fallback engine for raster/scanned PDFs
│
├── consolidator/                  # Grouping, delta reconciliation & currency engine
│   ├── sku_sanitizer.py           # SKU cleaning, alias resolution, noise stripping
│   ├── bag_filter.py              # Interactive container cancellation/de-selection
│   ├── item_grouper.py            # SKU/HSN/Rate grouping with bag tracking
│   ├── delta_processor.py         # Incremental update processor (+late orders)
│   ├── arithmetic_verifier.py     # Row & consignment mathematical validation
│   └── currency_words.py          # Indian (Lakhs/Crores) & Western words conversion
│
├── fleet/                         # Multi-branch fleet vehicle consolidation
│   └── fleet_manager.py           # Compiles multi-branch master fleet manifest
│
├── db/                            # SQLite persistence & audit repository
│   └── database.py                # SQLite schema migrations & dispatch logger
│
├── generator/                     # Publication & export engine
│   ├── pdf_builder.py             # Multi-page ReportLab PDF builder with branding
│   └── excel_exporter.py          # Multi-tab warehouse unloading checklist (.xlsx)
│
└── tests/                         # Automated unit & integration tests
    ├── test_math_verifier.py
    ├── test_currency_words.py
    └── test_sku_grouper.py
```

---

## Documentation Index

Explore the comprehensive technical specifications inside [`docs/`](docs/):

* [System Architecture & Design Specification](docs/architecture.md)
* [Document Layout & Format Architecture Analysis Specification](docs/layout_analysis_spec.md)
* [Multi-ERP Parser & Ingestion Specification](docs/parsers_spec.md)
* [SKU Consolidation & Reconciliation Rules](docs/consolidation_rules.md)
* [Output Document Generation & Compliance Specification](docs/output_generation_spec.md)
* [User Guide & Operational Workflows](docs/user_guide.md)

---

## Statutory Compliance

PDF Consolidator is designed in alignment with:
* **Rule 55, Central Goods and Services Tax (CGST) Rules**: Delivery Challans for transportation of goods without sale.
* **e-Way Bill Rule 138**: Consignment value aggregation and movement date compliance.

---

## License

This project is licensed under the [MIT License](LICENSE).\n