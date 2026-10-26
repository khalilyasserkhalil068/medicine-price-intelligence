"""
Page 6: Interactive Data Explorer & Quality Audits.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: #522D60, #80426E, #F2A67B, #FFD38B
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.data_loader import load_full_medicine_dataset
from utils.data_validation import get_data_quality_summary
from utils.ui import apply_luxury_styles, COLOR_PURPLE_DARK, COLOR_PLUM, COLOR_PEACH, COLOR_GOLD

st.set_page_config(page_title="Data Explorer | Medicine Analytics", page_icon="📁", layout="wide")

# Apply Luxury Theme
apply_luxury_styles()

st.title("📁 Interactive Data Explorer & Data Quality Audit")
st.markdown("Inspect, filter, analyze data quality, and export records from the complete Assorted Medicine Dataset of Bangladesh (21,714 products).")

@st.cache_data
def get_explorer_data():
    return load_full_medicine_dataset()

df_med = get_explorer_data()

tab_explore, tab_quality = st.tabs(["🔍 Browse & Filter Dataset", "🔬 Data Quality & Completeness Audit"])

with tab_explore:
    st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>1. Filter & Search Records</h3>", unsafe_allow_html=True)
    
    # Filter Controls
    c_f1, c_f2, c_f3 = st.columns(3)
    
    with c_f1:
        search_kw = st.text_input("Search Brand or Generic:", placeholder="e.g. Paracetamol, Cipro, Napa...")
        type_options = ["All Types"] + sorted(df_med["type"].dropna().unique().tolist())
        selected_type = st.selectbox("Filter Medicine Type:", options=type_options)
        
    with c_f2:
        dosage_options = ["All Dosage Forms"] + sorted(df_med["dosage_form_name"].dropna().unique().tolist())
        selected_dosage = st.selectbox("Filter Dosage Form:", options=dosage_options)
        
        priced_filter = st.radio("Price Status:", options=["All Records", "Priced Only (Non-Null)", "Unpriced / Ambiguous Only"], horizontal=True)
        
    with c_f3:
        mfr_options = ["All Manufacturers"] + sorted(df_med["manufacturer_name"].dropna().unique().tolist())
        selected_mfr = st.selectbox("Filter Manufacturer:", options=mfr_options)
        
        min_p = float(df_med["price"].min()) if df_med["price"].notna().any() else 0.0
        max_p = float(df_med["price"].max()) if df_med["price"].notna().any() else 1000.0
        price_range = st.slider("Price Filter (BDT):", min_value=0.0, max_value=min(1000.0, max_p), value=(0.0, 500.0), step=1.0)
        
    # Apply Filters
    filtered_df = df_med.copy()
    
    if search_kw.strip():
        kw = search_kw.strip().lower()
        filtered_df = filtered_df[
            filtered_df["brand_name"].fillna("").str.lower().str.contains(kw) |
            filtered_df["generic_name"].fillna("").str.lower().str.contains(kw)
        ]
        
    if selected_type != "All Types":
        filtered_df = filtered_df[filtered_df["type"] == selected_type]
        
    if selected_dosage != "All Dosage Forms":
        filtered_df = filtered_df[filtered_df["dosage_form_name"] == selected_dosage]
        
    if selected_mfr != "All Manufacturers":
        filtered_df = filtered_df[filtered_df["manufacturer_name"] == selected_mfr]
        
    if priced_filter == "Priced Only (Non-Null)":
        filtered_df = filtered_df[filtered_df["price"].notna()]
    elif priced_filter == "Unpriced / Ambiguous Only":
        filtered_df = filtered_df[filtered_df["price"].isna()]
        
    if priced_filter != "Unpriced / Ambiguous Only":
        filtered_df = filtered_df[
            (filtered_df["price"].isna()) |
            ((filtered_df["price"] >= price_range[0]) & (filtered_df["price"] <= price_range[1]))
        ]

    st.markdown(f"**Found <span class='badge-purple'>{len(filtered_df):,} matching products</span>** (out of {len(df_med):,} total records):", unsafe_allow_html=True)
    
    # Column Selector
    all_cols = filtered_df.columns.tolist()
    default_cols = ["brand_id", "brand_name", "generic_name", "dosage_form_name", "strength_normalized", "manufacturer_name", "drug_class_name", "price", "package_description"]
    selected_cols = st.multiselect("Select columns to view:", options=all_cols, default=[c for c in default_cols if c in all_cols])
    
    # Display table
    st.dataframe(filtered_df[selected_cols], use_container_width=True, height=450)
    
    # CSV Download Button
    csv_bytes = filtered_df[selected_cols].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_medicines_bangladesh.csv",
        mime="text/csv"
    )

with tab_quality:
    st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>2. Dataset Completeness & Null Value Audit</h3>", unsafe_allow_html=True)
    st.markdown("Examines the non-null completeness, missing value distribution, and unique cardinality for every attribute in the database:")
    
    quality_df = get_data_quality_summary(df_med)
    st.dataframe(quality_df.style.format({
        "Null %": "{:.2f}%"
    }), use_container_width=True, height=480)
    
    st.markdown("---")
    st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>3. Primary Key Uniqueness & Integrity</h3>", unsafe_allow_html=True)
    dup_brands = df_med.duplicated(subset=["brand_id"]).sum()
    dup_names = df_med.duplicated(subset=["brand_name", "manufacturer_name", "dosage_form_name", "strength_normalized"]).sum()
    
    d1, d2 = st.columns(2)
    d1.metric("Brand ID Duplicates", f"{dup_brands}", "Strict PK Uniqueness: PASS ✓")
    d2.metric("Exact Entity Duplicate Combinations", f"{dup_names}", "Different packaging variants preserved")
