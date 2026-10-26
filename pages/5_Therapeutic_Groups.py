"""
Page 5: Therapeutic Group Analysis & Crowded Generics.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: #522D60, #80426E, #F2A67B, #FFD38B
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.data_loader import (
    load_full_medicine_dataset,
    load_alternatives_per_group,
    load_drug_classes_summary
)
from utils.ui import (
    apply_luxury_styles,
    get_luxury_chart_layout,
    COLOR_PURPLE_DARK,
    COLOR_PLUM,
    COLOR_PEACH,
    COLOR_GOLD,
    PLOTLY_PALETTE,
    PLOTLY_CONFIG
)

st.set_page_config(page_title="Therapeutic Groups | Medicine Analytics", page_icon="🧬", layout="wide")

# Apply Luxury Theme
apply_luxury_styles()

st.title("🧬 Therapeutic Group & Active Compound Analysis")
st.markdown("Examine pharmaceutical competition across therapeutic drug classes and active generic molecules in Bangladesh.")

@st.cache_data
def get_therapeutic_data():
    df_med = load_full_medicine_dataset()
    df_groups = load_alternatives_per_group()
    df_dc = load_drug_classes_summary()
    return df_med, df_groups, df_dc

df_med, df_groups, df_dc = get_therapeutic_data()

# Methodological Notice
with st.expander("ℹ️ Aggregation Level & Medical Distinction (Important)", expanded=True):
    st.markdown(f"""
    * **Therapeutic Drug Class vs. Equivalent Alternative:**
      * A **Therapeutic Drug Class** (e.g. *Macrolides*, *Proton Pump Inhibitors*, *Non-steroidal Anti-inflammatory Drugs*) groups compounds by pharmacological mechanism. Products in the same drug class **are NOT medically interchangeable** without clinical evaluation.
      * **Equivalent Alternatives** in this study are strictly defined at the compound level: **Same Generic + Same Formulation + Same Strength**.
    """)

st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>1. Inspect Specific Therapeutic Drug Class</h3>", unsafe_allow_html=True)

# Selector for drug classes
all_classes = sorted(df_dc["drug_class_name"].dropna().unique().tolist())
selected_dc = st.selectbox(
    "Select Therapeutic Class:",
    options=all_classes,
    index=all_classes.index("Non-steroidal Anti-inflammatory Drugs (NSAIDs)") if "Non-steroidal Anti-inflammatory Drugs (NSAIDs)" in all_classes else 0
)

# Filter medicines in this drug class
dc_meds = df_med[df_med["drug_class_name"] == selected_dc]
priced_dc = dc_meds[dc_meds["price"].notna()]

# Metrics Row
dc_col1, dc_col2, dc_col3, dc_col4 = st.columns(4)

total_dc_brands = len(dc_meds)
unique_dc_generics = dc_meds["generic_name"].dropna().nunique()
unique_dc_mfrs = dc_meds["manufacturer_name"].dropna().nunique()
med_dc_price = priced_dc["price"].median() if not priced_dc.empty else 0.0
avg_dc_price = priced_dc["price"].mean() if not priced_dc.empty else 0.0
min_dc_price = priced_dc["price"].min() if not priced_dc.empty else 0.0
max_dc_price = priced_dc["price"].max() if not priced_dc.empty else 0.0

dc_col1.metric("Branded Products", f"{total_dc_brands:,}", f"{len(priced_dc):,} priced")
dc_col2.metric("Active Generics", f"{unique_dc_generics:,}", f"{unique_dc_mfrs} Manufacturers")
dc_col3.metric("Median Unit Price", f"{med_dc_price:.2f} BDT", f"Mean: {avg_dc_price:.2f} BDT")
dc_col4.metric("Price Extremes", f"{min_dc_price:.2f} - {max_dc_price:.2f} BDT", f"Range spread")

st.markdown("---")

# Visualizations for Selected Class
c_v1, c_v2 = st.columns(2)

custom_colorscale = [
    [0.0, COLOR_PURPLE_DARK],
    [0.4, COLOR_PLUM],
    [0.8, COLOR_PEACH],
    [1.0, COLOR_GOLD]
]

with c_v1:
    st.markdown(f"**Generics Count in {selected_dc}**")
    gen_counts = dc_meds["generic_name"].value_counts().head(10).reset_index()
    gen_counts.columns = ["generic_name", "product_count"]
    
    gen_title = f"Top 10 Active Compounds in {selected_dc}"
    fig_gen = px.bar(
        gen_counts,
        x="product_count",
        y="generic_name",
        orientation="h",
        labels={"product_count": "Branded Products", "generic_name": "Active Generic"},
        color="product_count",
        color_continuous_scale=custom_colorscale
    )
    fig_gen.update_layout(get_luxury_chart_layout(title=gen_title, height=380))
    fig_gen.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_gen, use_container_width=True, config=PLOTLY_CONFIG)

with c_v2:
    st.markdown(f"**Price Boxplot for Generics in {selected_dc}**")
    top_gen_names = gen_counts["generic_name"].head(6).tolist()
    sub_priced = priced_dc[priced_dc["generic_name"].isin(top_gen_names)]
    
    if not sub_priced.empty:
        box_title = "Price Distribution across Top Compounds"
        fig_box = px.box(
            sub_priced,
            x="generic_name",
            y="price",
            labels={"price": "Unit Price (BDT)", "generic_name": "Generic"},
            color="generic_name",
            color_discrete_sequence=PLOTLY_PALETTE
        )
        fig_box.update_layout(get_luxury_chart_layout(title=box_title, height=380))
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_box, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("No priced medicines available for box plot.")

st.markdown("---")

# Section 2: Most Crowded Alternative Groups Market-Wide
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>2. Market-Wide Most Competitive & Crowded Alternative Groups</h3>", unsafe_allow_html=True)
st.markdown("Alternative groups in Bangladesh with the highest brand density and price variations:")

sort_by = st.radio(
    "Sort Groups By:",
    options=["Most Crowded (Brand Count)", "Highest Price Spread (Max / Min Ratio)", "Highest Max Potential Savings %"],
    horizontal=True
)

sorted_groups = df_groups.copy()
if "Brand Count" in sort_by:
    sorted_groups = sorted_groups.sort_values(by="brands", ascending=False)
elif "Price Spread" in sort_by:
    sorted_groups = sorted_groups.sort_values(by="spread_x", ascending=False)
else:
    sorted_groups = sorted_groups.sort_values(by="max_saving_pct", ascending=False)

display_groups = sorted_groups.head(25).rename(columns={
    "generic_name": "Generic Compound",
    "dosage_form_name": "Dosage Form",
    "strength_normalized": "Strength",
    "brands": "Brand Count",
    "min_price": "Min Price (BDT)",
    "median_price": "Median Price (BDT)",
    "max_price": "Max Price (BDT)",
    "spread_x": "Price Spread (x)",
    "max_saving_pct": "Max Saving (%)"
})

st.dataframe(
    display_groups.style.format({
        "Min Price (BDT)": "{:.2f}",
        "Median Price (BDT)": "{:.2f}",
        "Max Price (BDT)": "{:.2f}",
        "Price Spread (x)": "{:.2f}x",
        "Max Saving (%)": "{:.1f}%"
    }),
    use_container_width=True,
    height=400
)
