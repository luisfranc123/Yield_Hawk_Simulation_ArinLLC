# ============================================================
# OPTION LEGS PAGE
# Displayed as a separate page in the Streamlit sidebar
# ============================================================
import streamlit as st
import pandas as pd
import time
from datetime import date, timedelta
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

expiration_date = st.sidebar.date_input(
    "Expiration Date", 
    value = date.today() + timedelta(days = 50), 
    min_value = date.today() + timedelta(days = 1), 
    max_value = date.today() + timedelta(days = 1825),
    help = "Select the options expiration date. Day count is calculated automatically."
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
    current_rate = 7/100,
    hawk_rate = 4.3/100,
    advisory_rate = 0.25/100,
    expiration_date = expiration_date,
    spread_width = 1_000,
    cost_per_contract = 0.01,
    contract_multiplier = 100,
    spx_override = spx_override,
)

# We need cashflows first since option_legs depends on it
cashflows = cash_flow_calc(inputs)
st.divider()
legs = option_legs(inputs, cashflows)
#-----------------------------------------------
# DISPLAY OPTION LEGS
# -----------------------------------------------
lower_strike = (int(inputs.spx_level)//inputs.spread_width)*inputs.spread_width
upper_strike = lower_strike + inputs.spread_width

st.subheader("Option Legs")
col1, col2, col3 = st.columns(3)
col1.metric("Lower Strike", f"{lower_strike:,}")
col2.metric("Upper Strike", f"{upper_strike:,}")
col3.metric("SPX at Trade", f"{inputs.spx_level:,}")

df = pd.DataFrame(legs).T.reset_index()
df.columns = ["Leg", "Action", "Type", "Strike", "Contracts", "Premium"]
st.dataframe(df, use_container_width=True, hide_index=True)


