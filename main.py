# =================================================================
# YIELD HAWK SIMULATOR 
# =================================================================
import streamlit as st
from datetime import date, timedelta
from yield_hawk_simulation import (YieldHawkInputs,
                                   fetch_spx_level, 
                                   inp_assumps,
                                   cash_flow_calc,
                                   savings_comparison,
                                   option_legs,
                                   scenario_analysis, 
                                   final_report)

st.set_page_config(page_title = "Yield Hawk Simulator", layout = "wide")
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
# SIDEBAR — Tax Rate Inputs          
# -----------------------------------------------
st.sidebar.subheader("Tax Rates")
lt_cap_gains_rate = st.sidebar.number_input(
    "Long-Term Cap Gains Rate (decimal)", 
    min_value = 0.10, max_value = 0.60, value = 0.20, step = 0.5
    )
st_cap_gains_rate = st.sidebar.number_input(
    "Short-Term Cap Gains Rate (decimal)", 
    min_value = 0.10, max_value = 0.60, value = 0.37, step = 0.5
    )

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
    current_rate = 7/100,
    hawk_rate = 4.3/100,
    advisory_rate = 0.25/100,
    expiration_date = expiration_date,
    spread_width = 1000,
    cost_per_contract = 0.01,
    contract_multiplier = 100,
    num_scenarios = num_scenarios,
    spx_override = spx_override, 
)

# Define Option legs to compute scenarios
st.divider()
cashflows = cash_flow_calc(inputs)
st.divider()
comparison = savings_comparison(inputs, cashflows)
st.divider()
legs = option_legs(inputs, cashflows)
scenarios  = scenario_analysis(inputs, legs, cashflows)
st.divider()
report = final_report(inputs, cashflows, comparison, 
                      lt_cap_gains_rate, st_cap_gains_rate)
