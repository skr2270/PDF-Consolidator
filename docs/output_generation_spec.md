# Output Document Generation & Compliance Specification

## 1. Overview

PDF Consolidator generates two core deliverables:
1. **Consolidated Transit Transfer Order (PDF)**: A publication-quality, multi-page vector PDF meeting statutory GST Rule 55 Delivery Challan requirements.
2. **Warehouse Unloading Checklist (Excel `.xlsx`)**: An interactive 3-tab workbook for logistics verification and bag-by-bag receipt audit.

---

## 2. ReportLab PDF Generation Architecture

### 2.1 Dynamic Pagination with `NumberedCanvas`
In standard PDF generation, knowing the total page count ahead of time is impossible before flowable text breaks are computed. PDF Consolidator uses a custom two-pass canvas (`NumberedCanvas`):
1. **Pass 1 (`showPage`)**: Saves the canvas drawing states and increments the page counter without writing the footer.
2. **Pass 2 (`save`)**: Iterates through all recorded page states, drawing the final running footer rule and dynamic page indicator (`Page X of Y` or `X`) with exact total page awareness.

```python
class NumberedCanvas(canvas.Canvas):
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()
```

### 2.2 Multi-Page Flow & Repeated Table Headers
* **Table Header Repetition**: Table flowables set `repeatRows=1`. When a table exceeds the vertical height of Page 1, the dark charcoal header bar (`#3C3D3A`) with white text automatically renders at the top margin ($50.4\text{ pt}$) of Page 2, Page 3, and all subsequent pages.
* **Orphan Prevention (`KeepTogether`)**:
  * The Summary row (`Items in Total`, `Total Rs.`), legal `Total In Words`, and `Authorized Signature` block are wrapped in a `KeepTogether` container.
  * This guarantees that totals and signature lines are never separated across page breaks.

### 2.3 Logo Aspect Ratio & Transparency
* Automatically detects PNG dimensions and mode (`RGBA`).
* Preserves transparency channel and calculates bounding box scaling (default $115.5\text{ pt} \times 46.76\text{ pt}$, aspect ratio $\sim 2.47$).

### 2.4 Dual Output Location Mirroring
To support both branch-level filing and vehicle-level paperwork:
* Saves a copy directly into the branch directory:
  `[Branch]/Transfer_Order_[Branch]_[ID].pdf`
* Mirrors a copy into the parent consignment directory:
  `Transfer Orders/Transfer_Order_[Branch]_[ID].pdf`

---

## 3. Statutory GST Transit Standards (Rule 55)

Under Rule 55 of the Central Goods and Services Tax (CGST) Rules in India, goods transported for reasons other than by way of supply (e.g., inter-branch stock transfers) must be accompanied by a Delivery Challan containing:

1. **Date and Number of the Delivery Challan**: Dynamic movement date (today's vehicle movement date) and unique serial number.
2. **Name, Address and GSTIN of Consignor**: Source store location with verified state GSTIN (`37` for Andhra Pradesh).
3. **Name, Address and GSTIN of Consignee**: Destination store location with verified state GSTIN (`36` for Telangana).
4. **Place of Supply**: State of destination and state code (`Telangana (36)`).
5. **HSN Code and Description of Goods**: Complete 6-to-8 digit Harmonized System of Nomenclature code.
6. **Quantity & Taxable Value**: Accurate physical unit quantities and valuation at transfer cost.
7. **Signature of Consignor**: Dedicated signature line for authorized store manager sign-off upon dispatch.

---

## 4. Warehouse Unloading Excel Workbook (`.xlsx`)

The generated workbook contains three purpose-built tabs:

### Tab 1: Dispatch Summary
* Consignment metadata: Dispatch Date, New Order ID, Source Branch, Destination Branch, Transporter/Vehicle details.
* Aggregate KPI cards: Total Bags, Total Pieces, Total Consignment Value.

### Tab 2: Master Product Checklist
* Master consolidated SKU inventory.
* Columns: `S.No`, `SKU`, `Item Description`, `HSN/SAC`, `Dispatched Qty`, `Received Qty (Physical Check)`, `Variance`, `Status (Match / Discrepancy)`.
* Pre-formatted with data validation check boxes for the warehouse receiving supervisor.

### Tab 3: Bag-by-Bag Unpacking Annexure
* Detailed physical container contents for ground staff during unpacking.
* Columns: `Bag Number`, `Original TO #`, `SKU`, `Description`, `Qty (pcs)`, `Unpacked By`, `Remarks`.\n