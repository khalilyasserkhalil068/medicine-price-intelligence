"""
Page 2: Medicine Search & Alternative Brand Exploration.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: #522D60, #80426E, #F2A67B, #FFD38B
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.data_loader import (
    load_full_medicine_dataset,
    load_alternatives_per_medicine
)
from utils.analysis import search_medicines, get_alternatives_for_brand
from utils.ui import (
    apply_luxury_styles,
    get_luxury_chart_layout,
    COLOR_PURPLE_DARK,
    COLOR_PLUM,
    COLOR_PEACH,
    COLOR_GOLD,
    PLOTLY_CONFIG,
    is_dark_mode,
    html_block
)

st.set_page_config(page_title="Medicine Alternatives | Medicine Analytics", page_icon="🔍", layout="wide")

# Apply Luxury Theme
apply_luxury_styles()

st.title("🔍 Medicine Search & Alternative Brand Matcher")
st.markdown("Search any branded pharmaceutical product in Bangladesh to inspect all clinically-equivalent alternatives sharing the exact **Active Generic + Dosage Form + Strength**.")

# Caching datasets
@st.cache_data
def get_search_data():
    df_med = load_full_medicine_dataset()
    df_comp = load_alternatives_per_medicine()
    return df_med, df_comp

df_med, df_comp = get_search_data()

# Search Box & Autocomplete
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>1. Select or Search Medicine</h3>", unsafe_allow_html=True)

col_search, col_preset = st.columns([2, 1])

with col_search:
    search_query = st.text_input(
        "Type Brand Name or Active Generic:",
        placeholder="e.g. Napa, Seclo, Ciprofloxacin, Aceclofenac, Azithromycin...",
        help="Search matches both brand trade names and active compound generic names."
    )

with col_preset:
    preset_choice = st.selectbox(
        "Or pick a popular showcase medicine:",
        options=["-- Select a popular medicine --", "Napa (Paracetamol 500mg)", "Seclo (Omeprazole 20mg)", "Flexi (Aceclofenac 100mg)", "Zithrin (Azithromycin 500mg)", "A-Card (Amlodipine 5mg)"]
    )

# Determine query
effective_query = search_query.strip()
if preset_choice != "-- Select a popular medicine --" and not search_query.strip():
    if "Napa" in preset_choice: effective_query = "Napa"
    elif "Seclo" in preset_choice: effective_query = "Seclo"
    elif "Flexi" in preset_choice: effective_query = "Flexi"
    elif "Zithrin" in preset_choice: effective_query = "Zithrin"
    elif "A-Card" in preset_choice: effective_query = "A-Card"

if not effective_query:
    effective_query = "Napa" # Default initial showcase

# Fetch search results
search_results = search_medicines(df_med, effective_query, limit=50)

if search_results.empty:
    st.warning(f"No medicines matched '{effective_query}'. Try another search query.")
    st.stop()

# Format selectbox options
medicine_options = {}
for _, row in search_results.iterrows():
    b_id = row["brand_id"]
    price_str = f"{row['price']:.2f} BDT" if pd.notna(row["price"]) else "Unpriced"
    label = f"{row['brand_name']} | {row['generic_name']} ({row['dosage_form_name']} - {row['strength_normalized']}) | {price_str} [{row['manufacturer_name']}]"
    medicine_options[b_id] = label

selected_brand_id = st.selectbox(
    "Choose specific medicine product to analyze:",
    options=list(medicine_options.keys()),
    format_func=lambda x: medicine_options[x]
)

# Fetch alternatives using exact project matching rules
alt_results = get_alternatives_for_brand(df_comp, df_med, selected_brand_id)

if not alt_results.get("found"):
    st.error("Selected medicine could not be retrieved from the database.")
    st.stop()

target = alt_results["target"]

st.markdown("---")
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>2. Selected Medicine Overview</h3>", unsafe_allow_html=True)

# Target Medicine Card in Luxury Style
# html_block() is required here: the conditional badge below becomes a blank
# line when the medicine is NOT the cheapest, which used to close the markdown
# HTML block and turn the rest of this card into a raw code block.
st.markdown(html_block(f"""
<div class="luxury-card highlight-card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
            <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
                <h2 style="margin: 0; font-size: 1.85rem;">{target['brand_name']}</h2>
                <span class="badge-purple">{target.get('type', 'allopathic')}</span>
                {f'<span class="badge-gold">🥇 Cheapest in Category</span>' if (alt_results.get('grp_min') and target.get('price') == alt_results['grp_min']) else ''}
            </div>
            <p style="margin: 0.3rem 0 0 0; font-size: 1.05rem; font-weight: 600;">
                {target['generic_name']} • {target['dosage_form_name']} • {target['strength_normalized']}
            </p>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.88rem;">
                Manufacturer: <strong>{target['manufacturer_name']}</strong> | Therapeutic: <strong>{target['drug_class_name']}</strong>
            </p>
        </div>
        <div style="background: linear-gradient(135deg, #3D1C49 0%, {COLOR_PURPLE_DARK} 100%); padding: 0.8rem 1.4rem; border-radius: 0.85rem; text-align: center; border: 1px solid rgba(255,211,139,0.3); box-shadow: 0 4px 14px rgba(82,45,96,0.25);">
            <span style="font-size: 0.72rem; color: {COLOR_GOLD}; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; display: block;">Unit Price</span>
            <span style="font-size: 1.8rem; font-weight: 900; color: #FFFFFF;">
                {f"{target['price']:.2f} BDT" if pd.notna(target.get('price')) else "Unpriced"}
            </span>
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)

