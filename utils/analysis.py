"""
Analysis module for Medicine Price Analysis Streamlit Dashboard.
Implements calculations for KPIs, alternative matching, manufacturer positioning, and therapeutic group insights.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def calculate_overview_kpis(df_med: pd.DataFrame, df_comp: pd.DataFrame, df_groups: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes overarching market and savings KPIs based on real project data.
    """
    total_meds = len(df_med)
    priced_mask = df_med["price"].notna()
    total_priced = priced_mask.sum()
    price_coverage_pct = round((total_priced / total_meds) * 100.0, 2) if total_meds > 0 else 0.0
    
    unique_generics = df_med["generic_name"].dropna().nunique()
    unique_mfrs = df_med["manufacturer_name"].dropna().nunique()
    unique_drug_classes = df_med["drug_class_name"].dropna().nunique()
    
    # Prices
    priced_series = df_med.loc[priced_mask, "price"]
    mean_price = round(priced_series.mean(), 2) if not priced_series.empty else 0.0
    median_price = round(priced_series.median(), 2) if not priced_series.empty else 0.0
    
    # Comparable medicines with alternatives
    total_comparable = len(df_comp)
    total_groups = len(df_groups)
    
    # Medicines with cheaper alternatives (saving_pct > 0)
    has_cheaper = df_comp[df_comp["saving_pct"] > 0]
    non_cheapest_share = round((len(has_cheaper) / total_comparable) * 100.0, 1) if total_comparable > 0 else 0.0
    median_saving_pct = round(df_comp.loc[df_comp["saving_pct"] > 0, "saving_pct"].median(), 1) if not has_cheaper.empty else 0.0
    mean_saving_pct = round(df_comp.loc[df_comp["saving_pct"] > 0, "saving_pct"].mean(), 1) if not has_cheaper.empty else 0.0
    save_gte_50_pct = round((df_comp["saving_pct"] >= 50).mean() * 100.0, 1) if total_comparable > 0 else 0.0
    
    return {
        "total_medicines": total_meds,
        "priced_medicines": int(total_priced),
        "price_coverage_pct": price_coverage_pct,
        "unique_generics": unique_generics,
        "unique_manufacturers": unique_mfrs,
        "unique_drug_classes": unique_drug_classes,
        "mean_price": mean_price,
        "median_price": median_price,
        "total_comparable": total_comparable,
        "total_groups": total_groups,
        "non_cheapest_count": len(has_cheaper),
        "non_cheapest_share": non_cheapest_share,
        "median_saving_pct": median_saving_pct,
        "mean_saving_pct": mean_saving_pct,
        "save_gte_50_pct": save_gte_50_pct
    }

def search_medicines(df_med: pd.DataFrame, query: str, limit: int = 50) -> pd.DataFrame:
    """
    Case-insensitive search across brand name and generic name.
    """
    if not query or not query.strip():
        return df_med.head(limit)
    q = query.strip().lower()
    
    mask = (
        df_med["brand_name"].fillna("").str.lower().str.contains(q, regex=False) |
        df_med["generic_name"].fillna("").str.lower().str.contains(q, regex=False)
    )
    res = df_med[mask].copy()
    
    # Prioritize exact start of brand name
    res["priority"] = np.where(
        res["brand_name"].str.lower().str.startswith(q), 1,
        np.where(res["brand_name"].str.lower().str.contains(f" {q}"), 2, 3)
    )
    res = res.sort_values(by=["priority", "price"], ascending=[True, True])
    return res.drop(columns=["priority"]).head(limit)

def get_alternatives_for_brand(df_comp: pd.DataFrame, df_full: pd.DataFrame, brand_id: int) -> Dict[str, Any]:
    """
    Retrieves all exact matched alternative brands for the target brand_id.
    Matches strictly on: generic_name + dosage_form_name + strength_normalized.
    """
    # 1. Look up in full dataset
    target_match = df_full[df_full["brand_id"] == brand_id]
    if target_match.empty:
        return {"found": False, "message": f"Brand ID {brand_id} not found."}
    
    target = target_match.iloc[0].to_dict()
    g_name = target.get("generic_name")
    df_name = target.get("dosage_form_name")
    str_norm = target.get("strength_normalized")
    curr_price = target.get("price")
    
    if pd.isna(g_name) or pd.isna(df_name) or pd.isna(str_norm):
        return {
            "found": True,
            "target": target,
            "has_group": False,
            "message": "This medicine is missing generic, dosage form, or normalized strength metadata required for alternative matching.",
            "alternatives": pd.DataFrame()
        }
    
    # Find all brands matching the exact criteria in df_full
    group_mask = (
        (df_full["generic_name"] == g_name) &
        (df_full["dosage_form_name"] == df_name) &
        (df_full["strength_normalized"] == str_norm)
    )
    group_meds = df_full[group_mask].copy()
    
    # Calculate group-level price metrics
    priced_in_grp = group_meds[group_meds["price"].notna()]
    grp_min = priced_in_grp["price"].min() if not priced_in_grp.empty else None
    grp_max = priced_in_grp["price"].max() if not priced_in_grp.empty else None
    grp_median = priced_in_grp["price"].median() if not priced_in_grp.empty else None
    
    # Sort alternatives by price ascending (nulls last)
    group_meds = group_meds.sort_values(by=["price", "brand_name"], ascending=[True, True])
    
    # Calculate savings vs current medicine
    if pd.notna(curr_price) and curr_price > 0:
        group_meds["price_diff"] = (curr_price - group_meds["price"]).round(2)
        group_meds["saving_amount"] = np.maximum(0.0, curr_price - group_meds["price"]).round(2)
        group_meds["saving_pct"] = np.where(
            group_meds["price"].notna(),
            np.round(np.maximum(0.0, curr_price - group_meds["price"]) / curr_price * 100.0, 1),
            np.nan
        )
    else:
        group_meds["price_diff"] = np.nan
        group_meds["saving_amount"] = np.nan
        group_meds["saving_pct"] = np.nan
        
    group_meds["is_selected"] = group_meds["brand_id"] == brand_id
    group_meds["is_cheapest"] = (group_meds["price"] == grp_min) & (group_meds["price"].notna())
    
    return {
        "found": True,
        "target": target,
        "has_group": True,
        "generic_name": g_name,
        "dosage_form_name": df_name,
        "strength_normalized": str_norm,
        "total_brands_in_group": len(group_meds),
        "priced_brands_in_group": len(priced_in_grp),
        "grp_min": grp_min,
        "grp_max": grp_max,
        "grp_median": grp_median,
        "alternatives": group_meds
    }
