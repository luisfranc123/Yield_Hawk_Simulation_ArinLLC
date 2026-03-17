### **Yield Hawk Strategy**
---
#### **1. Setting up the Inputs and Assumptions**

We define all the variables needed before doing any math. 

- `notional`: the total amount you want to borrow (e.g. $ 1,000,000)
- `current_rate`: what you're currently paying to borrow (e.g. 7% margin loan)
- `hawk_rate`: Yield Hawk borrowing rate (e.g. 4.30%)
- `advisory_fee`: Arin's fee, which is 0.25% of notional
- `days`: how many days until the options expire (the borrowing period)
- `spx_level`: current S&P 500 index level (used to size contracts)
- `spread_width`: the distance between strikes in index points (typically 1,000)
- `cost_per_contract`: brokerage commision per SPX contract

#### **2. Cash Flow Calculations**

In this section, we need to figure out three thins:

1. **How much cash you receive today**: the discounted proceeds from selling the box spread.
2. **How much you owe at expiration**: the fixed obligation (always the full notional).
3. **What the financing actually costs**: broke down per period and annualized.

The key fprmula is the same logic as a zero-coupon bond. The clien receives less than face cvalue today, and repay the full cface value latr. The difference, annualized, is the client's borrowing rate. 

#### **3. Side-by-Side Savings Comparison**

Compares the current borrowing rate against **Yield Hawk** and calculates the dollar savings.

#### **4. Option Leg Constructor**

This function defines the four actual legs of the box spread trade using the live SPX level. 

 - **SPX Put (Short)**: sell a put at the upper strike
 - **SPX Call (Short)**: Sell a call at the lower strike
 - **SPX Put (Long)**: buy a put at the lower strike
 - **SPX Call (Long)**: buy a call at the upper strike

#### **5. Scenario Analysis**

This section test a series of SPX scenarios, **below**, **between**, and **above** the strikes. One important key insight from here is that **no matter which scenario plays out, the net market value is always the same (market neutrality)**. 

#### **6. Tax-Adjusted Report**

Losses are taxed at blended rate of:
    - **60%** at the long-term capital gains rate
    - **40%** at the short-term capital gains rate. 

Regardless of the holding period. The blended after-tax rate effectively **reduces your true borrwing cost** depending on the tax bracket. 
