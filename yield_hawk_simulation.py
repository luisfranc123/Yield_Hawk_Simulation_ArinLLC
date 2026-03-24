# ============================================================
# YIELD HAWK STRATEGY SIMULATOR
# Based on Arin Risk Advisors -- Box Spread Financing Strategy
# ============================================================

import yfinance as yf
import streamlit as st
import pandas as pd
import time

# -----------------------------------------------
# CACHED SPX FETCH (outside the class)
# -----------------------------------------------
@st.cache_data(ttl=900)
def fetch_spx_level() -> float:
    """
    Fetches the latest SPX closing price from Yahoo Finance.
    Cached for 15 minutes to avoid rate limiting on cloud deployments.
    """
    for attempt in range(3):
        try:
            spx_ticker = yf.Ticker("^GSPC")
            spx_history = spx_ticker.history(period = "1d")
            if not spx_history.empty:
                return round(spx_history["Close"].iloc[-1], 2)
        except Exception:
            time.sleep(2)
    return None


# -----------------------------------------------
# SHARED INPUT CONTAINER
# -----------------------------------------------
class YieldHawkInputs:
    def __init__(self, notional, current_rate,
                 hawk_rate, advisory_rate, days,
                 spread_width = 1_000,
                 cost_per_contract = 0.01,
                 contract_multiplier = 100,
                 num_scenarios = 5,
                 spx_override = None):

        self.notional = notional
        self.current_rate = current_rate
        self.hawk_rate = hawk_rate
        self.advisory_rate = advisory_rate
        self.days = days
        self.spread_width = spread_width
        self.cost_per_contract = cost_per_contract
        self.contract_multiplier = contract_multiplier
        self.num_scenarios = num_scenarios

        # Use manual override if provided, otherwise fetch live
        if spx_override is not None:
            self.spx_level = spx_override
        else:
            with st.spinner("Fetching live SPX level..."):
                level = fetch_spx_level()
                if level is None:
                    st.error("Could not fetch SPX level from Yahoo Finance. "
                             "Please enter it manually in the sidebar.")
                    self.spx_level = 0.0
                else:
                    self.spx_level = level

        self.notional_per_spread = self.spread_width * self.contract_multiplier
        self.num_spreads = self.notional / self.notional_per_spread


# -----------------------------------------------
# FUNCTION 1: Inputs & Assumptions Summary
# -----------------------------------------------
def inp_assumps(inputs: YieldHawkInputs) -> dict:
    """
    Returns a summary dictionary of all inputs and assumptions.

    Args:
        inputs (YieldHawkInputs): shared input object
    """
    summary_inputs = {
        "Notional (Loan Amount)": inputs.notional,
        "Current Borrowing Rate (%)": round(inputs.current_rate * 100, 2),
        "Yield Hawk Rate gross (%)": round(inputs.hawk_rate * 100, 2),
        "Advisory Fee (%)": round(inputs.advisory_rate * 100, 2),
        "Borrowing Period (days)": inputs.days,
        "Current SPX Level": inputs.spx_level,
        "Spread Width (pts)": inputs.spread_width,
        "Notional per Spread ($)": inputs.notional_per_spread,
        "Number of Spreads": round(inputs.num_spreads, 1),
    }

    return summary_inputs


