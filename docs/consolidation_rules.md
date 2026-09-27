# SKU Consolidation, Delta Updates & Audit Rules

## 1. Consolidation Principles

When retail store associates pack inventory over days, they generate dozens of bag-wise transfer orders. The consolidation engine merges these orders into a unified product catalog suitable for bulk vehicle transit while retaining full physical traceability.

---

## 2. SKU Sanitization & Cleaning Rules

To prevent identical items from failing to merge due to associate formatting noise:
1. **SKU Sanitization**:
   * Strips prefixes like `SKU:`, `#`, `*`, spaces, and punctuation.
   * Converts to standardized uppercase alphanumeric string: `SKU = re.sub(r'[^A-Za-z0-9]', '', raw_sku).upper()`.
2. **Item Description Reconciliation**:
   * If two bags record the same SKU with slight description variations (e.g. `*BANGU COTTON SAREE` vs `BANGU COTTON SAREE`), the cleaner description (stripped of prefix flags) or the longest non-empty description is adopted.

---

## 3. The 3-Tuple Composite Aggregation Key

Items are consolidated using a strict 3-tuple key:

$$\text{Aggregation Key} = \big( \text{SKU}, \ \text{Unit Cost Price}, \ \text{HSN/SAC Code} \big)$$

### Rationale:
1. **SKU Matching**: Identical SKUs represent the exact same merchandise identity.
2. **Cost Price Separation**: If the same SKU was acquired or valued at different cost prices (e.g., older stock at ₹400 and newer stock at ₹450), they are **never** averaged. Averaging corrupts inventory valuation and accounting integrity. They are preserved as separate distinct lines.
3. **Tax Code Integrity**: Items under different HSN codes remain separate to guarantee statutory GST transit and e-Way bill compliance.

---

## 4. Bag Cancellation & De-Selection Workflows

In live dispatch environments, store managers may need to drop a damaged or held-back container (e.g. `Bag 85` held back) just before vehicle movement:
* The user interface and CLI support `--exclude-bags "BAG-85,BAG-86"` or interactive checkbox de-selection.
* When a bag is excluded, all associated raw order items are pruned from the aggregation set, and totals are recomputed dynamically.

---

## 5. Incremental Delta Updates & Last-Minute Order Ingestion

In physical logistics, store staff frequently pack and add late bags right up until vehicle departure (as seen when Sujatha Nagar added +8 orders `HCT-719 to 726` and then +5 orders `HCT-727 to 731`).

The **Delta Processor** supports seamless incremental updates:
1. Reads all valid original orders in the branch.
2. Calculates the baseline (previously consolidated state).
3. Computes the **Added Delta**:
   $$\Delta \text{Orders} = \text{New Orders Added}, \quad \Delta \text{Qty} = \sum \text{New Qty}, \quad \Delta \text{Amount} = \sum \text{New Amount}$$
4. Re-consolidates the full dataset and regenerates the updated Transit PDF and Excel checklist.
5. Emits an audit comparison table:

| Consignment Stage | Orders | Items | Pieces | Consignment Value (₹) | Bags |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Initial Baseline** | 78 orders | 90 items | 2,856 pcs | ₹16,24,621.00 | 78 bags |
| **Batch Add 1 (HCT-719 to 726)**| +8 orders | +8 items | +264 pcs | +₹2,34,100.00 | +8 bags |
| **Batch Add 2 (HCT-727 to 731)**| +5 orders | +12 items | +155 pcs | +₹1,43,815.00 | +5 bags |
| **Final Consignment Total** | **91 orders** | **110 items** | **3,275 pcs** | **₹20,02,536.00** | **91 bags** |

---

## 6. Currency & Number-to-Words Engine

To comply with statutory legal standards for transit challans and invoices, numerical grand totals are translated into formal words.

### Indian Numbering System (`num_to_words_in`)
Unlike Western notation (Thousands, Millions, Billions), Indian trade documentation uses **Crores, Lakhs, Thousands, Hundreds**:
* $1\text{ Lakh} = 1,00,000$
* $1\text{ Crore} = 1,00,00,000$

#### Syntax Rules:
* Value ₹20,02,536.00 $\rightarrow$ `Indian Rupee Twenty Lakh Two Thousand Five Hundred Thirty-Six Only`
* Value ₹6,01,808.50 $\rightarrow$ `Indian Rupee Six Lakh One Thousand Eight Hundred Eight and Fifty Paise Only`
* Handles single-digit paise correctly: ₹100.05 $\rightarrow$ `One Hundred and Five Paise`, ₹100.50 $\rightarrow$ `One Hundred and Fifty Paise`.
* Handles multi-crore values deterministically.
* Concludes with mandatory legal suffix `Only`.\n