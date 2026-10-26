# Data Cleaning Report

## 1. Dataset Overview
The raw dataset consists of 6 CSV files (medicine, generic, manufacturer, dosage form, drug class, indication). Data was preserved in `data/raw/` and only clean versions were generated in `data/cleaned/`.

## 2. Raw Data Quality
The raw data had some missing values, especially in `medicine.csv` (strength, package container, Package Size). Text fields contained leading/trailing spaces. The generic descriptions contained HTML tags. Price information was embedded inside the `package container` text along with currency symbols.

## 3. Missing Values
Missing values were left as NaN. No rows were dropped purely due to missing fields to avoid data loss. Example: Missing strength values were preserved as NaN rather than inventing strength values.

## 4. Duplicate Analysis
Exact duplicate rows were targeted for removal. Any identical rows across all columns were removed. We did NOT remove duplicated entities (e.g. repeated brand names) as they often represent different strengths, forms, or packages.

## 5. Text Standardization
Leading and trailing whitespace were removed from all text columns across all files. Placeholder strings like `N/A`, `NA`, `null`, `None`, `-` and empty strings were replaced with standard NaN.

## 6. Price Extraction
**Initial Parser Failure:**
The original regex `r'^([^:]+):\s* 3\s*([\d\.]+)'` was too restrictive and hardcoded a broken encoding artifact (` 3`) instead of correctly matching the Bangladeshi Taka symbol (`৳`). It also failed to process the diverse pricing formats, resulting in 0% numerical extraction (all `price`, `pack_price`, and `pack_size` were `NULL`).

**New Parsing Strategy:**
A robust parser was developed based on profiling the actual patterns in `package container`:
1. **Unit Price + Pack / Description + Pack:** e.g., `Unit Price: ৳ 6.00,(50's pack: ৳ 300.00)`. Extracted `price`, `pack_size`, `pack_price`.
2. **Description + Unit ONLY:** e.g., `50 ml bottle: ৳ 250.94`. Extracted `price` representing the unit price of that container.
3. **Ambiguous / Multiple Prices:** e.g., `10 gm tube: ৳ 70.00,30 gm tube: ৳ 150.00`. These cases were skipped (set to `NULL`) to preserve correctness.
4. **Currency:** Normalized safely to `BDT`. Commas in prices (e.g., `1,454.37`) were removed.

**Extraction Rates:**
- **price extraction rate:** 93.75%
- **pack_price extraction rate:** 62.30%
- **pack_size extraction rate:** 62.30%
- **Ambiguous rows left as NULL:** ~1,270
- **No pricing information left as NULL:** ~78 (including purely empty fields)

## 7. Strength Normalization
Strength was preserved in `strength_raw` and normalized whitespace variants were placed in `strength_normalized`. No medically significant strength variations were destroyed.

## 8. Package Normalization
The `package container` was preserved as `package_container_raw`.

## 9. Referential Integrity
Cross-references like `generic` in medicine to `generic name` in generic.csv were verified. Cleaned values matched original identifiers to preserve integrity.

## 10. Data Quality After Cleaning
The cleaned datasets are structurally consistent, numeric prices are properly extracted, and HTML artifacts were safely removed from medical descriptions.

## 11. Decisions Made
- Replaced missing/null placeholder strings with NaN.
- Extracted HTML text carefully to keep full readable medical text.
- Prioritized extraction correctness over extraction rate: ambiguous prices were left as NULL.

## 12. Decisions NOT Made
- We did not guess prices or perform calculations (e.g., `price * pack_size`) when ambiguous cases appeared.

## 13. Remaining Limitations
Some package containers still have complex string formats representing multiple distinct prices for distinct forms. These remain unparsed and are retained in the raw `package_description` string.
