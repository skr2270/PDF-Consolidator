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

### 2.1 Interactive Folder Selection
If running without `--input`, PDF Consolidator opens a native OS folder picker dialog to select the folder safely:

```bash
python cli.py consolidate
```

### 2.2 Analyzing Document Layout Architecture
Inspect geometry, typography, palette, column boundaries, and audit anomalies:

```bash
python cli.py analyze --input "G:\My Drive\THC\Documents\Transfer Orders\Gajuwaka"
```

### 2.3 Consolidating a Single Store Folder
Merge bag-wise orders into a unified transit document:

```bash
python cli.py consolidate \
  --input "G:\My Drive\THC\Documents\Transfer Orders\Gajuwaka" \
  --output "G:\My Drive\THC\Documents\Transfer Orders\Gajuwaka\Transfer_Order_Gajuwaka_HCT-TO-GWK-260927.pdf" \
  --date "today" \
  --order-id "HCT-TO-GWK-260927" \
  --logo "assets/logo.png"
```

### 2.4 Handling Incremental Late-Bag Additions
When store staff add more bags (e.g. `HCT-719 to 726` or `HCT-727 to 731`):

```bash
python cli.py consolidate \
  --input "G:\My Drive\THC\Documents\Transfer Orders\Sujatha Nagar" \
  --date "today" \
  --order-id "HCT-TO-SJN-260927" \
  --delta-report
```

### 2.5 Excluding Specific Bags
If a bag is held back or damaged before truck loading:

```bash
python cli.py consolidate \
  --input "G:\My Drive\THC\Documents\Transfer Orders\Sujatha Nagar" \
  --exclude-bags "BAG-85,BAG-86"
```

### 2.6 Multi-Branch Fleet Mode (Tonight's Vehicle Consignment)
Process all dispatching branches and generate the Fleet Manifest:

```bash
python cli.py fleet --input-root "G:\My Drive\THC\Documents\Transfer Orders" --date "today"
```

---

## 3. Running Automated Tests

To run the unit and integration test suite:

```bash
pytest tests/
```
Tests verify:
* Row and consignment arithmetic parity.
* Indian currency words conversions (including paise edge cases).
* SKU sanitization and grouping rules.
* Multi-page table row aggregation.\n