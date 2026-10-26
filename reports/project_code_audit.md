# Project Code Audit

## 1. Project Structure Before
The project had a flat mix of raw code, temporary files, data files, and logs in the root directory. Jupyter notebook code was available but without distinct organizational directories or proper markdown structuring. Path handling was somewhat localized. The `clean_data.py`, `profile_data.py`, `gen_notebook.py`, and `Data_Cleaning_Phase.ipynb` were all clumped together.

## 2. Project Structure After
The project has been refactored into a standardized Data Science layout.
- `data/raw/` contains unmodified raw CSV files.
- `data/cleaned/` contains the cleaned output from the Data Cleaning Phase.
- `notebooks/` contains well-structured, reproducible Jupyter notebooks running the data pipelines (`01_data_profiling.ipynb` and `02_data_cleaning.ipynb`).
- `reports/` stores profiling logs, transformation logs, and audit files.
- `requirements.txt`, `.gitignore`, and `README.md` are added.

## 3. Important Files
| File | Purpose | Input | Output | Status |
| ---- | ------- | ----- | ------ | ------ |
| `notebooks/01_data_profiling.ipynb` | Profiles raw data to check nulls, dupes, ranges | `data/raw/*.csv` | `reports/profiling_report.csv` | Ready |
| `notebooks/02_data_cleaning.ipynb` | Core reproducible cleaning logic (imputation, deduplication, regex extraction) | `data/raw/*.csv` | `data/cleaned/*.csv` | Ready |
| `reports/cleaning_report.md` | Qualitative report on decisions made during cleaning | N/A | N/A | Completed |
| `reports/data_quality_report.csv` | Validation report post-cleaning | `data/cleaned/*.csv` | N/A | Completed |

## 4. Files Kept
- All raw CSV data was preserved and moved to `data/raw/`.
- The previously generated cleaned CSVs in `data/cleaned/` were kept.
- Important analytical logs from the previous stage (`profiling_report.csv`, `transformation_log.csv`) were preserved.

## 5. Files Ignored
- `venv/`
- `__pycache__/`
- `scratch/`
- `*.pyc`
- `.ipynb_checkpoints/`

## 6. Files Removed
- `clean_data.py` (logic moved to `02_data_cleaning.ipynb`)
- `profile_data.py` (logic moved to `01_data_profiling.ipynb`)
- `gen_notebook.py` (was a temporary generation script)
- `Data_Cleaning_Phase.ipynb` (renamed and restructured to `notebooks/02_data_cleaning.ipynb`)

## 7. Code Improvements
- **Portable Paths**: Replaced string-based paths with `pathlib.Path` relative to the current working directory.
- **Notebook Structuring**: Added numbered Markdown headings (Objective, Imports, Configuration, Load Data, Processing, Save Output) to all Jupyter Notebooks.
- **Meaningful Comments**: Added explicit comments on *why* raw data is preserved, *why* exact duplicates are stripped while semantic duplicates are kept, and *why* specific RegEx logic was constructed.

## 8. Potential Issues
- **Price RegEx Encoding Bug**: The regex in `02_data_cleaning.ipynb` searches for the artifact ` 3` instead of the original `৳` (Bangladeshi Taka symbol). This bug was introduced due to an encoding translation in the previous phase when writing the python script. However, because we are strictly prohibited from changing the Data Science results during this Code Organization phase, this bug was intentionally preserved. This must be fixed in a future iteration when updating the cleaning logic is permitted.

## 9. Reproducibility Status
The project can now be completely rerun from scratch by sequentially executing the `notebooks/01_...` and `notebooks/02_...` notebooks. The inputs are static raw CSVs, and the output targets are well-defined.
