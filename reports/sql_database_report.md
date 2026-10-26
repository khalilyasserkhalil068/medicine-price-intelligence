# SQL Database Implementation Report

## 1. Database Overview
* **Database Name**: `MedicineDB`
* **Server Environment**: Microsoft SQL Server Express (`.\SQLEXPRESS`)
* **Schema**: `dbo`

## 2. Tables Created
We successfully implemented the following core tables conforming exactly to the normalized relational model derived during the Data Integration phase:
- `manufacturers` (240 rows)
- `dosage_forms` (113 rows)
- `drug_classes` (421 rows)
- `indications` (2043 rows)
- `generics` (1711 rows)
- `medicines` (21,714 rows)

## 3. Data Types & Constraints
- **Primary Keys**: Used the validated source IDs (`manufacturer_id`, `generic_id`, `brand_id`, etc.). All are INT and NOT NULL.
- **Foreign Keys**: Created with strict referential integrity.
  - `medicines.generic_id` → `generics` (NULL allowed for 2 specific records missing generics in source)
  - `medicines.manufacturer_id` → `manufacturers`
  - `medicines.dosage_form_id` → `dosage_forms`
  - `generics.drug_class_id` → `drug_classes`
  - `generics.indication_id` → `indications`
- **Check Constraints**:
  - `medicines.type` IN ('allopathic', 'herbal')
  - Prices >= 0
  - Pack sizes > 0
- **Defaults**: `currency` defaults to 'BDT'.

## 4. Drug Class Canonicalization
The Data Integration phase uncovered 20 semantic duplicate `drug_class_name`s that mapped to 52 duplicate IDs.
- **Resolution**: We deduplicated these before inserting them into `MedicineDB`, retaining the lowest integer ID for each name as the canonical ID.
- **Result**: The table successfully constrained `drug_class_name` to be UNIQUE, resulting in 421 rows (down from the 453 rows in the raw CSV).

## 5. Indexes
Foreign key indexes were added to optimize join operations for future EDA:
- `IX_generics_drug_class_id`
- `IX_generics_indication_id`
- `IX_medicines_generic_id`
- `IX_medicines_manufacturer_id`
- `IX_medicines_dosage_form_id`

## 6. Source vs SQL Reconciliation
| Source File | SQL Table | Source Row Count | SQL Row Count | Status |
|-------------|-----------|------------------|---------------|--------|
| `medicine_clean.csv` | `medicines` | 21,714 | 21,714 | PASS |
| `indication_clean.csv` | `indications` | 2,043 | 2,043 | PASS |
| `generic_clean.csv` | `generics` | 1,711 | 1,711 | PASS |
| `manufacturer_clean.csv` | `manufacturers` | 240 | 240 | PASS |
| `dosage_form_clean.csv` | `dosage_forms` | 113 | 113 | PASS |
| `drug_class_clean.csv` | `drug_classes` | 453 | 421 (Deduplicated) | PASS |

## 7. Price Extraction Reload & Validation
During initial SQL validation, it was discovered that 100% of rows had `NULL` for `price`, `pack_price`, and `pack_size`. This was traced back to a regex extraction failure in the upstream Data Cleaning pipeline (an encoding artifact prevented matching the `৳` symbol). The parser was rewritten to successfully extract prices and `dbo.medicines` was safely reloaded via an `XACT_ABORT ON` transaction. 

**Validated Price Loading Metrics:**
- **Total medicines**: 21,714
- **Extracted `price`**: 20,357 (93.75%)
- **Extracted `pack_price`**: 13,527 (62.30%)
- **Extracted `pack_size`**: 13,527 (62.30%)
- **Missing `price`**: 1,357 
  - *Ambiguous (Multiple distinct prices for different pack variants)*: 1,279 rows (left NULL intentionally to preserve correctness)
  - *No pricing info available*: 36 rows
  - *Raw package field NULL*: 42 rows

**Validation Rules Run:**
- **Orphan Records**: 0
- **Negative Prices**: 0
- **Invalid Pack Sizes**: 0
- **Duplicate Class Names**: 0

## 8. Analytical Views Created
- `vw_medicine_details`
- `vw_generic_price_comparison`
- `vw_generic_brand_counts`

## 9. Known Limitations
- The `medicines.generic_id` allows NULL because 2 source records lacked generic identifiers.
- Ambiguous multi-price strings (e.g., `10 gm tube: ৳ 70.00,30 gm tube: ৳ 150.00`) are not forced into a single numerical column and remain as `NULL` in the DB numerical columns (but text is preserved in `package_description`).
