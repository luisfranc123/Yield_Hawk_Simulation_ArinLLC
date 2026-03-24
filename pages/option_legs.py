# ============================================================
# OPTION LEGS PAGE
# Displayed as a separate page in the Streamlit sidebar
# ============================================================
import streamlit as st
import pandas as pd
from yield_hawk_simulation import (YieldHawkInputs,
                                   fetch_spx_level,
                                   cash_flow_calc,
                                   option_legs)

st.set_page_config(page_title = "Option Legs", layout="wide")
st.title("Option Legs Constructor")
st.caption("Box Spread — Four Legs Detail")

# -----------------------------------------------
# SIDEBAR — Inputs (mirrored from main.py)
# We need to re-collect inputs here.
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
# BUILD INPUTS AND RUN OPTION LEGS
# -----------------------------------------------
inputs = YieldHawkInputs(
    notional = notional,
    current_rate = 7 / 100,
    hawk_rate = 4.3 / 100,
    advisory_rate = 0.25 / 100,
    days = days,
    spread_width = 1_000,
    cost_per_contract = 0.01,
    contract_multiplier = 100,
    spx_override = spx_override,
)

# We need cashflows first since option_legs depends on it
cashflows = cash_flow_calc(inputs)
st.divider()
legs = option_legs(inputs, cashflows)

