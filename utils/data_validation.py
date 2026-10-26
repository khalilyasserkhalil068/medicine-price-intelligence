"""
Data validation module for Medicine Price Analysis Streamlit Dashboard.
Ensures data integrity, validates calculation inputs, and guards against invalid comparisons.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

def validate_price_value(price: Any) -> Tuple[bool, str]:
    """
    Validates that a price value is numeric, non-null, and non-negative.
    """
    if price is None or pd.isna(price):
        return False, "Price is missing (NULL)."
    try:
        val = float(price)
        if val < 0:
            return False, "Price cannot be negative."
        if val == 0:
            return False, "Price is zero (free/unlisted), cannot calculate percentage savings."
        return True, ""
    except (ValueError, TypeError):
        return False, "Price must be a valid numeric value."

def validate_quantity_value(quantity: Any) -> Tuple[bool, float, str]:
    """
    Validates that a quantity is positive and numeric.
    """
    if quantity is None:
        return False, 1.0, "Quantity cannot be empty."
    try:
        val = float(quantity)
        if val <= 0:
            return False, 1.0, "Quantity must be greater than zero."
        return True, val, ""
    except (ValueError, TypeError):
        return False, 1.0, "Quantity must be a valid number."

def calculate_savings_safely(original_price: float, alternative_price: float, quantity: float = 1.0) -> Dict[str, Any]:
    """
    Safely calculates unit savings, total savings, and savings percentage.
    Correctly handles:
    - Missing or invalid prices.
    - Zero original prices.
    - Alternatives that cost more than the original medicine (displays additional cost).
    - Returns structured status and flags.
    """
    valid_orig, msg_orig = validate_price_value(original_price)
    if not valid_orig:
        return {
            "status": "error",
            "message": f"Original medicine: {msg_orig}",
            "unit_saving": 0.0,
            "total_saving": 0.0,
            "saving_pct": 0.0,
            "costs_more": False,
            "additional_cost": 0.0
        }
        
    valid_alt, msg_alt = validate_price_value(alternative_price)
    if not valid_alt:
        return {
            "status": "error",
            "message": f"Alternative medicine: {msg_alt}",
            "unit_saving": 0.0,
            "total_saving": 0.0,
            "saving_pct": 0.0,
            "costs_more": False,
            "additional_cost": 0.0
        }
        
    valid_qty, clean_qty, msg_qty = validate_quantity_value(quantity)
    if not valid_qty:
        return {
            "status": "error",
            "message": msg_qty,
            "unit_saving": 0.0,
            "total_saving": 0.0,
            "saving_pct": 0.0,
            "costs_more": False,
            "additional_cost": 0.0
        }
        
    orig = float(original_price)
    alt = float(alternative_price)
    
    unit_diff = orig - alt
    total_diff = unit_diff * clean_qty
    
    if unit_diff < 0:
        # Alternative is actually MORE expensive
        additional_unit = abs(unit_diff)
        additional_total = abs(total_diff)
        more_pct = round((additional_unit / orig) * 100.0, 2)
        return {
            "status": "costs_more",
            "message": "Alternative costs more than the original medicine.",
            "unit_saving": 0.0,
            "total_saving": 0.0,
            "saving_pct": 0.0,
            "costs_more": True,
            "additional_unit_cost": round(additional_unit, 2),
            "additional_total_cost": round(additional_total, 2),
            "additional_cost_pct": more_pct,
            "original_total": round(orig * clean_qty, 2),
            "alternative_total": round(alt * clean_qty, 2),
            "quantity": clean_qty
        }
    elif unit_diff == 0:
        return {
            "status": "same_price",
            "message": "Alternative has the exact same price as the original medicine.",
            "unit_saving": 0.0,
            "total_saving": 0.0,
            "saving_pct": 0.0,
            "costs_more": False,
            "original_total": round(orig * clean_qty, 2),
            "alternative_total": round(alt * clean_qty, 2),
            "quantity": clean_qty
        }
    else:
        saving_pct = round((unit_diff / orig) * 100.0, 2)
        return {
            "status": "savings",
            "message": "Savings available.",
            "unit_saving": round(unit_diff, 2),
            "total_saving": round(total_diff, 2),
            "saving_pct": saving_pct,
            "costs_more": False,
            "original_total": round(orig * clean_qty, 2),
            "alternative_total": round(alt * clean_qty, 2),
            "quantity": clean_qty
        }

def get_data_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes columns, non-null counts, null percentages, and data types.
    """
    total = len(df)
    summary = []
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = round((null_count / total) * 100.0, 2) if total > 0 else 0.0
        unique_cnt = df[col].nunique()
        summary.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Non-Null Count": total - null_count,
            "Null Count": null_count,
            "Null %": null_pct,
            "Unique Values": unique_cnt
        })
    return pd.DataFrame(summary)
