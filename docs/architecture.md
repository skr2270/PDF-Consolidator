# System Architecture & Design Specification

## 1. System Overview & Core Mission

**PDF Consolidator** is an enterprise-grade document intelligence, layout analysis, and logistics consolidation platform designed to solve the real-world operational and regulatory disconnect between retail inventory preparation and physical vehicle transport.

In retail and multi-store distribution:
1. **Incremental Store Preparation**: Over several days, store associates pack merchandise into physical containers (bags, boxes, or cartons), generating individual transfer orders or delivery challans in POS/ERP systems (such as Zoho POS, Zoho Books, Tally, Busy, SAP, or Marg) as each container is sealed.
2. **Bulk Vehicle Movement**: All stock from multiple branches physically moves together in a single transport vehicle.
3. **Statutory Tax & Transit Compliance**: Under transport regulations (such as GST Rule 55 in India, e-Way bill consignment mandates, and transit checkpoints), transit documents must:
   - Carry the **actual vehicle movement date** (today's date).
   - Consolidate dozens of fragmented bag orders into a unified movement document per dispatching branch.
   - Maintain accurate Place of Supply and GSTIN matching.
   - Reconcile line item arithmetic without rounding drift.
4. **Unloading Verification**: Receiving store staff must retain a transparent container audit trail (which bag contains which items) during unpacking.
5. **Last-Minute Incremental Additions**: Ground staff frequently add late bags (e.g. +8 bags, +5 bags) right up until the truck departs. The platform must handle continuous incremental additions without manual re-entry.

---

## 2. End-to-End Processing Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["1. Document Ingestion & Guard Layer"]
        A[Input Folder / Drag & Drop PDFs] --> B[Circular Ingestion Guard]
        B -->|Filter out Transfer_Order_*.pdf & Consolidated.pdf| C[Raw Order PDFs]
        C --> D[Hydration & Accessibility Check]
        D --> E[PDF Reader & Plumber Engine]
        E -->|Vector PDF| F[Native Text Extractor]
        E -->|Scanned / Raster PDF| G[OCR Fallback Engine]
    end

    subgraph Stage1 ["2. Stage 1: Document Layout Architecture & Audit"]
        F & G --> H[Geometry & Coordinate Analyzer]
        F & G --> I[Typography & Font Inspector]
        F & G --> J[Color Palette & Token Extractor]
        F & G --> K[Table Grid & Boundary Detector]
        F & G --> L[Quality Control & Audit Engine]
        
        L --> L1[Math Verifier: Qty x Rate = Amt]
        L --> L2[Sequence Gap Detector: e.g. Missing HCT-587]
        L --> L3[Container Order Check: e.g. Bag 9 vs Bag 8]
        L --> L4[Catalog Tag Detector: * and # prefixes]
        L --> L5[Cross-Order Duplicate SKU Detector]

        H & I & J & K & L --> M[Architectural Layout & Audit Report]
    end

    subgraph Stage2 ["3. Stage 2: Multi-ERP Parsing Layer"]
        F & G --> N{ERP Strategy Selector}
        N -->|Zoho Format| O[Zoho Multi-Page Parser]
        N -->|Tally Format| P[Tally Multi-Page Parser]
        N -->|Custom / Other| Q[Generic Spatial Table Parser]
        
        O & P & Q --> R[Normalized Order Schema]
    end

    subgraph Stage3 ["4. Stage 3: Consolidation & Delta Engine"]
        R --> S[SKU Sanitization & Name Resolver]
        S --> T[Bag De-selection & Cancellation Filter]
        T --> U[SKU & HSN Grouping Engine]
        U --> V[Container / Bag Trail Mapper]
        V --> W[Incremental Delta Processor]
        W --> X[Indian & International Currency Words Engine]
    end

    subgraph Stage4 ["5. Stage 4: Multi-Branch & Persistence Layer"]
        X --> Y[Fleet Manager: Multi-Branch Consolidation]
        Y --> Z[SQLite Dispatch & SKU Registry]
        Z --> AA[Dispatch History & Audit Trail]
    end

    subgraph Stage5 ["6. Stage 5: Publication & Dual Export"]
        X --> AB[ReportLab Vector PDF Builder]
        X --> AC[OpenPyXL Warehouse Checklist Exporter]
        
        AB --> AD[Consolidated Transit PDF: Multi-page, Repeated Headers]
        AC --> AE[3-Tab Excel Unloading Workbook]
        
        AD --> AF[Dual Mirroring: Branch Folder & Root Folder]
    end
```

---

## 3. Modular Architecture Breakdown

### 3.1 `analyzer/` — Document Layout & Format Architecture Engine
* **`geometry.py`**: Auto-detects page size (A4, Letter), orientation, margin insets (top, bottom, left, right), and maps the 6 spatial layout zones across single or multi-page documents.
* **`typography.py`**: Extracts embedded font families (Ubuntu, Helvetica), scales font sizes into a 6-tier hierarchy, and records font weights and leading.
* **`palette.py`**: Extracts exact vector fills (header bar `#3C3D3A`), border rules (`#ADADAD`, `#CCCCCC`), and text colors into design tokens.
* **`table_grid.py`**: Analyzes character coordinate bounding boxes to determine column boundaries, width percentages, and alignment (numeric right-aligned, text left-aligned).
* **`audit_checker.py`**: Comprehensive QC audit:
  * Verifies row-level math ($	ext{Qty} 	imes 	ext{Rate} = 	ext{Amount}$).
  * Checks order sequence continuity (flags gaps like missing `HCT-587`).
  * Checks container sequencing (flags out-of-order bag creations).
  * Detects catalog prefix tags (`*` and `#`).
  * Detects duplicate SKUs distributed across separate transfer orders.

### 3.2 `parsers/` — Multi-ERP Ingestion Layer
* **`guard.py` (Circular Ingestion Guard)**: Inspects filenames and metadata to strictly exclude previously generated outputs (`Transfer_Order_*.pdf`, `Consolidated.pdf`, `.xlsx`, temporary files), preventing circular duplication.
* **`hydration.py`**: Validates file accessibility on cloud-synced drives (e.g. Google Drive for Desktop), checking for non-zero file sizes and handling on-demand file hydration retries.
* **`base_parser.py`**: Abstract contract for ERP-specific parsers with **multi-page iteration support** (`for page in pdf.pages`).
* **`zoho_parser.py`**: Optimized for Zoho Books, Zoho Inventory, and Zoho POS.
* **`tally_parser.py`**: Optimized for Tally Prime and Tally.ERP 9 stock transfer vouchers.
* **`generic_table_parser.py`**: Universal spatial table extractor using horizontal character clustering and whitespace boundary projection.
* **`ocr_fallback.py`**: Gracefully invokes OCR for raster or flattened image PDFs when zero digital characters are detected.

### 3.3 `consolidator/` — Grouping, Delta & Currency Engine
* **`sku_sanitizer.py`**: Trims whitespace, standardizes casing, strips non-alphanumeric noise, and resolves catalog aliases.
* **`bag_filter.py`**: Allows users to interactively exclude/cancel specific bags before consolidation.
* **`item_grouper.py`**: Groups items by 3-tuple `(SKU, Cost Price, HSN)` while appending container references to an audit set.
* **`delta_processor.py`**: Handles incremental additions (e.g. +8 orders, +5 orders) by calculating the baseline, added delta, and updated total.
* **`currency_words.py`**: Translates monetary amounts into words with exact paise precision using Indian numbering (Crores, Lakhs, Thousands, Hundreds) and Western formats, handling zero paise, single-digit paise, and multi-crore numbers.

### 3.4 `fleet/` — Multi-Branch Fleet Management
* **`fleet_manager.py`**: Scans parent directories containing multiple branch subfolders (e.g. Gajuwaka, Beach Road, Sujatha Nagar), builds store-level unified transit documents, and compiles a unified **Master Fleet Vehicle Manifest** summarizing the entire consignment.

### 3.5 `db/` — SQLite Persistence Layer
* **`database.py`**: Local relational SQLite database managing historical runs, audit logs, and SKU registries:
```sql
CREATE TABLE IF NOT EXISTS dispatches (
    id TEXT PRIMARY KEY,
    dispatch_date DATE NOT NULL,
    source_branch TEXT NOT NULL,
    dest_branch TEXT NOT NULL,
    source_gstin TEXT NOT NULL,
    dest_gstin TEXT NOT NULL,
    total_bags INTEGER NOT NULL,
    total_pieces REAL NOT NULL,
    total_value REAL NOT NULL,
    pdf_path TEXT,
    excel_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consolidated_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispatch_id TEXT REFERENCES dispatches(id),
    sku TEXT NOT NULL,
    description TEXT NOT NULL,
    hsn TEXT NOT NULL,
    qty REAL NOT NULL,
    cost_price REAL NOT NULL,
    amount REAL NOT NULL,
    bags_contained TEXT
);

CREATE TABLE IF NOT EXISTS raw_orders (
    id TEXT PRIMARY KEY,
    dispatch_id TEXT REFERENCES dispatches(id),
    order_no TEXT NOT NULL,
    original_date DATE,
    bag_no TEXT,
    pieces REAL,
    amount REAL
);
```

### 3.6 `generator/` — Publication & Dual Export Engine
* **`pdf_builder.py`**: ReportLab engine generating vector PDFs matching analyzed styling, with two-pass `NumberedCanvas` dynamic page numbering, repeated table headers on page breaks (`repeatRows=1`), brand logo aspect-ratio fitting, offline font fallback (`Ubuntu` $ightarrow$ `Helvetica`), and orphan prevention.
* **`excel_exporter.py`**: OpenPyXL engine emitting a 3-tab warehouse unloading workbook (Consignment Summary, Master Product Checklist with check-off boxes, and Bag-by-Bag Unpacking Annexure).\n