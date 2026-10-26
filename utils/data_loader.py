"""
Data loader module for Medicine Price Analysis Streamlit Dashboard.
Handles relative paths, data loading, and caching for all project datasets.
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

# Determine project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ANALYSIS_DIR = PROJECT_ROOT / "reports" / "analysis"
DB_PATH = DATA_DIR / "medicine.db"

def get_db_connection():
    """Returns a SQLite connection to data/medicine.db."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def load_full_medicine_dataset() -> pd.DataFrame:
    """
    Loads the full 21,714 medicine records from SQLite vw_medicine_details.
    Includes both priced and unpriced medicines, allopathic and herbal.
    """
    conn = get_db_connection()
    query = """
    SELECT 
        m.brand_id,
        m.brand_name,
        m.type,
        m.generic_name,
        m.dosage_form_name,
        m.strength,
        m.strength_normalized,
        m.manufacturer_name,
        m.drug_class_name,
        m.indication_name,
        m.price,
        m.pack_price,
        m.pack_size,
        m.currency,
        m.package_description
    FROM vw_medicine_details m
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Cast appropriate data types
    df["brand_id"] = df["brand_id"].astype(int)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["pack_price"] = pd.to_numeric(df["pack_price"], errors="coerce")
    df["pack_size"] = pd.to_numeric(df["pack_size"], errors="coerce")
    
    return df

def load_alternatives_per_medicine() -> pd.DataFrame:
    """
    Loads reports/analysis/alternatives_per_medicine.csv (18,476 comparable medicines).
    Contains calculated alternative metrics, savings, and price index per brand.
    """
    csv_path = ANALYSIS_DIR / "alternatives_per_medicine.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df["brand_id"] = df["brand_id"].astype(int)
    numeric_cols = ["price", "grp_n", "n_alternatives", "grp_min", "grp_median", "grp_max", "saving_amount", "saving_pct", "price_index"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_alternatives_per_group() -> pd.DataFrame:
    """
    Loads reports/analysis/alternatives_per_group.csv (1,875 equivalent groups).
    Contains group statistics, spreads, and max saving percentages.
    """
    csv_path = ANALYSIS_DIR / "alternatives_per_group.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    num_cols = ["brands", "min_price", "median_price", "max_price", "spread_x", "max_saving_pct"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_manufacturer_price_index() -> pd.DataFrame:
    """
    Loads reports/analysis/manufacturer_price_index.csv (107 manufacturers with >= 30 comparable products).
    """
    csv_path = ANALYSIS_DIR / "manufacturer_price_index.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df["n"] = pd.to_numeric(df["n"], errors="coerce").astype(int)
    df["median_index"] = pd.to_numeric(df["median_index"], errors="coerce")
    df["pct_cheapest"] = pd.to_numeric(df["pct_cheapest"], errors="coerce")
    
    # Categorize manufacturers by market price position
    df["position_category"] = np.where(
        df["median_index"] < 0.95, "Budget / Economical",
        np.where(df["median_index"] > 1.05, "Premium / Expensive", "Fair / Market Average")
    )
    return df

def load_drug_classes_summary() -> pd.DataFrame:
    """
    Aggregates drug classes by medicine counts and price statistics from SQLite.
    """
    conn = get_db_connection()
    query = """
    SELECT 
        dc.drug_class_name,
        COUNT(m.brand_id) AS total_products,
        COUNT(m.price) AS priced_products,
        ROUND(AVG(m.price), 2) AS avg_price,
        ROUND(MIN(m.price), 2) AS min_price,
        ROUND(MAX(m.price), 2) AS max_price
    FROM drug_classes dc
    JOIN generics g ON dc.drug_class_id = g.drug_class_id
    JOIN medicines m ON g.generic_id = m.generic_id
    GROUP BY dc.drug_class_id, dc.drug_class_name
    HAVING COUNT(m.brand_id) >= 5
    ORDER BY total_products DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
