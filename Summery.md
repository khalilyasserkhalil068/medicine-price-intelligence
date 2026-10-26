I am working on a Data Science project that analyses medicine data from Kaggle, titled:

"Assorted Medicine Dataset of Bangladesh 💊💉"

Treat the information below as the primary context for the project, and do not start from scratch.

## 🎯 Project goal

Analyse the medicine data and extract useful insights, in particular:

1. Number of medicines
2. Number of generics
3. Number of manufacturers
4. Average prices
5. Cheapest alternatives
6. Most expensive alternatives
7. Number of alternatives per medicine
8. Price distribution
9. Price and package analysis
10. Savings percentage between alternatives

Note:
The current dataset does not contain pharmacy / stock / availability data, so we do not infer whether a medicine is available in pharmacies without an additional source.

## 📊 The original dataset files

### medicine.csv
21,714 rows — 10 columns

Columns:
- brand id
- brand name
- type
- slug
- dosage form
- generic
- strength
- manufacturer
- package container
- Package Size

Missing values:
- generic: 2
- strength: 849
- package container: 42
- Package Size: 7,779

Exact duplicate rows: 0

### generic.csv
1,711 rows — 22 columns

Most important columns:
- generic id
- generic name
- drug class
- indication
- monograph link
- medical description fields

### manufacturer.csv
240 rows — 5 columns

### dosage form.csv
113 rows — 4 columns

### drug class.csv
453 rows — 4 columns

There are duplicate names:
453 source rows → 421 canonical unique drug classes.

### indication.csv
2,043 rows — 4 columns

## 🔗 Referential integrity

The relationships were verified:

- medicine.generic → generic.generic name = 100% match
- medicine.manufacturer → manufacturer = 100% match
- medicine.dosage form → dosage form = 100% match
- generic.drug class → drug class = 100% match
- generic.indication → indication = 100% match

The original relationships in the CSV files rely on textual values, not on IDs.

## 🧹 Data cleaning

The cleaning stage is complete.

What was done:
- raw data preserved
- whitespace cleaned
- placeholders unified
- HTML handled inside text fields
- cleaned fields created
- strength cleaned
- the following fields were created:
  - package_description
  - price
  - pack_price
  - pack_size
  - currency = BDT
  - strength_raw
  - strength_normalized
- no missing values invented
- no availability invented
- no artificial alternative labels created

## 💰 Price extraction

There was a problem extracting prices from `package_description`, and it has been fixed.

Five patterns were detected:

1. Unit Price + Pack
   Example:
   `Unit Price: ৳ 6.00,(50's pack: ৳ 300.00),`

2. Description + Pack
   Example:
   `10 ml drop: ৳ 7.28,(12's pack: ৳ 87.36),`

3. Description + Unit only
   Example:
   `50 ml bottle: ৳ 250.94`

4. Multiple Units / Multiple Prices
   Example:
   `10 gm tube: ৳ 70.00,30 gm tube: ৳ 150.00`

   These cases are considered ambiguous, and the price fields were intentionally left NULL instead of picking a price incorrectly.

5. No price / unavailable

> Note on the currency symbol: the examples above are the raw strings exactly as they appear in the source data, which use the ৳ (taka) sign. Everywhere the project itself displays a price it uses `BDT`, and the `currency` column is `BDT`.

### Final price statistics

Total medicines:
21,714

price non-null:
20,357

price null:
1,357

pack_price non-null:
13,527

pack_size non-null:
13,527

Ambiguous multiple-pricing:
1,279

Raw package NULL:
42

No pricing information:
36

Reconciliation:
20,357 + 1,357 = 21,714

Status:
RECONCILIATION PASSED — READY FOR SQL RELOAD

## 🗄️ SQL Server database

I am using:

SQL Server Express
Instance:
DESKTOP-GEUHMVT\SQLEXPRESS

Database:
MedicineDB

Schema:
dbo

And I use SQL Server Management Studio 20.

### Tables

- manufacturers = 240
- dosage_forms = 113
- drug_classes = 421
- indications = 2043
- generics = 1711
- medicines = 21714

### Main relationships

manufacturer 1:N medicine
generic 1:N medicine
dosage_form 1:N medicine
drug_class → generic
indication → generic

### Important

There are 2 medicines without a generic in the source data, therefore `generic_id` in `medicines` allows NULL.

FK orphan validation:
0

Invalid prices:
0

Invalid pack sizes:
0

## 🗂️ SQL files

Created:

sql/01_create_database.sql
sql/02_create_tables.sql
sql/03_create_constraints.sql
sql/04_load_data.sql
sql/05_validation.sql
sql/06_analysis_queries.sql
sql/load_medicines_only.sql

Views:
- vw_medicine_details
- vw_generic_price_comparison
- vw_generic_brand_counts

Indexes exist on the foreign keys.

## 🔄 SQL price reload

A safe reload of the `medicines` table was performed after fixing price extraction.

With none of the following:
- DROP DATABASE
- DROP TABLE
- deleting the schema
- deleting PK / FK / indexes

The reload ran inside a transaction with:
SET XACT_ABORT ON

And the result:

Total = 21,714
Price = 20,357
Price NULL = 1,357
Pack Price = 13,527
Pack Size = 13,527
Ambiguous = 1,279
Orphans = 0
Invalid prices = 0
Invalid pack sizes = 0

## 📁 Project structure

The project is roughly organised as follows:

data/
  raw/
  cleaned/

notebooks/

reports/

scripts/

sql/

README.md
requirements.txt
.gitignore
.env.example

Removed:
- venv
- scratch_*.py
- debugging temporary files

## 📌 Current project status

Data Profiling ✅
Data Cleaning ✅
Data Integration ✅
Project Cleanup ✅
SQL Server Database ✅
Price Extraction ✅
SQL Reload ✅

### Current step

Before moving into EDA, I want to be strongly confident that price extraction is correct.

We need price validation covering:

1. Comparing `price` against `package_description`
2. Verifying `pack_price`
3. Verifying `pack_size`
4. Detecting suspicious prices
5. Detecting parsing errors
6. Verifying ambiguous cases
7. Calculating the price extraction success rate
8. Producing a PASS / WARNING / FAIL report

Once the price quality is confirmed, we move on to:

EDA → Alternative Analysis → Price Analysis → Visualization/Dashboard

## ⚠️ Important rules

- Do not invent data.
- Do not treat Generic = Active Ingredient as an automatic assumption.
- Do not treat a repeated brand name as a duplicate without analysis.
- Do not invent availability.
- Do not change the raw data.
- Do not delete missing values without a clear reason.
- Do not pick a price from an ambiguous package description at random.
- Any change to the data must be explainable and documented.
- The goal is a real Data Science project, not just a dashboard.

Start from the last point we reached:
PRICE EXTRACTION VALIDATION

And before making any change to the project, explain what you are going to do and why.
