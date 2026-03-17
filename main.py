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
st.caption("Based on ArinLLC Risk Advisors — Box Spread Financing Strategy")

# -----------------------------------------------
# SIDEBAR SLIDERS
# -----------------------------------------------
st.sidebar.header("Strategy Inputs")

notional = st.sidebar.number_input(
    "Notional (Loan Amount $)", 
    min_value = 100_000, max_value = 100_000_000, 
    value = 10_000_000, step = 5_000
)

current_rate = st.sidebar.slider(
    "Current Borrowing Rate (%)", 
    min_value = 0.0, max_value = 20.0, value = 5.0, step = 0.1
)/100

hawk_rate = st.sidebar.slider(
    "Yield Hawk Rate gross (%)", 
    min_value = 0.0, max_value = 20.0, value = 4.3, step = 0.1
)/100

advisory_rate = st.sidebar.slider(            
    "Advisory Fee (%)",
    min_value=0.0, max_value=5.0, value=0.5, step=0.05
)/100

days = st.sidebar.slider(
    "Borrowing Period (days)", 
    min_value = 1, max_value = 365, value = 50, step = 1
)

spread_width = st.sidebar.number_input(
    "Spread Width (pts)", 
    min_value = 100, max_value = 5_000, value = 1_000, step = 100
)

cost_per_contract = st.sidebar.number_input(
    "Cost per Contract ($)", 
    min_value = 0.0, max_value = 10.0, value = 0.01, step = 0.01
)

contract_multiplier = st.sidebar.number_input(
    "Contract Multiplier", 
    min_value = 1, max_value = 1_000, value = 100, step = 10
)

num_scenarios = st.sidebar.slider(
    "Number of Scenarios",
    min_value = 3, max_value = 10, value = 5, step = 1 
)

lt_cap_gains_rate = st.sidebar.slider(
    "Long-Term Cap Gains Rate (%)",
    min_value = 0.0, max_value = 40.0, value = 20.0, step = 0.5
)/100

st_cap_gains_rate = st.sidebar.slider(
    "Short-Term Cap Gains Rate (%)",
    min_value = 0.0, max_value = 60.0, value = 37.0, step = 0.5
)/100

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
    days = days,
    spread_width = int(spread_width),
    cost_per_contract = cost_per_contract,
    contract_multiplier = int(contract_multiplier),
    num_scenarios = num_scenarios,
    spx_override = spx_override, 
)

st.divider()
summary = inp_assumps(inputs)
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