# -----------------------------------------------
# FUNCTION 2: Cash Flow Calculations
# -----------------------------------------------
def cash_flow_calc(inputs: YieldHawkInputs) -> dict:
    """
    Returns a dictionary of all cash flow calculations.

    Args:
        inputs (YieldHawkInputs): shared input object
    """
    # 2.1 Proceeds received today
    proceeds_today = inputs.notional / (1 + inputs.hawk_rate * (inputs.days / 365))

    # 2.2 Obligation at expiration (always full notional)
    obligation = inputs.notional

    # 2.3 Gross financing cost
    gross_cost = obligation - proceeds_today

    # 2.4 Advisory fee prorated for borrowing period
    advisory_fee_cost = inputs.notional * inputs.advisory_rate * (inputs.days / 365)

    # 2.5 Brokerage commissions
    brokerage_cost = 4 * inputs.num_spreads * inputs.cost_per_contract

    # 2.6 Total all-in financing cost
    total_cost = gross_cost + advisory_fee_cost + brokerage_cost

    # 2.7 Effective annualized rate
    allin_rate = (total_cost / inputs.notional) * (365 / inputs.days)

    cashflows = {
        "Adivory Rate (%)": inputs.advisory_rate*100,
        "Gross Financing Cost ($)": round(gross_cost, 2),
        "Advisory Fee Cost ($)": round(advisory_fee_cost, 2),
        "Brokerage Commission Cost ($)": round(brokerage_cost, 2),
        "Total All-In Financing Cost ($)": round(total_cost, 2),
        "All-In Annualized Rate (%)": round(allin_rate * 100, 4),
    }

    st.subheader("Cash Flow Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Proceeds Today", f"${proceeds_today:,.2f}")
    col2.metric("Total Financing Cost", f"${total_cost:,.2f}")
    col3.metric("All-In Rate (ann.)", f"{allin_rate*100:.4f}%")

    df = pd.DataFrame(
        [(k, f"${v:,.2f}" if "$" in k else f"{v}") for k, v in cashflows.items()],
        columns=["Item", "Value"]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    return cashflows


# -----------------------------------------------
# FUNCTION 3: Side-by-Side Savings Comparison
# -----------------------------------------------
def savings_comparison(inputs: YieldHawkInputs, cashflows: dict) -> dict:
    """
    Compares the current borrowing rate against Yield Hawk
    and calculates the dollar savings.

    Args:
        inputs (YieldHawkInputs): shared input object
        cashflows (dict): output from cash_flow_calc()
    """
    # Current rate cost
    current_cost_period = inputs.notional * inputs.current_rate * (inputs.days / 365)
    current_cost_annual = inputs.notional * inputs.current_rate

    # Yield Hawk cost
    hawk_cost_period  = cashflows["Total All-In Financing Cost ($)"]
    hawk_rate_annual = cashflows["All-In Annualized Rate (%)"] / 100
    hawk_cost_annual = inputs.notional * hawk_rate_annual

    # Savings
    savings_period = current_cost_period - hawk_cost_period
    savings_annual = current_cost_annual - hawk_cost_annual
    savings_rate = inputs.current_rate - hawk_rate_annual

    comparison = {
        "Financing Rate — Current (%)" : round(inputs.current_rate * 100, 2),
        "Financing Rate — Yield Hawk (%)": round(hawk_rate_annual * 100, 4),
        "Rate Savings (%)": round(savings_rate * 100, 4),
        "Cost (Period) — Current ($)": round(current_cost_period, 2),
        "Cost (Period) — Yield Hawk ($)": round(hawk_cost_period, 2),
        "Savings per Period ($)": round(savings_period, 2),
        "Cost (Annual) — Current ($)": round(current_cost_annual, 2),
        "Cost (Annual) — Yield Hawk ($)": round(hawk_cost_annual, 2),
        "Annual Savings ($)": round(savings_annual, 2),
    }

    st.subheader("Savings Comparison")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rate Savings", f"{savings_rate*100:.4f}%",
                delta=f"-{savings_rate*100:.2f}% vs current")
    col2.metric("Period Savings", f"${savings_period:,.2f}")
    col3.metric("Annual Savings", f"${savings_annual:,.2f}")

    return comparison


