"""
Page 1: Overview & Macro Market Intelligence.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: #522D60, #80426E, #F2A67B, #FFD38B
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils.data_loader import (
    load_full_medicine_dataset,
    load_alternatives_per_medicine,
    load_alternatives_per_group,
    load_drug_classes_summary
)
from utils.analysis import calculate_overview_kpis
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

st.set_page_config(page_title="Market Overview | Medicine Analytics", page_icon="📊", layout="wide")

# Apply Luxury Theme
apply_luxury_styles()

st.title("📊 Macro Market Overview & Key Performance Indicators")
st.markdown("Macro-level analysis of pharmaceutical offerings, pricing dispersion, and savings potential across Bangladesh's medicine dataset.")

# Load Data
@st.cache_data
def get_overview_data():
    df_med = load_full_medicine_dataset()
    df_comp = load_alternatives_per_medicine()
    df_groups = load_alternatives_per_group()
    df_dc = load_drug_classes_summary()
    kpis = calculate_overview_kpis(df_med, df_comp, df_groups)
    return df_med, df_comp, df_groups, df_dc, kpis

df_med, df_comp, df_groups, df_dc, kpis = get_overview_data()

# Dynamic KPI Cards
st.markdown(f"<h4 style='color: {COLOR_PLUM}; margin-top: 1rem;'>✦ Key Market Metrics</h4>", unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric(
    label="Total Products",
    value=f"{kpis['total_medicines']:,}",
    help="Total branded pharmaceutical products recorded in the dataset."
)
kpi2.metric(
    label="Priced Coverage",
    value=f"{kpis['price_coverage_pct']}%",
    delta=f"{kpis['priced_medicines']:,} priced",
    help="Percentage of medicines with validated, unambiguous numerical price data."
)
kpi3.metric(
    label="Manufacturers",
    value=f"{kpis['unique_manufacturers']:,}",
    help="Total active pharmaceutical manufacturing companies."
)
kpi4.metric(
    label="Therapeutic Classes",
    value=f"{kpis['unique_drug_classes']:,}",
    help="Total canonical medical therapeutic drug classes."
)
kpi5.metric(
    label="Alternative Groups",
    value=f"{kpis['total_groups']:,}",
    delta=f"{kpis['total_comparable']:,} brands",
    help="Groups with identical generic + dosage form + strength having >=2 priced brands."
)

st.markdown("<br>", unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)

s1.metric(
    label="Median Medicine Price",
    value=f"{kpis['median_price']:.2f} BDT",
    help="Median unit price across all priced medicines (robust to high-price oncology outliers)."
)
s2.metric(
    label="Mean Medicine Price",
    value=f"{kpis['mean_price']:.2f} BDT",
    help="Arithmetic mean pulled up by high-cost biologics and cancer treatments."
)
s3.metric(
    label="Median Potential Savings",
    value=f"{kpis['median_saving_pct']}%",
    delta=f"Mean: {kpis['mean_saving_pct']}%",
    help="Median savings achieved by switching to the lowest-priced equivalent brand."
)
s4.metric(
    label="Non-Cheapest Share",
    value=f"{kpis['non_cheapest_share']}%",
    delta=f"{kpis['non_cheapest_count']:,} brands",
    delta_color="inverse",
    help="Percentage of comparable medicines priced strictly higher than the group minimum."
)

st.markdown("---")

# Visualizations Row 1: Price Distribution & Manufacturer Volume
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>📉 Price Distribution & Portfolio Concentration</h3>", unsafe_allow_html=True)

col_ctrl, _ = st.columns([3, 2])
with col_ctrl:
    scale_type = st.radio(
        "Price Distribution Scale Mode:",
        options=["Logarithmic (Recommended)", "Linear (0 - 500 BDT)"],
        horizontal=True
    )

col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    priced_df = df_med[df_med["price"].notna()].copy()
    
    if "Logarithmic" in scale_type:
        priced_df["log_price"] = np.log10(priced_df["price"].clip(lower=0.1))
        fig_price = px.histogram(
            priced_df,
            x="price",
            nbins=60,
            log_x=True,
            labels={"price": "Unit Price (BDT, Log Scale)"},
            color_discrete_sequence=[COLOR_PURPLE_DARK]
        )
        fig_price.add_vline(x=kpis["median_price"], line_dash="dash", line_color=COLOR_GOLD,
                            annotation_text=f"Median: {kpis['median_price']} BDT", annotation_position="top left")
        chart_title_p = "Distribution of Unit Prices (Log Scale)"
    else:
        clipped_df = priced_df[priced_df["price"] <= 500]
        fig_price = px.histogram(
            clipped_df,
            x="price",
            nbins=50,
            labels={"price": "Unit Price (BDT)"},
            color_discrete_sequence=[COLOR_PURPLE_DARK]
        )
        fig_price.add_vline(x=kpis["median_price"], line_dash="dash", line_color=COLOR_GOLD,
                            annotation_text=f"Median: {kpis['median_price']} BDT")
        chart_title_p = "Distribution of Unit Prices (<= 500 BDT)"
        
    fig_price.update_layout(get_luxury_chart_layout(title=chart_title_p, height=415))
    fig_price.update_layout(bargap=0.08)
    st.plotly_chart(fig_price, use_container_width=True, config=PLOTLY_CONFIG)

with col_chart2:
    top_mfr = df_med["manufacturer_name"].value_counts().head(15).reset_index()
    top_mfr.columns = ["manufacturer_name", "product_count"]
    
    custom_colorscale = [
        [0.0, COLOR_PURPLE_DARK],
        [0.4, COLOR_PLUM],
        [0.8, COLOR_PEACH],
        [1.0, COLOR_GOLD]
    ]
    
    fig_mfr = px.bar(
        top_mfr,
        x="product_count",
        y="manufacturer_name",
        orientation="h",
        labels={"product_count": "Total Branded Products", "manufacturer_name": "Manufacturer"},
        color="product_count",
        color_continuous_scale=custom_colorscale
    )
    fig_mfr.update_layout(get_luxury_chart_layout(title="Top 15 Manufacturers by Product Portfolio", height=415))
    fig_mfr.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_mfr, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# Visualizations Row 2: Therapeutic Groups & Price Dispersion
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>🧬 Therapeutic Groups & Price Dispersion</h3>", unsafe_allow_html=True)
col_chart3, col_chart4 = st.columns([1, 1])

with col_chart3:
    top_dc = df_dc.head(12)
    fig_dc = px.bar(
        top_dc,
        x="drug_class_name",
        y="total_products",
        labels={"total_products": "Branded Products", "drug_class_name": "Therapeutic Class"},
        color="avg_price",
        color_continuous_scale=custom_colorscale
    )
    fig_dc.update_layout(get_luxury_chart_layout(title="Top 12 Therapeutic Drug Classes by Brand Count", height=420))
    fig_dc.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_dc, use_container_width=True, config=PLOTLY_CONFIG)

with col_chart4:
    top_10_classes = top_dc["drug_class_name"].head(8).tolist()
    box_data = df_med[df_med["drug_class_name"].isin(top_10_classes) & df_med["price"].notna() & (df_med["price"] <= 150)]
    
    fig_box = px.box(
        box_data,
        x="drug_class_name",
        y="price",
        labels={"price": "Unit Price (BDT)", "drug_class_name": "Therapeutic Group"},
        color="drug_class_name",
        color_discrete_sequence=PLOTLY_PALETTE
    )
    fig_box.update_layout(get_luxury_chart_layout(title="Price Spreads in Top Therapeutic Groups (<= 150 BDT)", height=420))
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-35)
    st.plotly_chart(fig_box, use_container_width=True, config=PLOTLY_CONFIG)
