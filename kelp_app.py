import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(page_title="KELP Lab Financial Model", page_icon="🧪", layout="wide")

# -----------------------------------------------------------------------------
# Sidebar ‒ Key Assumptions (edit to run scenarios)
# -----------------------------------------------------------------------------
st.sidebar.header("🔧 Model Assumptions")

# --- COMPANY INFO -------------------------------------------------------------
st.sidebar.subheader("Company snapshot")
company_name = st.sidebar.text_input("LLC name", "KELP Laboratory LLC")
launch_year = st.sidebar.number_input("Launch year", value=datetime.now().year, step=1)

# --- PERSONNEL ----------------------------------------------------------------
st.sidebar.subheader("Payroll")
num_director = st.sidebar.number_input("Lab Director(s)", 0, 5, value=1)
director_salary = st.sidebar.number_input("Director base salary ($)", 50000, 300000, value=125000, step=5000)
num_scientists = st.sidebar.number_input("Sr. Chemists/Microbiologists", 0, 20, value=4)
scientist_salary = st.sidebar.number_input("Scientist base salary ($)", 40000, 200000, value=93000, step=5000)
num_techs = st.sidebar.number_input("Lab Techs", 0, 20, value=2)
tech_salary = st.sidebar.number_input("Tech base salary ($)", 30000, 120000, value=51000, step=5000)
num_admin = st.sidebar.number_input("Admin (FTE)", 0.0, 5.0, value=0.5, step=0.5)
admin_salary = st.sidebar.number_input("Admin base salary ($)", 30000, 120000, value=49000, step=5000)
benefit_load = st.sidebar.slider("Benefits & payroll tax loading (%)", 0.0, 0.5, value=0.25)

# --- FIXED & SEMI‑FIXED MONTHLY COSTS ----------------------------------------
st.sidebar.subheader("Facilities & leases (monthly)")
lab_rent = st.sidebar.number_input("Lab rent", 0, 100000, value=21945, step=1000)
instrument_lease = st.sidebar.number_input("Instrument leases", 0, 50000, value=14000, step=500)
utilities = st.sidebar.number_input("Utilities (power, water, data)", 0, 20000, value=2000, step=100)
argon_packs = st.sidebar.number_input("UHP Argon packs / month", 0, 10, value=1)
argon_pack_price = st.sidebar.number_input("Price per argon pack ($)", 0, 20000, value=5324, step=100)
service_contracts = st.sidebar.number_input("OEM & facility service", 0, 20000, value=5000, step=500)
insurance = st.sidebar.number_input("Insurance (BOP + WC + cyber)", 0, 20000, value=2500, step=100)
cleaning = st.sidebar.number_input("Lab cleaning / janitorial", 0, 10000, value=1500, step=100)
it_lims = st.sidebar.number_input("IT + LIMS SaaS", 0, 20000, value=4000, step=100)
regulatory = st.sidebar.number_input("Regulatory & PT fees", 0, 20000, value=1960, step=100)
other_fixed = st.sidebar.number_input("Other fixed G&A", 0, 20000, value=500, step=100)

# --- VARIABLE PER‑SAMPLE COST -------------------------------------------------
st.sidebar.subheader("Per‑sample economics")
avg_revenue = st.sidebar.number_input("Avg. revenue per sample", 0, 1000, value=120, step=5)
variable_cost = st.sidebar.number_input("Variable cost per sample", 0, 500, value=22, step=1)

# -----------------------------------------------------------------------------
# Derived calculations
# -----------------------------------------------------------------------------
# Payroll
annual_payroll = (
    num_director * director_salary +
    num_scientists * scientist_salary +
    num_techs * tech_salary +
    num_admin * admin_salary
)
annual_payroll_loaded = annual_payroll * (1 + benefit_load)
monthly_payroll = annual_payroll_loaded / 12

# Fixed & semi‑fixed monthly burn
monthly_fixed = (
    monthly_payroll + lab_rent + instrument_lease + utilities +
    argon_packs * argon_pack_price + service_contracts + insurance +
    cleaning + it_lims + regulatory + other_fixed
)

