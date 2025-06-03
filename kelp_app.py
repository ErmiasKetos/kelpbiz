"""
KELP Lab Financial Simulator

A comprehensive Streamlit application for modeling revenues, costs, break-even analysis,
and multi-year forecasts for analytical water-testing laboratories.

Dependencies: streamlit, pandas, numpy, altair
Python version: >=3.9
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="KELP Lab Financial Model",
    page_icon="🧪",
    layout="wide",
)

# Default values for all inputs
defaults = {
    "company_name": "KELP Laboratory LLC",
    "launch_year": datetime.now().year,
    "num_director": 1,
    "director_sal": 120000,
    "num_scientist": 2,
    "scientist_sal": 75000,
    "num_tech": 3,
    "tech_sal": 50000,
    "num_admin": 1.0,
    "admin_sal": 45000,
    "benefit_load": 25,
    "lab_rent": 15000,
    "instr_lease": 8000,
    "utilities": 3000,
    "argon_packs": 2,
    "argon_price": 800,
    "service_contr": 4000,
    "insurance": 2500,
    "cleaning": 1200,
    "it_lims": 2000,
    "regulatory": 1500,
    "other_fixed": 2000,
    "avg_revenue": 180,
    "variable_cost": 25,
    "monthly_samples": 500,
}

# Initialize session state for non-widget keys
if 'cost_from_csv' not in st.session_state:
    st.session_state.cost_from_csv = 0
if 'reagents_from_csv' not in st.session_state:
    st.session_state.reagents_from_csv = 0
if 'analyte_prices' not in st.session_state:
    st.session_state.analyte_prices = {}

# Title
st.title("🧪 KELP Lab Financial Simulator")

# Sidebar
st.sidebar.header("Configuration")

# Reset button
if st.sidebar.button("🔄 Reset to Defaults", type="secondary"):
    for key in defaults.keys():
        if key in st.session_state:
            st.session_state[key] = defaults[key]
    st.session_state.cost_from_csv = 0
    st.session_state.reagents_from_csv = 0
    st.session_state.analyte_prices = {}
    st.rerun()

# CSV Upload - Operating Budget
st.sidebar.subheader("📊 Operating Budget CSV (Optional)")
csv_file = st.sidebar.file_uploader(
    "Upload operating budget CSV", 
    type="csv", 
    key="csv_file",
    help="CSV with columns: 'Name' and 'Monthly USD'"
)

if csv_file is not None:
    try:
        df = pd.read_csv(csv_file)
        if 'Name' in df.columns and 'Monthly USD' in df.columns:
            st.session_state.cost_from_csv = df['Monthly USD'].sum()
            
            # Identify reagents/consumables
            reagent_keywords = ["consumable", "reagent", "media", "chem"]
            reagent_mask = df['Name'].str.lower().str.contains('|'.join(reagent_keywords), na=False)
            st.session_state.reagents_from_csv = df.loc[reagent_mask, 'Monthly USD'].sum()
            
            st.sidebar.success(f"✅ Loaded ${st.session_state.cost_from_csv:,.0f}/mo from CSV")
        else:
            st.sidebar.error("❌ CSV must have 'Name' and 'Monthly USD' columns")
    except Exception as e:
        st.sidebar.error(f"❌ Error reading CSV: {str(e)}")

# CSV Upload - Analyte Prices
st.sidebar.subheader("💰 Analyte Price List CSV")
price_file = st.sidebar.file_uploader(
    "Upload analyte price CSV", 
    type="csv", 
    key="price_file",
    help="CSV with columns: 'Analyte' and 'Price'"
)

if price_file is not None:
    try:
        price_df = pd.read_csv(price_file)
        if 'Analyte' in price_df.columns and 'Price' in price_df.columns:
            st.session_state.analyte_prices = dict(zip(price_df['Analyte'], price_df['Price']))
            st.sidebar.success(f"✅ Loaded {len(st.session_state.analyte_prices)} analytes")
        else:
            st.sidebar.error("❌ CSV must have 'Analyte' and 'Price' columns")
    except Exception as e:
        st.sidebar.error(f"❌ Error reading price CSV: {str(e)}")

# Company Snapshot
st.sidebar.subheader("🏢 Company Snapshot")
company_name = st.sidebar.text_input(
    "LLC name", 
    value=defaults["company_name"], 
    key="company_name"
)
launch_year = st.sidebar.number_input(
    "Launch year", 
    min_value=2000, 
    max_value=2100, 
    value=defaults["launch_year"], 
    step=1,
    key="launch_year"
)

# Payroll Assumptions
st.sidebar.subheader("👥 Payroll Assumptions")
num_director = st.sidebar.number_input(
    "Lab Directors", 
    min_value=0, 
    max_value=5, 
    value=defaults["num_director"], 
    step=1,
    key="num_director"
)
director_sal = st.sidebar.number_input(
    "Director salary ($)", 
    min_value=50000, 
    max_value=300000, 
    value=defaults["director_sal"], 
    step=5000,
    key="director_sal"
)

num_scientist = st.sidebar.number_input(
    "Sr Scientists", 
    min_value=0, 
    max_value=20, 
    value=defaults["num_scientist"], 
    step=1,
    key="num_scientist"
)
scientist_sal = st.sidebar.number_input(
    "Scientist salary ($)", 
    min_value=40000, 
    max_value=200000, 
    value=defaults["scientist_sal"], 
    step=5000,
    key="scientist_sal"
)

num_tech = st.sidebar.number_input(
    "Lab Techs", 
    min_value=0, 
    max_value=20, 
    value=defaults["num_tech"], 
    step=1,
    key="num_tech"
)
tech_sal = st.sidebar.number_input(
    "Tech salary ($)", 
    min_value=30000, 
    max_value=120000, 
    value=defaults["tech_sal"], 
    step=5000,
    key="tech_sal"
)

num_admin = st.sidebar.number_input(
    "Admin (FTE)", 
    min_value=0.0, 
    max_value=5.0, 
    value=defaults["num_admin"], 
    step=0.5,
    key="num_admin"
)
admin_sal = st.sidebar.number_input(
    "Admin salary ($)", 
    min_value=30000, 
    max_value=120000, 
    value=defaults["admin_sal"], 
    step=5000,
    key="admin_sal"
)

benefit_load = st.sidebar.slider(
    "Benefits & payroll-tax (%)", 
    min_value=0, 
    max_value=50, 
    value=defaults["benefit_load"], 
    step=1,
    key="benefit_load"
)

# Fixed Monthly Costs
st.sidebar.subheader("🏭 Fixed Monthly Costs")
lab_rent = st.sidebar.number_input(
    "Lab rent ($)", 
    min_value=0, 
    max_value=100000, 
    value=defaults["lab_rent"], 
    step=1000,
    key="lab_rent"
)
instr_lease = st.sidebar.number_input(
    "Instrument leases ($)", 
    min_value=0, 
    max_value=50000, 
    value=defaults["instr_lease"], 
    step=500,
    key="instr_lease"
)
utilities = st.sidebar.number_input(
    "Utilities (Pwr+Water) ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["utilities"], 
    step=100,
    key="utilities"
)
argon_packs = st.sidebar.number_input(
    "UHP argon packs / mo", 
    min_value=0, 
    max_value=10, 
    value=defaults["argon_packs"], 
    step=1,
    key="argon_packs"
)
argon_price = st.sidebar.number_input(
    "Price per argon pack ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["argon_price"], 
    step=100,
    key="argon_price"
)
service_contr = st.sidebar.number_input(
    "OEM service contracts ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["service_contr"], 
    step=500,
    key="service_contr"
)
insurance = st.sidebar.number_input(
    "Insurance (BOP+WC) ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["insurance"], 
    step=100,
    key="insurance"
)
cleaning = st.sidebar.number_input(
    "Lab cleaning ($)", 
    min_value=0, 
    max_value=10000, 
    value=defaults["cleaning"], 
    step=100,
    key="cleaning"
)
it_lims = st.sidebar.number_input(
    "IT & LIMS SaaS ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["it_lims"], 
    step=100,
    key="it_lims"
)
regulatory = st.sidebar.number_input(
    "Regulatory & PT fees ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["regulatory"], 
    step=100,
    key="regulatory"
)
other_fixed = st.sidebar.number_input(
    "Other fixed G&A ($)", 
    min_value=0, 
    max_value=20000, 
    value=defaults["other_fixed"], 
    step=100,
    key="other_fixed"
)

# Analyte Selection & Pricing
st.sidebar.subheader("🧪 Analyte Selection & Pricing")
if st.session_state.analyte_prices:
    selected_analytes = st.sidebar.multiselect(
        "Select analytes per sample",
        options=list(st.session_state.analyte_prices.keys()),
        key="selected_analytes"
    )
    per_sample_revenue = sum(st.session_state.analyte_prices[analyte] for analyte in selected_analytes)
    st.sidebar.metric("Revenue / sample based on selection", f"${per_sample_revenue:.2f}")
else:
    per_sample_revenue = st.sidebar.number_input(
        "Average revenue / sample ($)", 
        min_value=0.0, 
        max_value=1000.0, 
        value=float(defaults["avg_revenue"]), 
        step=5.0,
        key="avg_revenue"
    )

# Per-Sample Variable Cost
monthly_samples = st.sidebar.number_input(
    "Expected samples / month", 
    min_value=0, 
    max_value=10000, 
    value=defaults["monthly_samples"], 
    step=50,
    key="monthly_samples"
)

# Calculate default variable cost hint
if st.session_state.reagents_from_csv > 0:
    default_var_cost = st.session_state.reagents_from_csv / max(monthly_samples, 1)
else:
    default_var_cost = defaults["variable_cost"]

variable_cost = st.sidebar.number_input(
    "Variable cost / sample ($)", 
    min_value=0.0, 
    max_value=500.0, 
    value=float(default_var_cost), 
    step=1.0,
    key="variable_cost"
)

# Derived Calculations
total_annual_payroll = (
    num_director * director_sal +
    num_scientist * scientist_sal +
    num_tech * tech_sal +
    num_admin * admin_sal
)
monthly_payroll = total_annual_payroll * (1 + benefit_load/100) / 12

manual_fixed = (
    monthly_payroll +
    lab_rent +
    instr_lease +
    utilities +
    (argon_packs * argon_price) +
    service_contr +
    insurance +
    cleaning +
    it_lims +
    regulatory +
    other_fixed
)

# Use CSV cost if available, otherwise manual calculation
if st.session_state.cost_from_csv > 0:
    monthly_fixed = st.session_state.cost_from_csv
else:
    monthly_fixed = manual_fixed

# Contribution margin and break-even
contrib_margin = per_sample_revenue - variable_cost
if contrib_margin <= 0:
    break_even = float("inf")
else:
    break_even = monthly_fixed / contrib_margin

# Profit at current sample volume
revenue = monthly_samples * per_sample_revenue
variable_tot = monthly_samples * variable_cost
monthly_profit = revenue - variable_tot - monthly_fixed

# Main Page - Top KPIs
st.header("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Monthly Fixed Burn", f"${monthly_fixed:,.0f}")

with col2:
    st.metric("Contribution Margin / sample", f"${contrib_margin:.2f}")

with col3:
    if break_even == float("inf"):
        st.metric("Break-even samples / mo", "∞")
    else:
        st.metric("Break-even samples / mo", f"{break_even:,.0f}")

with col4:
    st.metric(f"Profit @ {monthly_samples:,} samples", f"${monthly_profit:,.0f}")

# Legend & Notes
with st.expander("ℹ️ Legend & Notes"):
    st.markdown("""
    * **Monthly Fixed Burn** – non-volume-driven costs (payroll, rent, leases, insurance, etc.).
    * **Variable Cost / sample** – direct, sample-specific costs (e.g., consumables, gases, reagents, QC duplicates, waste disposal). This is computed by summing all consumable/reagent line items (from CSV hint or manual entry) divided by sample count.
    * **Contribution Margin** – incremental profit per sample (revenue minus variable cost).
    * **Break-even samples / mo** – volume at which total contribution margin equals fixed burn.
    * **Analyte Selection** – when an analyte price list is uploaded, select analytes; "Revenue / sample" = sum of selected analyte prices.
    * **Summary Recommendation** – Typical per-sample revenue ranges from **$100 to $250**. Lower-end clients order basic tests (IC + a few metals + microbiology); higher-end clients include PFAS or large panels, pushing revenue to $300–$500. Use the analyte selection tool to calculate your exact average.
    """)

# Profit vs. Throughput Chart
st.subheader("📈 Profit vs. Throughput")

max_plot = st.slider("Plot up to (samples/mo)", 0, 5000, 2500, 100)

arr = np.arange(0, max_plot + 1, 100)
profit_curve = (per_sample_revenue - variable_cost) * arr - monthly_fixed

curve_df = pd.DataFrame({"Samples": arr, "Profit": profit_curve})

line = (
    alt.Chart(curve_df)
    .mark_line(size=3)
    .encode(
        x=alt.X("Samples", title="Monthly Samples"),
        y=alt.Y("Profit", scale=alt.Scale(zero=False), title="Monthly Profit ($)"),
        tooltip=["Samples", alt.Tooltip("Profit", format=",.0f")]
    )
    .properties(height=400)
)

if break_even != float("inf") and break_even <= max_plot:
    be_rule = (
        alt.Chart(pd.DataFrame({"x": [break_even]}))
        .mark_rule(strokeDash=[6,3], color="red", size=2)
        .encode(x=alt.X("x", title="Monthly Samples"))
    )
    chart = line + be_rule
else:
    chart = line

st.altair_chart(chart, use_container_width=True)
st.caption("🟥 Red dashed line = break-even volume")

# Five-Year Projection
with st.expander("📊 Five-Year Projection"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        growth = st.slider("Annual sample growth (%)", 0, 100, 20)
    with col2:
        price_inc = st.slider("Annual price increase (%)", 0, 20, 3)
    with col3:
        inflate = st.slider("Fixed-cost inflation (%)", 0, 20, 4)
    
    years = np.arange(0, 5)
    vols = monthly_samples * (1 + growth/100) ** years
    revs = vols * per_sample_revenue * (1 + price_inc/100) ** years
    vars = vols * variable_cost * (1 + inflate/100) ** years
    fixed = monthly_fixed * (1 + inflate/100) ** years
    ebitda = revs - vars - fixed
    
    proj_df = pd.DataFrame({
        "Year": launch_year + years,
        "Samples / yr": (vols * 12).astype(int),
        "Revenue": revs * 12,
        "Variable Cost": vars * 12,
        "Fixed Cost": fixed * 12,
        "EBITDA": ebitda * 12,
    })
    
    st.dataframe(
        proj_df.style.format({
            "Samples / yr": "{:,}",
            "Revenue": "${:,.0f}",
            "Variable Cost": "${:,.0f}",
            "Fixed Cost": "${:,.0f}",
            "EBITDA": "${:,.0f}",
        }),
        use_container_width=True
    )
    
    bar = (
        alt.Chart(proj_df)
        .mark_bar(size=40)
        .encode(
            x=alt.X("Year:O", title="Fiscal Year"),
            y=alt.Y("EBITDA", title="Annual EBITDA ($)"),
            color=alt.condition(
                alt.datum.EBITDA > 0,
                alt.value("#4caf50"),  # green for positive
                alt.value("#e53935")   # red for negative
            ),
            tooltip=["Year", alt.Tooltip("EBITDA", format="$,.0f")]
        )
        .properties(height=300)
    )
    
    st.altair_chart(bar, use_container_width=True)
    st.caption("Green = positive EBITDA; Red = negative.")

# Footer
st.markdown("---")
st.markdown(
    "*This interactive model is for planning purposes only. "
    "Validate all inputs against actual quotes, contracts, and market data "
    "before making financial decisions.*"
)
