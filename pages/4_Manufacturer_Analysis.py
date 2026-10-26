"""
Page 4: Manufacturer Benchmarking & Price Index Analysis.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: #522D60, #80426E, #F2A67B, #FFD38B
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.data_loader import (
    load_full_medicine_dataset,
    load_manufacturer_price_index
)
from utils.ui import (
    apply_luxury_styles,
    get_luxury_chart_layout,
    COLOR_PURPLE_DARK,
    COLOR_PLUM,
    COLOR_PEACH,
    COLOR_GOLD,
    PLOTLY_CONFIG
)

st.set_page_config(page_title="Manufacturer Analysis | Medicine Analytics", page_icon="🏭", layout="wide")

# Apply Luxury Theme
apply_luxury_styles()

st.title("🏭 Pharmaceutical Manufacturer Benchmarking")
st.markdown("Analysis of pharmaceutical companies in Bangladesh: portfolio size, pricing positioning (Price Index), and the share of products offering the lowest market price.")

@st.cache_data
def get_mfr_data():
    df_med = load_full_medicine_dataset()
    df_mfr = load_manufacturer_price_index()
    return df_med, df_mfr

df_med, df_mfr = get_mfr_data()

# Methodology Callout
with st.expander("ℹ️ What is the Manufacturer Price Index? (Methodology Explanation)", expanded=True):
    st.markdown(f"""
    * **Price Index Definition:** For each brand, `price_index = brand_price / median_price_of_equivalent_group`. 
    * **Aggregation:** A manufacturer's overall score is the **median price index** across all its comparable products (minimum 30 products).
    * **Interpretation:**
      * **Index < 1.0:** The manufacturer prices its products **below** the market median (<span class="badge-peach">Budget / Economical</span>).
      * **Index = 1.0:** The manufacturer aligns directly with typical market prices (<span class="badge-gold">Fair / Market Average</span>).
      * **Index > 1.0:** The manufacturer charges a **premium above** the market median (<span class="badge-purple">Premium Positioning</span>).
    * *Note:* The Price Index is a normalized dimensionless ratio, **not a monetary price in BDT**.
    """, unsafe_allow_html=True)

st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>1. Manufacturer Portfolio Deep Dive</h3>", unsafe_allow_html=True)

# Manufacturer Selector
all_mfr_names = sorted(df_med["manufacturer_name"].dropna().unique().tolist())
selected_mfr = st.selectbox(
    "Select Manufacturer to Inspect:",
    options=all_mfr_names,
    index=all_mfr_names.index("Square Pharmaceuticals Ltd.") if "Square Pharmaceuticals Ltd." in all_mfr_names else 0
)

# Filter products for selected manufacturer
mfr_products = df_med[df_med["manufacturer_name"] == selected_mfr]
priced_mfr = mfr_products[mfr_products["price"].notna()]

# Lookup in benchmark index
idx_match = df_mfr[df_mfr["manufacturer_name"] == selected_mfr]

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

total_prods = len(mfr_products)
priced_cnt = len(priced_mfr)
avg_p = priced_mfr["price"].mean() if not priced_mfr.empty else 0.0
med_p = priced_mfr["price"].median() if not priced_mfr.empty else 0.0
min_p = priced_mfr["price"].min() if not priced_mfr.empty else 0.0
max_p = priced_mfr["price"].max() if not priced_mfr.empty else 0.0

m_col1.metric("Total Catalog Brands", f"{total_prods:,}", f"{priced_cnt:,} priced")
m_col2.metric("Median Unit Price", f"{med_p:.2f} BDT", f"Range: {min_p:.2f} - {max_p:.2f} BDT")
m_col3.metric("Average Unit Price", f"{avg_p:.2f} BDT", help="Arithmetic average")

if not idx_match.empty:
    m_info = idx_match.iloc[0]
    p_idx = m_info["median_index"]
    pct_cheap = m_info["pct_cheapest"]
    cat = m_info["position_category"]
    
    m_col4.metric(
        "Price Index",
        f"{p_idx:.2f}",
        f"{cat.split()[0]}",
        delta_color="normal" if p_idx <= 1.0 else "inverse"
    )
    m_col5.metric(
        "% Cheapest Brands",
        f"{pct_cheap:.1f}%",
        f"{m_info['n']} compared brands",
        help="Percentage of this manufacturer's products that are the cheapest available brand in their group"
    )
else:
    m_col4.metric("Price Index", "N/A", "Less than 30 comparable products")
    m_col5.metric("% Cheapest Brands", "N/A", "Excluded from benchmark")

st.markdown("---")

# Visualizations Row: Top Budget vs Top Premium
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>2. Market Price Index Comparison (107 Benchmarked Manufacturers)</h3>", unsafe_allow_html=True)

tab_chart1, tab_chart2 = st.tabs(["📊 Price Index (Budget vs. Premium)", "🎯 Portfolio Size vs. Price Index Scatter"])

with tab_chart1:
    top_n = st.slider("Number of extreme manufacturers to display per tier:", min_value=5, max_value=20, value=10)
    
    budget_mfrs = df_mfr.head(top_n).copy()
    budget_mfrs["tier"] = "Economical / Budget Tier (Index < 1.0)"
    
    premium_mfrs = df_mfr.tail(top_n).copy().iloc[::-1]
    premium_mfrs["tier"] = "Premium / Dearest Tier (Index > 1.0)"
    
    combined_tiers = pd.concat([budget_mfrs, premium_mfrs])
    
    chart_title_1 = f"Top {top_n} Most Economical vs. Top {top_n} Most Expensive Manufacturers"
    fig_index = px.bar(
        combined_tiers,
        x="median_index",
        y="manufacturer_name",
        color="tier",
        orientation="h",
        labels={"median_index": "Median Price Index (1.0 = Market Median)", "manufacturer_name": "Company"},
        color_discrete_map={
            "Economical / Budget Tier (Index < 1.0)": COLOR_PEACH,
            "Premium / Dearest Tier (Index > 1.0)": COLOR_PURPLE_DARK
        }
    )
    fig_index.add_vline(x=1.0, line_dash="dash", line_color=COLOR_GOLD, annotation_text="Market Median (1.0)")
    fig_index.update_layout(get_luxury_chart_layout(title=chart_title_1, height=520))
    fig_index.update_layout(yaxis=dict(categoryorder="array", categoryarray=combined_tiers["manufacturer_name"].tolist()[::-1]))
    st.plotly_chart(fig_index, use_container_width=True, config=PLOTLY_CONFIG)

with tab_chart2:
    chart_title_2 = "Manufacturer Portfolio Size (n) vs. Median Price Index"
    fig_scatter = px.scatter(
        df_mfr,
        x="n",
        y="median_index",
        size="pct_cheapest",
        color="position_category",
        hover_name="manufacturer_name",
        labels={
            "n": "Number of Comparable Products (Sample Size)",
            "median_index": "Median Price Index",
            "pct_cheapest": "% Cheapest Brands",
            "position_category": "Positioning"
        },
        color_discrete_map={
            "Budget / Economical": COLOR_PEACH,
            "Fair / Market Average": COLOR_PLUM,
            "Premium / Expensive": COLOR_PURPLE_DARK
        }
    )
    fig_scatter.add_hline(y=1.0, line_dash="dash", line_color=COLOR_GOLD)
    fig_scatter.update_layout(get_luxury_chart_layout(title=chart_title_2, height=480))
    st.plotly_chart(fig_scatter, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# Sortable Full Table
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>3. Comprehensive Manufacturer Ranking Table</h3>", unsafe_allow_html=True)

search_term = st.text_input("Filter table by company name:", placeholder="e.g. Square, Beximco, Delta, Incepta...")
filtered_tbl = df_mfr.copy()
if search_term.strip():
    filtered_tbl = filtered_tbl[filtered_tbl["manufacturer_name"].str.contains(search_term.strip(), case=False)]

display_table = filtered_tbl.rename(columns={
    "manufacturer_name": "Manufacturer Name",
    "n": "Evaluated Products",
    "median_index": "Median Price Index",
    "pct_cheapest": "% Cheapest Brands",
    "position_category": "Market Positioning"
})

st.dataframe(
    display_table.style.format({
        "Median Price Index": "{:.2f}",
        "% Cheapest Brands": "{:.1f}%"
    }),
    use_container_width=True,
    height=400
)
