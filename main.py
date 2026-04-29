# =================================================================
# YIELD HAWK SIMULATOR 
# =================================================================
import streamlit as st
from datetime import date, timedelta
from yield_hawk_simulation import (YieldHawkInputs,
                                   fetch_sofr_rate,
                                   cash_flow_calc,
                                   savings_comparison,
                                   option_legs,
                                   scenario_analysis,
                                   final_report)

st.set_page_config(page_title="Yield Hawk Simulator", 
                   layout="wide", 
                   initial_sidebar_state = "expanded", 
                   menu_items = None)

st.markdown("""
<style>
    /* Headings — Segoe UI Bold, White on dark background */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    /* Body text — Calibri, white on dark background */
    body, p, label,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stDataFrame"] {
        font-family: Calibri, Georgia, sans-serif !important;
        color: #FFFFFF;
    }
    /* Hide multi-page nav (functionality moved into tabs) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    /* Preserve Material Icons for ALL button spans site-wide */
    button span, header span,
    [data-testid="stExpanderToggleIcon"] span,
    [data-testid="collapsedControl"] span,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebar"] button span,
    .material-icons, span.material-icons {
        font-family: 'Material Icons' !important;
        color: #FFFFFF !important;
    }
    /* Sidebar typography */
    [data-testid="stSidebar"] * {
        font-family: Calibri, Georgia, sans-serif !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
        color: #1B8FFB !important;
    }
    /* Metric labels — Sky Blue */
    [data-testid="stMetricLabel"] {
        font-family: 'Segoe UI', Arial, sans-serif !important;
        font-weight: 600 !important;
        color: #1B8FFB !important;
    }
    /* Metric values — white */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    /* Disclaimer caption — Neutral Gray */
    [data-testid="stCaptionContainer"] {
        color: #80807F !important;
        font-family: Calibri, Georgia, sans-serif !important;
    }
    /* Tabs — inactive gray, active Sky Blue with underline */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Segoe UI', Arial, sans-serif !important;
        font-weight: 600 !important;
        color: #80807F !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1B8FFB !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #1B8FFB !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        background-color: #0A1F38 !important;
    }
    /* Alert / info / success messages — brand dark with Sky Blue border */
    [data-testid="stAlert"] {
        background-color: #0A1F38 !important;
        border-left-color: #1B8FFB !important;
        color: #FFFFFF !important;
    }
    [data-testid="stAlert"] p {
        color: #FFFFFF !important;
    }
    /* NEW: Fix overlapping text issues */
    .stApp header {
        display: none !important;
    }
    
    /* Remove the default "Manage app" button and any floating menus */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* Ensure main content starts at top with proper spacing */
    .main .block-container {
        padding-top: 2rem !important;
    }
    
    /* Remove any deployment/menu icons in top-right */
    .stApp button[title="Manage app"] {
        display: none !important;
    }
    
    /* Hide Streamlit's default "Deploy" button */
    .stApp .st-emotion-cache-1v0mbdj {
        display: none !important;
    }
    
    /* Additional fix for any floating elements */
    [data-testid="baseButton-header"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html = True)

st.title("YIELD HAWK STRATEGY SIMULATOR")
st.caption("Based on Arin Risk Advisors, LLC — Box Spread Financing Strategy")

# -----------------------------------------------
# SIDEBAR SLIDERS
# -----------------------------------------------
st.sidebar.header("Strategy Inputs")

notional = st.sidebar.number_input(
    "Notional (Loan Amount $)", 
    min_value = 100_000, max_value = 100_000_000, 
    value = 1_000_000, step = 10_000
)

expiration_date = st.sidebar.date_input(
    "Expiration Date", 
    value = date.today() + timedelta(days = 50), 
    min_value = date.today() + timedelta(days = 1), 
    max_value = date.today() + timedelta(days = 1825),
    help = "Select the options expiration date. Day count is calculated automatically."
)

num_scenarios = st.sidebar.slider(
    "Number of Scenarios",
    min_value = 3, max_value = 10, value = 5, step = 1 
)

# -----------------------------------------------
# SIDEBAR — SBL Rate (SOFR-Based)
# -----------------------------------------------
st.sidebar.subheader("SBL Rate (SOFR-Based)")

with st.spinner("Fetching SOFR rate..."):
    fetched_sofr = fetch_sofr_rate()

use_manual_sofr = st.sidebar.toggle(
    "Enter SOFR manually",
    value=(fetched_sofr is None)
)

if use_manual_sofr or fetched_sofr is None:
    sofr_rate = st.sidebar.number_input(
        "SOFR Rate (%)",
        min_value=0.0, max_value=15.0, value=5.30, step=0.05
    ) / 100
else:
    sofr_rate = fetched_sofr
    st.sidebar.metric("Live SOFR", f"{sofr_rate*100:.2f}%")

sbl_spread = st.sidebar.number_input(
    "SBL Spread over SOFR (%)",
    min_value=0.25, max_value=5.0, value=1.50, step=0.25
) / 100

# -----------------------------------------------
# SIDEBAR — Yield Hawk Rates
# -----------------------------------------------
st.sidebar.subheader("Yield Hawk Rates")
hawk_rate = st.sidebar.number_input(
    "Yield Hawk Gross Rate (%)",
    min_value=1.0, max_value=15.0, value=4.30, step=0.05
) / 100
advisory_rate = st.sidebar.number_input(
    "Arin Advisory Fee (%)",
    min_value=0.0, max_value=2.0, value=0.25, step=0.05
) / 100

# -----------------------------------------------
# SIDEBAR — Tax Rate Inputs
# -----------------------------------------------
st.sidebar.subheader("Tax Rates")
lt_cap_gains_rate = st.sidebar.number_input(
    "Long-Term Cap Gains Rate (%)",
    min_value=10.0, max_value=60.0, value=20.0, step=1.0
) / 100
st_cap_gains_rate = st.sidebar.number_input(
    "Short-Term Cap Gains Rate (%)",
    min_value=10.0, max_value=60.0, value=37.0, step=1.0
) / 100

# -----------------------------------------------
# SPX LEVEL - Live Fecthed with manual fallback
# -----------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("SPX Level")
use_manual_spx = st.sidebar.toggle("Enter SPX manually", value = False)

if use_manual_spx:
    spx_override = st.sidebar.number_input(
        "SPX Level (manual)", 
        min_value = 1000.0, max_value = 10000.0, 
    value = 5500.0, step = 10.0
    )
else:
    spx_override = None

# -----------------------------------------------
# MAIN — Run all the functions
# -----------------------------------------------
inputs = YieldHawkInputs(
    notional = notional,
    sofr_rate = sofr_rate,
    sbl_spread = sbl_spread,
    hawk_rate = hawk_rate,
    advisory_rate = advisory_rate,
    expiration_date = expiration_date,
    spread_width = 1000,
    cost_per_contract = 0.01,
    contract_multiplier = 100,
    num_scenarios = num_scenarios,
    spx_override = spx_override, 
)

cashflows = cash_flow_calc(inputs)

tab1, tab2, tab3 = st.tabs(["▲ Strategy Comparison", "◈ Tax Analysis", "◎ Option Details"])

with tab1:
    comparison = savings_comparison(inputs, cashflows)

with tab2:
    report = final_report(inputs, cashflows, comparison,
                          lt_cap_gains_rate, st_cap_gains_rate)

with tab3:
    legs = option_legs(inputs, cashflows)
    scenario_analysis(inputs, legs, cashflows)

st.caption(
    "*Results are estimates for illustrative purposes only and may vary "
    "based on market conditions and individual circumstances.*"
)
