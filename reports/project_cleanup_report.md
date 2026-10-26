# Project Cleanup Report

## Overview
This document details the cleanup and organization pass performed on the Assorted Medicine Dataset of Bangladesh project prior to the SQL Database phase. The goal was to ensure reproducibility, clarity, and maintainability.

## 1. Files Kept
- **`data/raw/*.csv`**: The original, immutable source data. Kept as the source of truth.
- **`data/cleaned/*.csv`**: The validated outputs of the cleaning pipeline. Kept as inputs for integration and SQL phases.
- **`notebooks/01_data_profiling.ipynb`**: Initial data profiling and understanding workflow.
- **`notebooks/02_data_cleaning.ipynb`**: Core cleaning pipeline.
- **`notebooks/03_data_integration.ipynb`**: Data integration and modeling analysis.
- **`reports/`**: All validated reports (cleaning, profiling, integration, ERD, SQL schema, relationships, key mappings). Kept as crucial design documentation.
- **`requirements.txt`**: Project dependencies.
- **`.gitignore`**: Version control rules.

## 2. Files Removed
The following files were removed as they were obsolete, scratch, or duplicated logic that has since been properly incorporated into the Jupyter notebooks:
- `clean_data.py`: Obsolete script (replaced by `02_data_cleaning.ipynb`).
- `profile_data.py`: Obsolete script (replaced by `01_data_profiling.ipynb`).
- `gen_notebook.py`: Temporary one-time generation script.
- `Data_Cleaning_Phase.ipynb`: Old experimental notebook.
- `scratch/` directory: Contained temporary analysis scripts (`inspect_integration.py`, `build_nb3.py`, etc.) whose insights and outputs have now been properly baked into `03_data_integration.ipynb` and the generated reports.

## 3. Files Moved
- `scratch/gen_mappings.py` → `scripts/generate_mappings.py`: This script generates the key mapping tables for the SQL phase. It is not a scratch script but a reproducible pipeline component, so it was promoted to the `scripts/` directory and its paths were updated to be relative and portable.

## 4. Code Improvements
- **Portable Paths**: Removed hard-coded paths (e.g. `e:/DEPI/...`) in scripts. Used `pathlib.Path(__file__).resolve().parents[1]` and `Path.cwd().parent` to ensure the project can be cloned and run on any machine or operating system.
- **Removed Scratch Directories**: Purged temporary working directories to avoid clutter.
- **Directory Structure**: Validated the strict separation of `data/raw`, `data/cleaned`, `notebooks/`, `reports/`, and `scripts/`.

## 5. Notebook Improvements
- Verified that all three core notebooks (`01_data_profiling.ipynb`, `02_data_cleaning.ipynb`, `03_data_integration.ipynb`) use portable, project-relative paths.
- Ensured they represent a clear, logical, and sequential Data Science workflow with well-documented markdown sections.

## 6. Report Cleanup
- Validated that `reports/` only contains finalized, meaningful analysis files.
- Verified that the `reports/project_manifest.csv` accurately tracks the inputs, outputs, and purposes of all current files.

## 7. Reproducibility
The project is fully reproducible. To rerun the pipeline from scratch on a new machine:
1. `git clone` the repository.
2. `pip install -r requirements.txt`
3. Launch `jupyter notebook`.
4. Run the notebooks in sequential order (`01` -> `02` -> `03`).
5. (Optional) Run `python scripts/generate_mappings.py` to regenerate the SQL key mappings.

## 8. Remaining Issues
- **None.** The project is completely clean, documented, and organized.
- It is 100% ready for the **SQL Database Design and Implementation** phase.
