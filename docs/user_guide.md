# User Guide & Operational Workflows

## 1. Getting Started

### 1.1 Prerequisites
* Python 3.10, 3.11, 3.12, or 3.13
* Windows, macOS, or Linux

### 1.2 Installation
```bash
cd "C:\Saikumar\Projects\PDF Consolidator"
python -m pip install -r requirements.txt
```

---

## 2. Command Line Interface (CLI)

PDF Consolidator provides commands for layout analysis, single-store consolidation, incremental delta updates, and multi-branch fleet batching.

### 2.1 Analyzing Document Layout Architecture
Inspect geometry, typography, palette, column boundaries, and audit anomalies:

```bash
python cli.py analyze --input "G:\My Drive\THC\Documents\Transfer Orders\Gajuwaka"
```

**Terminal Output Highlights**:
* Page format: A4 portrait ($595.42 \times 841.69\text{ pt}$)
* Font hierarchy: Ubuntu Regular & Bold (28pt Title, 9pt Table Text, 8pt Subtext)
* Color tokens: Header fill `#3C3D3A`, Divider `#ADADAD`
* Audit Findings: Missing `HCT-587`, Bag 9 vs Bag 8 sequence inversion, `*` and `#` catalog prefixes.

### 2.2 Consolidating a Single Store Folder
Merge bag-wise orders into a unified transit document:

```bash
python cli.py consolidate \
  --input "G:\My Drive\THC\Documents\Transfer Orders\Gajuwaka" \
  --output "G:\My Drive\THC\Documents\Transfer Orders\Gajuwaka\Transfer_Order_Gajuwaka_HCT-TO-GWK-260927.pdf" \
  --date "today" \
  --order-id "HCT-TO-GWK-260927" \
  --logo "assets/logo.png"
```

### 2.3 Incremental Delta Updates (Adding Late Orders)
When store staff add more bags (e.g. `HCT-719 to 726` or `HCT-727 to 731`):

```bash
python cli.py consolidate \
  --input "G:\My Drive\THC\Documents\Transfer Orders\Sujatha Nagar" \
  --date "today" \
  --order-id "HCT-TO-SJN-260927" \
  --delta-report
```
The `--delta-report` flag displays the baseline totals, added delta (+Qty, +Amount, +Bags), and updated grand total!

### 2.4 Multi-Branch Fleet Mode (Tonight's Vehicle Consignment)
Process all dispatching branches and generate the Fleet Manifest:

```bash
python cli.py fleet --input-root "G:\My Drive\THC\Documents\Transfer Orders" --date "today"
```

---

## 3. Interactive Web Dashboard

Launch the browser interface:

```bash
python app.py
```

### Dashboard Tabs:
1. **Layout Architecture Analyzer**: Drop any batch of PDFs to inspect geometry, typography, color palette, and quality control audit.
2. **Store Consolidator**: Merge orders with real-time SKU aggregation, custom order IDs, and logo upload.
3. **Fleet Vehicle Manifest**: View all dispatching branches loaded into tonight's vehicle, overall bag count, and grand totals.
4. **Downloads**: One-click download of the Unified Transit PDF and Warehouse Excel Checklist.\n