# Break‑even throughput
contribution_margin = avg_revenue - variable_cost
be_samples = np.inf if contribution_margin <= 0 else monthly_fixed / contribution_margin

# -----------------------------------------------------------------------------
# Main UI
# -----------------------------------------------------------------------------
st.title("🧪 KELP Laboratory Financial Simulator")

col1, col2, col3 = st.columns(3)
col1.metric("Monthly Fixed Burn", f"${monthly_fixed:,.0f}")
col2.metric("Contribution Margin / sample", f"${contribution_margin:,.0f}")
col3.metric("Break‑even samples / month", f"{be_samples:,.0f}")

st.divider()

# Throughput scenario explorer
st.header("📈 Profit vs. Throughput Scenario")
max_samples = st.slider("Select maximum monthly sample volume to plot", 0, 5000, 2500, 100)

samples = np.arange(0, max_samples + 1, 100)
profit = (avg_revenue - variable_cost) * samples - monthly_fixed
scenario_df = pd.DataFrame({"Monthly Samples": samples, "Profit ($)": profit})

line = (
    alt.Chart(scenario_df)
    .mark_line(interpolate="monotone", size=3)
    .encode(
        x="Monthly Samples",
        y="Profit ($)",
        tooltip=["Monthly Samples", "Profit ($)"]
    )
    .properties(height=400)
)

be_rule = (
    alt.Chart(pd.DataFrame({"be": [be_samples]}))
    .mark_rule(strokeDash=[6,3], color="red")
    .encode(x="be")
)

st.altair_chart(line + be_rule, use_container_width=True)

st.caption("🔴 Dashed line shows financial break‑even point.")

# -----------------------------------------------------------------------------
# Multi‑year projection (optional)
# -----------------------------------------------------------------------------
with st.expander("📊 Five‑Year Projection"):
    st.write("Adjust growth & inflation assumptions to see long‑term cash‑flow.")
    annual_sample_growth = st.slider("Annual sample‑volume growth (%)", 0, 100, 20)
    annual_price_increase = st.slider("Annual price increase (%)", 0, 20, 3)
    annual_fixed_inflation = st.slider("Annual fixed‑cost inflation (%)", 0, 20, 4)

    years = np.arange(0, 5)
    year_list = launch_year + years
    volume = (1 + annual_sample_growth/100) ** years * be_samples  # start at break-even volume
    revenue_stream = volume * 12 * avg_revenue * (1 + annual_price_increase/100) ** years
    variable_stream = volume * 12 * variable_cost * (1 + annual_fixed_inflation/100) ** years

    fixed_stream = monthly_fixed * 12 * (1 + annual_fixed_inflation/100) ** years
    ebitda = revenue_stream - variable_stream - fixed_stream

    proj_df = pd.DataFrame({
        "Year": year_list,
        "Samples / yr": volume * 12,
        "Revenue": revenue_stream,
        "Variable Cost": variable_stream,
        "Fixed Cost": fixed_stream,
        "EBITDA": ebitda
    })

    st.dataframe(proj_df.style.format({
        "Samples / yr": "{:,.0f}",
        "Revenue": "${:,.0f}",
        "Variable Cost": "${:,.0f}",
        "Fixed Cost": "${:,.0f}",
        "EBITDA": "${:,.0f}"
    }), use_container_width=True)

    bar = (
        alt.Chart(proj_df)
        .mark_bar(size=40)
        .encode(x="Year:O", y="EBITDA", color=alt.condition(alt.datum.EBITDA > 0, alt.value("#4caf50"), alt.value("#e53935")))
        .properties(height=300)
    )
    st.altair_chart(bar, use_container_width=True)
    st.caption("Green = positive EBITDA; red = negative.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.write("---")
st.markdown("*This interactive model is built for high‑level decision support only. Please validate cost & pricing data for your specific operation before committing capital.*")
