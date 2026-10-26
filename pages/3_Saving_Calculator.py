"""
Page 3: Prescription Savings Calculator.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: #522D60, #80426E, #F2A67B, #FFD38B
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.data_loader import (
    load_full_medicine_dataset,
    load_alternatives_per_medicine
)
from utils.analysis import search_medicines, get_alternatives_for_brand
from utils.data_validation import calculate_savings_safely, validate_quantity_value
from utils.ui import (
    apply_luxury_styles,
    get_luxury_chart_layout,
    COLOR_PURPLE_DARK,
    COLOR_PLUM,
    COLOR_PEACH,
    COLOR_GOLD,
    PLOTLY_CONFIG
)

st.set_page_config(page_title="Savings Calculator | Medicine Analytics", page_icon="💰", layout="wide")

# Apply Luxury Theme
apply_luxury_styles()

st.title("💰 Prescription Savings Calculator")
st.markdown("Calculate personalized prescription savings by comparing your current medicine against equivalent alternative brands in Bangladesh.")

@st.cache_data
def get_calc_data():
    df_med = load_full_medicine_dataset()
    df_comp = load_alternatives_per_medicine()
    return df_med, df_comp

df_med, df_comp = get_calc_data()

# Mode Selection
calc_mode = st.radio(
    "Calculation Input Mode:",
    options=["Select from Real Medicine Database (Recommended)", "Manual Custom Price Input"],
    horizontal=True
)

st.markdown("---")

if "Database" in calc_mode:
    # 1. Search Medicine
    st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>1. Select Current Prescribed Medicine</h3>", unsafe_allow_html=True)
    col_q, col_p = st.columns([2, 1])
    with col_q:
        q = st.text_input("Search Current Medicine Brand:", placeholder="e.g. Napa, Flexi, Seclo, Cipro, Azithromycin...")
    with col_p:
        preset = st.selectbox(
            "Or pick showcase medicine:",
            options=["-- Select a popular medicine --", "Napa (Paracetamol 500mg)", "Seclo (Omeprazole 20mg)", "Flexi (Aceclofenac 100mg)", "Zithrin (Azithromycin 500mg)", "A-Card (Amlodipine 5mg)"]
        )
    
    effective_q = q.strip()
    if preset != "-- Select a popular medicine --" and not q.strip():
        if "Napa" in preset: effective_q = "Napa"
        elif "Seclo" in preset: effective_q = "Seclo"
        elif "Flexi" in preset: effective_q = "Flexi"
        elif "Zithrin" in preset: effective_q = "Zithrin"
        elif "A-Card" in preset: effective_q = "A-Card"

    if not effective_q:
        effective_q = "Napa"
        
    matched = search_medicines(df_med, effective_q, limit=30)
    
    if matched.empty:
        st.warning(f"No medicines found for '{effective_q}'. Try another keyword.")
        st.stop()
        
    med_choices = {}
    for _, r in matched.iterrows():
        p_str = f"{r['price']:.2f} BDT" if pd.notna(r["price"]) else "Unpriced"
        med_choices[r["brand_id"]] = f"{r['brand_name']} | {r['generic_name']} ({r['dosage_form_name']} - {r['strength_normalized']}) | {p_str}"
        
    selected_orig_id = st.selectbox(
        "Current Medicine Brand:",
        options=list(med_choices.keys()),
        format_func=lambda x: med_choices[x]
    )
    
    # Fetch alternatives
    alt_data = get_alternatives_for_brand(df_comp, df_med, selected_orig_id)
    orig_target = alt_data["target"]
    orig_price = orig_target.get("price")
    
    # 2. Select Alternative
    st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>2. Select Alternative Brand to Compare</h3>", unsafe_allow_html=True)
    
    if not alt_data.get("has_group") or alt_data["alternatives"].empty:
        st.warning("⚠️ This medicine does not have equivalent alternative brands with valid pricing in the dataset.")
        st.stop()
        
    alts_priced = alt_data["alternatives"][alt_data["alternatives"]["price"].notna()].copy()
    if alts_priced.empty:
        st.warning("⚠️ All alternatives in this group lack numerical pricing data.")
        st.stop()
        
    alt_options = {}
    cheapest_id = alts_priced.iloc[0]["brand_id"]
    for _, r in alts_priced.iterrows():
        is_cheap_tag = " [Cheapest 🥇]" if r["brand_id"] == cheapest_id else ""
        is_curr_tag = " [Current 📍]" if r["brand_id"] == selected_orig_id else ""
        alt_options[r["brand_id"]] = f"{r['brand_name']} ({r['manufacturer_name']}) - {r['price']:.2f} BDT{is_cheap_tag}{is_curr_tag}"
        
    selected_alt_id = st.selectbox(
        "Select Alternative Brand (Defaults to Cheapest):",
        options=list(alt_options.keys()),
        index=0,
        format_func=lambda x: alt_options[x]
    )
    
    selected_alt_row = alts_priced[alts_priced["brand_id"] == selected_alt_id].iloc[0]
    alt_price = selected_alt_row["price"]
    
    orig_name = f"{orig_target['brand_name']} ({orig_target['manufacturer_name']})"
    alt_name = f"{selected_alt_row['brand_name']} ({selected_alt_row['manufacturer_name']})"

else:
    # Manual Price Input Mode
    st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>Manual Price Entry Mode</h3>", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        orig_name = st.text_input("Current Medicine Label:", value="Original Brand X")
        orig_price = st.number_input("Current Unit Price (BDT):", min_value=0.0, value=15.0, step=0.5)
    with m_col2:
        alt_name = st.text_input("Alternative Medicine Label:", value="Alternative Brand Y")
        alt_price = st.number_input("Alternative Unit Price (BDT):", min_value=0.0, value=9.5, step=0.5)

st.markdown("---")

# Quantity Input with Session State
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>3. Prescription Quantity & Duration</h3>", unsafe_allow_html=True)

if "calc_qty_val" not in st.session_state:
    st.session_state.calc_qty_val = 30

def update_qty(v: int):
    st.session_state.calc_qty_val = v

col_qty, col_preset_qty = st.columns([1, 1])

with col_qty:
    quantity_input = st.number_input(
        "Enter Quantity (units / tablets / containers):",
        min_value=1,
        max_value=5000,
        step=1,
        key="calc_qty_val",
        help="Typical full monthly course is 30 units (1 daily), 60 units (2 daily), or 90 units (3 daily)."
    )

with col_preset_qty:
    st.write("Quick Duration Presets:")
    q_b1, q_b2, q_b3, q_b4 = st.columns(4)
    q_b1.button("1 Unit", use_container_width=True, on_click=update_qty, args=(1,))
    q_b2.button("1 Month (30)", use_container_width=True, on_click=update_qty, args=(30,))
    q_b3.button("2 Months (60)", use_container_width=True, on_click=update_qty, args=(60,))
    q_b4.button("3 Months (90)", use_container_width=True, on_click=update_qty, args=(90,))

# Calculate Savings Safely
calc_result = calculate_savings_safely(orig_price, alt_price, quantity_input)

st.markdown("---")
st.markdown(f"<h3 style='color: {COLOR_PURPLE_DARK};'>4. Financial Comparison Results</h3>", unsafe_allow_html=True)

if calc_result["status"] == "error":
    st.error(f"❌ Calculation Error: {calc_result['message']}")
elif calc_result["status"] == "costs_more":
    st.warning("⚠️ **Notice:** The selected alternative is MORE EXPENSIVE than your current medicine.")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Current Total Cost", f"{calc_result['original_total']:.2f} BDT", f"Unit: {orig_price:.2f} BDT")
    r_col2.metric("Alternative Total Cost", f"{calc_result['alternative_total']:.2f} BDT", f"Unit: {alt_price:.2f} BDT")
    r_col3.metric(
        "Additional Out-of-Pocket Cost",
        f"+{calc_result['additional_total_cost']:.2f} BDT",
        f"+{calc_result['additional_cost_pct']}% more expensive",
        delta_color="inverse"
    )
elif calc_result["status"] == "same_price":
    st.info("⚖️ Both brands have the identical unit price. Switching yields no net savings.")
else:
    # Substantial or standard savings in Luxury Box
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #3D1C49 0%, {COLOR_PURPLE_DARK} 45%, {COLOR_PLUM} 100%); padding: 1.8rem 2.2rem; border-radius: 1.25rem; color: white; border: 1px solid rgba(255,211,139,0.3); box-shadow: 0 10px 28px -6px rgba(82,45,96,0.3); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge-gold">👑 Net Prescription Savings</span>
                <div style="display: flex; align-items: baseline; gap: 0.8rem; margin-top: 0.5rem;">
                    <span style="font-size: 2.8rem; font-weight: 900; color: {COLOR_GOLD}; letter-spacing: -0.02em;">
                        {calc_result['total_saving']:.2f} BDT
                    </span>
                    <span style="font-size: 1.1rem; color: #F8EBF4; font-weight: 600;">
                        saved for {quantity_input} units
                    </span>
                </div>
                <p style="margin: 0.2rem 0 0 0; color: #E8D3E4; font-size: 0.92rem;">
                    Switching from <strong>{orig_name}</strong> to <strong>{alt_name}</strong>
                </p>
            </div>
            <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,211,139,0.35); padding: 1rem 1.6rem; border-radius: 1rem; text-align: center;">
                <span style="font-size: 0.75rem; text-transform: uppercase; color: {COLOR_GOLD}; font-weight: 700; letter-spacing: 0.08em; display: block;">Savings Ratio</span>
                <span style="font-size: 2.4rem; font-weight: 900; color: #FFFFFF;">
                    {calc_result['saving_pct']}%
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    r_col1, r_col2 = st.columns(2)
    r_col1.metric("Current Total Cost (Original)", f"{calc_result['original_total']:.2f} BDT", f"Unit: {orig_price:.2f} BDT")
    r_col2.metric("Alternative Total Cost", f"{calc_result['alternative_total']:.2f} BDT", f"Unit: {alt_price:.2f} BDT")
    
    # Plotly Visual Breakdown with Luxury Colors
    fig_calc = go.Figure()
    
    fig_calc.add_trace(go.Bar(
        name="Cost Paid with Alternative",
        x=["Prescription Total"],
        y=[calc_result["alternative_total"]],
        marker_color=COLOR_PLUM,
        text=[f"{calc_result['alternative_total']:.2f} BDT"],
        textposition="auto"
    ))
    
    fig_calc.add_trace(go.Bar(
        name="Net Money Saved",
        x=["Prescription Total"],
        y=[calc_result["total_saving"]],
        marker_color=COLOR_PEACH,
        text=[f"Saved: {calc_result['total_saving']:.2f} BDT"],
        textposition="auto"
    ))
    
    layout = get_luxury_chart_layout(f"Prescription Cost Breakdown ({quantity_input} units)", height=320)
    fig_calc.update_layout(layout)
    fig_calc.update_layout(barmode="stack", yaxis_title="Total Amount (BDT)")
    
    st.plotly_chart(fig_calc, use_container_width=True, config=PLOTLY_CONFIG)

st.caption("ℹ️ **Calculation Methodology:** Savings = (Original Price - Alternative Price) × Quantity. In cases where the alternative costs more, additional cost is reported instead of false negative savings.")