# Secondary specs
c_info1, c_info2, c_info3 = st.columns(3)
with c_info1:
    pack_desc = target.get("package_description") or "Not recorded"
    st.info(f"📦 **Packaging Container:** {pack_desc}")
with c_info2:
    if alt_results.get("has_group") and alt_results.get("grp_min") is not None:
        g_min = alt_results["grp_min"]
        g_max = alt_results["grp_max"]
        g_med = alt_results["grp_median"]
        st.info(f"📊 **Group Range:** {g_min:.2f} - {g_max:.2f} BDT (Median: {g_med:.2f} BDT)")
    else:
        st.info("📊 **Group Range:** Single product or unpriced group")
with c_info3:
    tot_alts = alt_results.get("total_brands_in_group", 1) - 1
    st.info(f"🎯 **Available Alternatives:** {max(0, tot_alts)} competing brands")

st.markdown("---")

# Alternatives Table Section
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>3. Equivalent Alternative Brands</h3>", unsafe_allow_html=True)

if not alt_results.get("has_group"):
    st.info(f"ℹ️ {alt_results.get('message', 'No equivalent alternatives found.')}")
    st.stop()

alts_df = alt_results["alternatives"].copy()

if alts_df.empty or len(alts_df) <= 1:
    st.info("ℹ️ No other competing brands exist in the dataset sharing this exact generic, dosage form, and normalized strength.")
    st.stop()

# Filters for the alternatives table
with st.expander("Filter & Refine Alternatives", expanded=False):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        all_mfrs = sorted(alts_df["manufacturer_name"].dropna().unique().tolist())
        selected_mfrs = st.multiselect("Filter by Manufacturer(s):", options=all_mfrs, default=[])
    with f_col2:
        priced_only = st.checkbox("Show priced alternatives only", value=True)

# Apply filters
filtered_alts = alts_df.copy()
if selected_mfrs:
    filtered_alts = filtered_alts[filtered_alts["manufacturer_name"].isin(selected_mfrs)]
if priced_only:
    filtered_alts = filtered_alts[filtered_alts["price"].notna()]

st.markdown(f"Displaying **{len(filtered_alts)}** equivalent brands (sorted lowest to highest price):")

# Format columns for display
display_cols = ["brand_name", "manufacturer_name", "price", "price_diff", "saving_amount", "saving_pct", "package_description"]
table_df = filtered_alts[display_cols].copy()

table_df.columns = [
    "Brand Name",
    "Manufacturer",
    "Unit Price (BDT)",
    "Difference (BDT)",
    "Savings (BDT)",
    "Savings (%)",
    "Packaging Description"
]

# Highlight current brand and cheapest brand with palette colors
def highlight_luxury_rows(row):
    # The highlight colours must follow the active theme: a pale background in
    # Dark mode would put light text on a light cell and make the row unreadable.
    _dark = is_dark_mode()
    _curr = ("background-color: #4A3320; color: #FFE3B8; font-weight: bold; "
             "border-left: 3px solid #F2A67B;") if _dark else \
            ("background-color: #FFF2DF; font-weight: bold; "
             "border-left: 3px solid #F2A67B;")
    _cheap = ("background-color: #3A2440; color: #F3D9EE; font-weight: bold; "
              "border-left: 3px solid #A3588E;") if _dark else \
             ("background-color: #F8EBF4; font-weight: bold; "
              "border-left: 3px solid #80426E;")
    is_curr = row["Brand Name"] == target["brand_name"]
    is_cheapest = row["Unit Price (BDT)"] == alt_results["grp_min"]
    if is_curr:
        return [_curr] * len(row)
    elif is_cheapest:
        return [_cheap] * len(row)
    return [""] * len(row)

st.dataframe(
    table_df.style.apply(highlight_luxury_rows, axis=1).format({
        "Unit Price (BDT)": "{:.2f}",
        "Difference (BDT)": "{:+.2f}",
        "Savings (BDT)": "{:.2f}",
        "Savings (%)": "{:.1f}%"
    }, na_rep="--"),
    use_container_width=True,
    height=400
)

# Alternative Price Distribution Chart
if not filtered_alts[filtered_alts["price"].notna()].empty:
    st.markdown(f"<h4 style='color: {COLOR_PLUM}; margin-top: 1rem;'>✦ Alternative Price Comparison Chart</h4>", unsafe_allow_html=True)
    chart_df = filtered_alts[filtered_alts["price"].notna()].sort_values("price", ascending=True).head(25)
    chart_df["color_tag"] = np.where(
        chart_df["brand_id"] == selected_brand_id, "Selected Brand",
        np.where(chart_df["price"] == alt_results["grp_min"], "Cheapest Alternative", "Other Equivalent Brands")
    )
    
    chart_title_alt = f"Price Comparison: {target['generic_name']} {target['dosage_form_name']} {target['strength_normalized']} (Top 25 Brands)"
    fig_alt = px.bar(
        chart_df,
        x="brand_name",
        y="price",
        color="color_tag",
        color_discrete_map={
            "Selected Brand": COLOR_GOLD,
            "Cheapest Alternative": COLOR_PEACH,
            "Other Equivalent Brands": COLOR_PURPLE_DARK
        },
        labels={"price": "Unit Price (BDT)", "brand_name": "Brand Name", "color_tag": "Product Status"}
    )
    fig_alt.update_layout(get_luxury_chart_layout(title=chart_title_alt, height=400))
    fig_alt.update_layout(xaxis_tickangle=-40)
    st.plotly_chart(fig_alt, use_container_width=True, config=PLOTLY_CONFIG)

st.caption("⚠️ **Methodological Note:** Alternatives in this dashboard reflect identical generic chemical entity, dosage form, and strength as stated on manufacturer packaging. This does not represent an individualized pharmacist substitution recommendation.")