# -----------------------------------------------
# FUNCTION 4: Option Legs Constructor
# -----------------------------------------------
def option_legs(inputs: YieldHawkInputs, cashflows: dict) -> dict:
    """
    Constructs the four legs of the box spread using the
    live SPX level to determine realistic strike prices.

    Args:
        inputs (YieldHawkInputs): shared input object
        cashflows (dict): output from cash_flow_calc()
    """
    # Strike prices
    lower_strike = (int(inputs.spx_level) // inputs.spread_width) * inputs.spread_width
    upper_strike = lower_strike + inputs.spread_width

    # Premium per leg
    proceeds_today = cashflows["Proceeds Received Today ($)"]
    net_per_spread = proceeds_today / inputs.num_spreads
    net_per_contract = net_per_spread / inputs.contract_multiplier

    legs = {
        "SPX Put (Short)" : {
            "action"    : "Sell",
            "type"      : "Put",
            "strike"    : upper_strike,
            "contracts" : int(-inputs.num_spreads),
            "premium"   : round(net_per_contract * 0.03, 2),
        },
        "SPX Call (Short)" : {
            "action"    : "Sell",
            "type"      : "Call",
            "strike"    : lower_strike,
            "contracts" : int(-inputs.num_spreads),
            "premium"   : round(net_per_contract * 0.13, 2),
        },
        "SPX Put (Long)" : {
            "action"    : "Buy",
            "type"      : "Put",
            "strike"    : lower_strike,
            "contracts" : int(inputs.num_spreads),
            "premium"   : round(net_per_contract * 0.30, 2),
        },
        "SPX Call (Long)" : {
            "action"    : "Buy",
            "type"      : "Call",
            "strike"    : upper_strike,
            "contracts" : int(inputs.num_spreads),
            "premium"   : round(net_per_contract * 0.54, 2),
        },
    }

    return legs


# -----------------------------------------------
# FUNCTION 5: Scenario Analysis
# -----------------------------------------------
def scenario_analysis(inputs: YieldHawkInputs, legs: dict, cashflows: dict) -> dict:
    """
    Tests multiple SPX price scenarios at expiration to confirm
    the strategy is market neutral.

    Args:
        inputs (YieldHawkInputs): shared input object
        legs (dict): output from option_legs()
        cashflows(dict): output from cash_flow_calc()
    """
    lower_strike = legs["SPX Put (Long)"]["strike"]
    upper_strike = legs["SPX Call (Long)"]["strike"]

    # Dynamic scenario generation
    range_start = lower_strike - 2 * inputs.spread_width
    range_end = upper_strike + 2 * inputs.spread_width
    step = (range_end - range_start) // (inputs.num_scenarios - 1)

    scenarios = {
        f"SPX at {range_start + i * step:,}" : range_start + i * step
        for i in range(inputs.num_scenarios)
    }

    results = {}

    for leg_name, details in legs.items():
        row = {}
        for label, spx_final in scenarios.items():
            strike    = details["strike"]
            contracts = details["contracts"]

            if details["type"] == "Call":
                payoff = max(spx_final - strike, 0)
            else:
                payoff = max(strike - spx_final, 0)

            value      = payoff * contracts * inputs.contract_multiplier
            row[label] = round(value, 2)

        results[leg_name] = row

    df = pd.DataFrame(results).T
    allin_rate = cashflows["All-In Annualized Rate (%)"]

    st.subheader("Scenario Analysis")
    st.dataframe(df.style.format("${:,.2f}"), use_container_width=True)
    st.info(f"All-In Financing Rate: **{allin_rate:.4f}%** — Identical across all scenarios (market neutral)")

    return df


# -----------------------------------------------
# FUNCTION 6: Final Report with Tax Adjustment
# -----------------------------------------------
def final_report(inputs: YieldHawkInputs,
                 cashflows: dict,
                 comparison: dict,
                 lt_cap_gains_rate: float,
                 st_cap_gains_rate: float) -> dict:
    """
    Produces a final summary report including the Section 1256
    tax-adjusted borrowing cost.

    Args:
        inputs (YieldHawkInputs): shared input object
        cashflows (dict): output from cash_flow_calc()
        comparison (dict): output from savings_comparison()
        lt_cap_gains_raten (float): long-term capital gains rate
        st_cap_gains_rate  (float): short-term capital gains rate
    """
    # Section 1256 blended rate: 60% LT + 40% ST
    blended_tax_rate = 0.60 * lt_cap_gains_rate + 0.40 * st_cap_gains_rate

    # Gross all-in borrowing rate
    gross_rate = cashflows["All-In Annualized Rate (%)"] / 100

    # After-tax borrowing rate
    aftertax_rate = gross_rate * (1 - blended_tax_rate)

    # After-tax dollar costs
    aftertax_cost_period = inputs.notional * aftertax_rate * (inputs.days / 365)
    aftertax_cost_annual = inputs.notional * aftertax_rate

    # After-tax savings vs current rate
    current_cost_annual  = comparison["Cost (Annual) — Current ($)"]
    aftertax_savings = current_cost_annual - aftertax_cost_annual

    tax_report = {
        "After-Tax Cost per Period ($)": round(aftertax_cost_period, 2),
        "After-Tax Cost Annual ($)": round(aftertax_cost_annual, 2),
        "Current Rate Annual Cost ($)": round(current_cost_annual, 2),
    }

    st.subheader("Final Report (Tax-Adjusted)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Rate", f"{gross_rate*100:.4f}%")
    col2.metric("After-Tax Rate", f"{aftertax_rate*100:.4f}%")
    col3.metric("After-Tax Ann. Savings", f"${aftertax_savings:,.2f}")

    df = pd.DataFrame(
        [(k, f"${v:,.2f}" if "$" in k else f"{v}%") for k, v in tax_report.items()],
        columns=["Metric", "Value"]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info(
    f"- **Long-Term Cap Gains Rate:** {(lt_cap_gains_rate*100):.2f}%\n"
    f"- **Short-Term Cap Gains Rate:** {(st_cap_gains_rate*100):.2f}%\n"
    f"- **Blended Tax Rate:** {(blended_tax_rate*100):.2f}%"
    )
    return tax_report
