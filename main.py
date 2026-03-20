# =================================================================
# YIELD HAWK SIMULATOR 
# =================================================================
import streamlit as st
from yield_hawk_simulation import (YieldHawkInputs,
                                   fetch_spx_level, 
                                   inp_assumps,
                                   cash_flow_calc,
                                   savings_comparison,
                                   option_legs,
                                   scenario_analysis, 
                                   final_report)

st.set_page_config(page_title="Yield Hawk Simulator", layout="wide")
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

days = st.sidebar.slider(
    "Borrowing Period (days)", 
    min_value = 1, max_value = 365, value = 50, step = 1
)


num_scenarios = st.sidebar.slider(
    "Number of Scenarios",
    min_value = 3, max_value = 10, value = 5, step = 1 
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
    days = days,
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
legs = option_legs(inputs, cashflows)
st.divider()
scenarios  = scenario_analysis(inputs, legs, cashflows)
st.divider()
report = final_report(inputs, cashflows, comparison, 
                      lt_cap_gains_rate, st_cap_gains_rate)
