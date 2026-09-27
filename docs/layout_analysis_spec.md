# Document Layout & Format Architecture Analysis Specification

## 1. Objectives

The **Layout Architecture Analysis Engine** performs forensic structural analysis on input PDF transfer documents to extract:
1. Exact visual geometry, margins, and coordinate boundaries of the 6 layout zones.
2. Full typography hierarchy, font families, weights, and leading.
3. Design color tokens (table header fills, divider rules, text shades).
4. Table column grid architecture (column widths, percentage distribution, and alignments).
5. Comprehensive Quality Control & Audit Report (calculation checks, sequence gap detection, container ordering, SKU tagging, and duplicate SKU distribution).

---

## 2. Geometry & Zone Coordinate Mapping

The engine segments each document page into 6 distinct horizontal zones:

```
+-------------------------------------------------------------------------+
| ZONE 1: MASTER BRANDING & DOCUMENT IDENTITY (y: ~50 - 140 pt)           |
| [Logo: 115.5 x 46.8 pt]                            [Title: Ubuntu 28pt] |
| Company Legal Entity, GSTIN, Address, Contacts     TransferOrder#, Date |
|                                                    Created By           |
+-------------------------------------------------------------------------+
| ZONE 2: SUPPLY & STORE ROUTING BLOCK (y: ~140 - 295 pt)                 |
| Place Of Supply: State (Code)                                           |
| Source Location Card             | Destination Location Card            |
| (Address, GSTIN, Phone, Web)     | (Address, GSTIN, Phone, Web)         |
+-------------------------------------------------------------------------+
| ZONE 3: TABULAR DATA GRID (y: ~306 pt downward)                         |
| [Col 1: #] [Col 2: Item & SKU] [Col 3: HSN] [Col 4: Qty] [Col 5: Rate]  |
| Alternating 0.8 pt Row Separator Lines                                  |
+-------------------------------------------------------------------------+
| ZONE 4: SUMMARY & TOTALS BLOCK                                          |
| Items in Total: XXX.XX                           Total: Rs. X,XX,XXX.XX |
| Total In Words: Indian Rupee ... Only                                   |
+-------------------------------------------------------------------------+
| ZONE 5: DISPATCH AUDIT & SIGN-OFF                                       |
| Reason / Container Scope (e.g. BAG-01 to BAG-91)                        |
| Authorized Signature ______________________________________             |
+-------------------------------------------------------------------------+
| ZONE 6: RUNNING FOOTER (y: ~791 - 842 pt)                               |
| 0.8 pt Border Rule                                        [Page Number] |
+-------------------------------------------------------------------------+
```

### 2.1 Dimensional Attributes (A4 Default)
* **Page Bounds**: $595.42	ext{ pt} 	imes 841.69	ext{ pt}$ ($210	ext{ mm} 	imes 297	ext{ mm}$).
* **Margin Insets**: Top $50.4	ext{ pt}$, Bottom $50.4	ext{ pt}$, Left $45.6	ext{ pt}$, Right $34.8	ext{ pt}$.
* **Active Printable Width**: $515.0	ext{ pt}$ ($181.7	ext{ mm}$).

---

## 3. Typography Hierarchy & Font Inspection

The engine iterates over every glyph in the PDF character tree to build a typographic profile:

| Level | Size | Weight | Detected Font | Role |
| :--- | :---: | :---: | :--- | :--- |
| **Title** | $26.0 - 28.0	ext{ pt}$ | Bold | `Ubuntu`, `Helvetica` | Document Title (`Transfer Order`) |
| **Section Header** | $10.0 - 12.0	ext{ pt}$ | Bold | `Ubuntu-Bold` | Summary Labels (`Total Rs.`) |
| **Table Header** | $9.0	ext{ pt}$ | Bold | `Ubuntu-Bold` | Grid Headers (`#`, `Item`, `HSN`, `Qty`) |
| **Body Text** | $9.0	ext{ pt}$ | Regular | `Ubuntu` | Store Addresses, Item Names, Cost Prices |
| **Sub-Metadata** | $8.0	ext{ pt}$ | Regular | `Ubuntu` | Secondary Identifiers (`SKU: 35659`, `pcs`) |
| **Running Footer** | $8.0	ext{ pt}$ | Regular | `Ubuntu` | Dynamic Page Numbers (`1`, `2`, `3`) |

---

## 4. Color Palette & Design Tokens

Extracts normalized design tokens for replication:

```json
{
  "tokens": {
    "header_band_fill": "#3C3D3A",
    "header_band_text": "#FFFFFF",
    "row_divider_stroke": "#ADADAD",
    "row_divider_width": 0.8,
    "card_divider_stroke": "#CCCCCC",
    "card_divider_width": 0.8,
    "text_primary": "#000000",
    "text_body": "#333333",
    "text_footer": "#6C718A"
  }
}
```

---

## 5. Table Grid Architecture & Column Layout

Measures exact column geometry and alignment rules:

| # | Column Name | Width (pt) | Width (%) | Alignment | Layout Description |
| :-: | :--- | :-: | :-: | :--- | :--- |
| **1** | `#` | $25.7	ext{ pt}$ | $5.0\%$ | Left / Center | Row Index Number |
| **2** | `Item & Description` | $201.0	ext{ pt}$ | $39.0\%$ | Left | Line 1: Item Name; Line 2: `SKU: <id>` |
| **3** | `HSN/SAC` | $77.2	ext{ pt}$ | $15.0\%$ | Center | 6-to-8 digit GST HSN Code |
| **4** | `Qty` | $56.6	ext{ pt}$ | $11.0\%$ | Right | Line 1: Quantity; Line 2: Unit `pcs` |
| **5** | `Cost Price` | $77.2	ext{ pt}$ | $15.0\%$ | Right | Unit Cost with `Rs.` prefix |
| **6** | `Amount` | $77.2	ext{ pt}$ | $15.0\%$ | Right | Total Line Item Amount |

---

## 6. Comprehensive Quality Control & Audit Engine

The audit engine runs 5 automated checks on every ingested document batch:

1. **Row Arithmetic Parity**:
   $$\Delta = |	ext{Quantity} 	imes 	ext{Cost Price} - 	ext{Row Amount}|$$
   Flags any calculation exceeding $0.01	ext{ INR}$.
2. **Order Totals Reconciliation**:
   Checks whether $\sum 	ext{Line Quantities} = 	ext{Reported Total Qty}$ and $\sum 	ext{Line Amounts} = 	ext{Reported Total Amount}$.
3. **Sequence Continuity Checker**:
   Scans order IDs to detect gaps in numbering (e.g., flagging missing order `HCT-587` between `586` and `588`).
4. **Container / Bag Sequence Anomaly Checker**:
   Identifies container reversal (e.g. order `HCT-586` assigned `BAG-9` while `HCT-588` assigned `BAG-8`).
5. **Catalog Prefix & Tagging Detection**:
   Flags inventory tags such as `*` (e.g. `*BANGU COTTON SAREE`) or `#` (e.g. `# IKKATHPATOLA VAS`) used by merchants for internal discount classes.
6. **Cross-Order Duplicate SKU Detection**:
   Identifies identical SKUs split across multiple separate bags (e.g. SKU 41878 appearing in both HCT-582 and HCT-583, or SKU 50761 across HCT-719, 720, 721).\n