"""
Main Entry Point for Medicine Price Analysis Streamlit Dashboard.
Assorted Medicine Dataset of Bangladesh 💊
Luxury Theme: Royal Velvet Purple (#522D60), Plum Wine (#80426E), Sunset Peach (#F2A67B), Golden Sand (#FFD38B)
"""

import streamlit as st
from pathlib import Path
from utils.data_loader import (
    load_full_medicine_dataset,
    load_alternatives_per_medicine,
    load_alternatives_per_group
)
from utils.analysis import calculate_overview_kpis
from utils.ui import apply_luxury_styles, COLOR_PURPLE_DARK, COLOR_PLUM, COLOR_PEACH, COLOR_GOLD

# Page Configuration
st.set_page_config(
    page_title="Medicine Price & Alternatives Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Royal Velvet Luxury Styling
apply_luxury_styles()

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <span class="sidebar-hero-emoji" style="filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">💊</span>
        <h2 style="margin: 0; color: {COLOR_GOLD} !important; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.01em;">MEDICINE ANALYTICS</h2>
        <span style="font-size: 0.75rem; letter-spacing: 0.1em; color: {COLOR_PEACH} !important; text-transform: uppercase; font-weight: 700;">Bangladesh Intelligence</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    # NOTE: previously this was <br>-separated lines containing inline <code>
    # chips. The chips were taller than the line box, so every row overlapped
    # the next one and the last chip was clipped by the sidebar edge. Each row
    # is now a flex line (see .status-row in utils/ui.py).
    st.markdown(
        f"""
    <div style="font-size: 0.85rem; margin-bottom: 0.35rem;">
        <span style="color: {COLOR_GOLD}; font-weight: 700;">Data Pipeline Status</span>
    </div>
    <div class="status-list">
        <div class="status-row"><span class="status-label">✓ Data Profiling</span><span class="status-chip">Verified</span></div>
        <div class="status-row"><span class="status-label">✓ Cleaning &amp; Regex</span><span class="status-chip">93.8%</span></div>
        <div class="status-row"><span class="status-label">✓ Relational Modeling</span><span class="status-chip">100%</span></div>
        <div class="status-row"><span class="status-label">✓ EDA &amp; Price Analysis</span><span class="status-chip">Complete</span></div>
        <div class="status-row"><span class="status-label">✓ Live Dashboard</span><span class="status-chip">Active</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(f"""
    <div style="background: rgba(255,211,139,0.1); border: 1px solid rgba(255,211,139,0.25); border-radius: 0.75rem; padding: 0.8rem; font-size: 0.8rem; color: #F5E8F3;">
        ✨ <strong>Executive Deliverables:</strong><br>
        <div style="margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.35rem;">
            <a href="http://localhost:5000/portal" target="_blank" style="color: {COLOR_PEACH}; text-decoration: none; font-weight: 700;">🌐 Executive Portal (Web)</a>
            <a href="http://localhost:5000" target="_blank" style="color: {COLOR_GOLD}; text-decoration: none; font-weight: 600;">⚡ Flask Fast Dashboard</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    report_pdf_path = Path("reports/Assorted_Medicine_Bangladesh_Final_Project_Report.pdf")
    if report_pdf_path.exists():
        with open(report_pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Download Executive PDF (8 Pages)",
                data=pdf_file.read(),
                file_name="Medicine_Price_Intelligence_Executive_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# Hero Header
st.markdown(f"""
<div style="margin-bottom: 1rem;">
    <div class="hero-eyebrow">
        ✦ Executive Healthcare Data Science Platform
    </div>
    <h1 style="font-size: 2.2rem; font-weight: 900; margin: 0; line-height: 1.25;">
        Medicine Price &amp; Alternatives Intelligence
    </h1>
    <p style="font-size: 1.05rem; margin-top: 0.5rem; max-width: 900px; line-height: 1.6;">
        A high-performance analytics platform exploring medicine pricing, patient savings opportunities, manufacturer positioning, and brand alternatives across the pharmaceutical market of Bangladesh.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def get_cached_data():
    df_med = load_full_medicine_dataset()
    df_comp = load_alternatives_per_medicine()
    df_groups = load_alternatives_per_group()
    kpis = calculate_overview_kpis(df_med, df_comp, df_groups)
    return df_med, df_comp, df_groups, kpis

try:
    df_med, df_comp, df_groups, kpis = get_cached_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading project datasets: {e}")
    data_loaded = False

if data_loaded:
    # Luxury Hero Card
    st.markdown(f"""
    <div class="luxury-hero">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge-gold">👑 Assorted Medicine Dataset of Bangladesh</span>
                <h2 style="font-size: 1.8rem; margin: 0.8rem 0 0.5rem 0; color: #FFFFFF !important;">
                    Unlocking Patient Savings through Chemical Equivalence
                </h2>
                <p style="max-width: 820px; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.2rem;">
                    Indexing <strong>{kpis['total_medicines']:,} registered branded medicines</strong> across 
                    <strong>{kpis['unique_generics']:,} active generics</strong> and <strong>{kpis['unique_manufacturers']:,} pharmaceutical companies</strong>.
                    Our methodology proves that <strong>{kpis['non_cheapest_share']}%</strong> of marketed medicines are priced higher than the cheapest alternative, 
                    unlocking a <strong>median potential savings of {kpis['median_saving_pct']}%</strong> per prescription.
                </p>
            </div>
        </div>
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem;">
            <span class="badge-gold">✨ {kpis['total_comparable']:,} Comparable Brands</span>
            <span class="badge-peach">🎯 {kpis['total_groups']:,} Alternative Groups</span>
            <span class="badge-purple">💎 {kpis['price_coverage_pct']}% Numerical Price Coverage</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats Row
    st.markdown("<h4 style='margin-bottom: 0.8rem;'>✦ Macro Key Performance Indicators</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Medicines", f"{kpis['total_medicines']:,}", f"{kpis['price_coverage_pct']}% Priced")
    col2.metric("Generics / Actives", f"{kpis['unique_generics']:,}", f"{kpis['unique_drug_classes']:,} Drug Classes")
    col3.metric("Median Saving %", f"{kpis['median_saving_pct']}%", f"{kpis['non_cheapest_share']}% Not Cheapest")
    col4.metric("Comparable Groups", f"{kpis['total_groups']:,}", f"{kpis['unique_manufacturers']} Manufacturers")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='margin-bottom: 0.4rem;'>🧭 Platform Navigation Suite</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.92rem; margin-bottom: 1.2rem;'>Explore the 6 specialized analytical modules designed for patients, healthcare economists, and pharmaceutical researchers:</p>", unsafe_allow_html=True)

    # Navigation Grid
    g1, g2, g3 = st.columns(3)
    
    with g1:
        st.markdown(f"""
        <div class="luxury-card" style="min-height: 185px;">
            <span class="card-emoji">📊</span>
            <h4 style="margin: 0; font-size: 1.15rem;">1. Macro Overview</h4>
            <p style="font-size: 0.86rem; margin: 0.5rem 0 0 0; line-height: 1.55;">
                Macro market analysis, dynamic KPI summaries, price distributions (median vs. mean), and top manufacturers.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_Overview.py", label="Open Market Overview", icon="📊")

    with g2:
        st.markdown(f"""
        <div class="luxury-card" style="min-height: 185px;">
            <span class="card-emoji">🔍</span>
            <h4 style="margin: 0; font-size: 1.15rem;">2. Medicine Alternatives</h4>
            <p style="font-size: 0.86rem; margin: 0.5rem 0 0 0; line-height: 1.55;">
                Search any brand or generic, inspect equivalent alternatives strictly matched by generic + form + strength, and view prices.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Medicine_Alternatives.py", label="Explore Alternatives", icon="🔍")

    with g3:
        st.markdown(f"""
        <div class="luxury-card" style="min-height: 185px;">
            <span class="card-emoji">💰</span>
            <h4 style="margin: 0; font-size: 1.15rem;">3. Savings Calculator</h4>
            <p style="font-size: 0.86rem; margin: 0.5rem 0 0 0; line-height: 1.55;">
                Interactive prescription calculator computing financial savings in BDT and % with safe handling of all pricing edge cases.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_Saving_Calculator.py", label="Open Savings Calculator", icon="💰")

    st.markdown("<br>", unsafe_allow_html=True)
    g4, g5, g6 = st.columns(3)

    with g4:
        st.markdown(f"""
        <div class="luxury-card" style="min-height: 185px;">
            <span class="card-emoji">🏭</span>
            <h4 style="margin: 0; font-size: 1.15rem;">4. Manufacturer Analysis</h4>
            <p style="font-size: 0.86rem; margin: 0.5rem 0 0 0; line-height: 1.55;">
                Benchmark 107 pharmaceutical companies by portfolio size, price index (budget vs. premium), and cheapest brand share.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/4_Manufacturer_Analysis.py", label="Inspect Manufacturers", icon="🏭")

    with g5:
        st.markdown(f"""
        <div class="luxury-card" style="min-height: 185px;">
            <span class="card-emoji">🧬</span>
            <h4 style="margin: 0; font-size: 1.15rem;">5. Therapeutic Groups</h4>
            <p style="font-size: 0.86rem; margin: 0.5rem 0 0 0; line-height: 1.55;">
                Analyze therapeutic drug classes, price dispersion in major categories, and crowded active compounds.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/5_Therapeutic_Groups.py", label="View Therapeutic Groups", icon="🧬")

    with g6:
        st.markdown(f"""
        <div class="luxury-card" style="min-height: 185px;">
            <span class="card-emoji">📁</span>
            <h4 style="margin: 0; font-size: 1.15rem;">6. Data Explorer</h4>
            <p style="font-size: 0.86rem; margin: 0.5rem 0 0 0; line-height: 1.55;">
                Raw & cleaned tabular data browser, column metadata, null-value audits, and filtered CSV export.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/6_Data_Explorer.py", label="Launch Data Explorer", icon="📁")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Methodology & Disclosures
    with st.expander("🔬 Analytical Methodology & Medical Limitations Disclosure", expanded=False):
        st.markdown(f"""
        * **Strict Alternative Definition:** Two brands are considered alternatives **only** if they share the exact identical `generic_name + dosage_form_name + normalized strength`.
        * **Regulatory Disclosure:** Product equivalence in this dataset reflects matching active ingredient, formulation, and strength. It does **not** constitute clinical bioequivalence proof, pharmacokinetic validation, or a personal pharmacist prescription.
        * **Availability Limitation:** The source dataset does not contain inventory, pharmacy stock levels, or geographical availability.
        * **Ambiguous Pricing Handling:** Formulations with multiple competing pack prices in a single description were deliberately preserved as `NULL` in numerical columns to guarantee extraction accuracy over false guesses.
        """)
