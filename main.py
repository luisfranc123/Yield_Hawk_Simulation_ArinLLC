# =================================================================
# YIELD HAWK SIMULATOR 
# =================================================================
import streamlit as st
from datetime import date, timedelta
from yield_hawk_simulation import (YieldHawkInputs,
                                   cash_flow_calc,
                                   savings_comparison,
                                   option_legs,
                                   scenario_analysis,
                                   final_report)

st.set_page_config(page_title="Yield Hawk Simulator", layout="wide")

st.markdown("""
<style>
    /* Headings — Segoe UI Bold, Sky Blue on dark background */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
        color: #1B8FFB !important;
    }
    /* Body text — Calibri, white on dark background */
    body, p, label,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stDataFrame"] {
        font-family: Calibri, Georgia, sans-serif !important;
        color: #FFFFFF;
    }
    /* Preserve Material Icons font for all icon elements */
    [data-testid="stExpanderToggleIcon"] span,
    [data-testid="collapsedControl"] span,
    [data-testid="stSidebarCollapseButton"] span,
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
</style>
""", unsafe_allow_html=True)

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
# SIDEBAR — Borrowing Rates
# -----------------------------------------------
st.sidebar.subheader("Borrowing Rates")
current_rate = st.sidebar.number_input(
    "Alternative Borrowing Rate (%)",
    min_value=1.0, max_value=20.0, value=7.0, step=0.25
) / 100
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
    current_rate = current_rate,
    hawk_rate = hawk_rate,
    advisory_rate = advisory_rate,
    expiration_date = expiration_date,
    spread_width = 1000,
    cost_per_contract = 0.01,
    contract_multiplier = 100,
    num_scenarios = num_scenarios,
    spx_override = spx_override, 
)

st.divider()
cashflows = cash_flow_calc(inputs)
st.divider()
comparison = savings_comparison(inputs, cashflows)
st.divider()
report = final_report(inputs, cashflows, comparison,
                      lt_cap_gains_rate, st_cap_gains_rate)
st.divider()

with st.expander("Technical Details — Option Legs & Scenario Analysis"):
    legs = option_legs(inputs, cashflows)
    scenario_analysis(inputs, legs, cashflows)

st.caption(
    "*Results are estimates for illustrative purposes only and may vary "
    "based on market conditions and individual circumstances.*"
)
