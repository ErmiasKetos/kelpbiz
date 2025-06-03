import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(page_title="KELP Lab Financial Model", page_icon="🧪", layout="wide")

# -----------------------------------------------------------------------------
# Sidebar – Key Assumptions (user‑editable parameters)
# -----------------------------------------------------------------------------
st.sidebar.header("🔧 Model Assumptions")

# ◼ Company snapshot
st.sidebar.subheader("Lab identity")
company_name = st.sidebar.text_input("LLC name", "KELP Laboratory LLC")
launch_year = st.sidebar.number_input("Launch year", value=datetime.now().year, step=1)

# ◼ Personnel
st.sidebar.subheader("Payroll")
num_director = st.sidebar.number_input("Lab Director(s)", 0, 5, 1)
director_salary = st.sidebar.number_input("Director base salary ($)", 50_000, 300_000, 125_000, 5_000)
num_scientists = st.sidebar.number_input("Sr. Chemists/Microbiologists", 0, 20, 4)
scientist_salary = st.sidebar.number_input("Scientist base salary ($)", 40_000, 200_000, 93_000, 5_000)
num_techs = st.sidebar.number_input("Lab Techs", 0, 20, 2)
tech_salary = st.sidebar.number_input("Tech base salary ($)", 30_000, 120_000, 51_000, 5_000)
num_admin = st.sidebar.number_input("Admin (FTE)", 0.0, 5.0, 0.5, 0.5)
admin_salary = st.sidebar.number_input("Admin base salary ($)", 30_000, 120_000, 49_000, 5_000)
benefit_load = st.sidebar.slider("Benefits & payroll‐tax loading (%)", 0.0, 0.5, 0.25, 0.01)

# ◼ Fixed & semi‑fixed monthly costs
st.sidebar.subheader("Facilities & leases (monthly)")
lab_rent = st.sidebar.number_input("Lab rent", 0, 100_000, 21_945, 1_000)
instrument_lease = st.sidebar.number_input("Instrument leases", 0, 50_000, 14_000, 500)
utilities = st.sidebar.number_input("Utilities (power, water, data)", 0, 20_000, 2_000, 100)
argon_packs = st.sidebar.number_input("UHP argon packs / month", 0, 10, 1)
argon_pack_price = st.sidebar.number_input("Price per argon pack ($)", 0, 20_000, 5_324, 100)
service_contracts = st.sidebar.number_input("OEM & facility service", 0, 20_000, 5_000, 500)
insurance = st.sidebar.number_input("Insurance (BOP + WC + cyber)", 0, 20_000, 2_500, 100)
cleaning = st.sidebar.number_input("Lab cleaning / janitorial", 0, 10_000, 1_500, 100)
it_lims = st.sidebar.number_input("IT + LIMS SaaS", 0, 20_000, 4_000, 100)
regulatory = st.sidebar.number_input("Regulatory & PT fees", 0, 20_000, 1_960, 100)
other_fixed = st.sidebar.number_input("Other fixed G&A", 0, 20_000, 500, 100)

# ◼ Per‑sample economics (averaged)
st.sidebar.subheader("Per‑sample economics (blended)")
avg_revenue = st.sidebar.number_input("Avg. revenue per sample ($)", 0, 1_000, 120, 5)
variable_cost = st.sidebar.number_input("Variable cost per sample ($)", 0, 500, 22, 1)

# ◼ Throughput scenario selector
st.sidebar.subheader("Throughput scenario")
expected_samples = st.sidebar.number_input("Expected monthly sample volume", 0, 10_000, 1_400, 50)

# -----------------------------------------------------------------------------
# Derived calculations
# -----------------------------------------------------------------------------
annual_payroll = (
    num_director * director_salary +
    num_scientists * scientist_salary +
    num_techs * tech_salary +
    num_admin * admin_salary
)
annual_payroll_loaded = annual_payroll * (1 + benefit_load)
monthly_payroll = annual_payroll_loaded / 12

monthly_fixed = (
    monthly_payroll + lab_rent + instrument_lease + utilities +
    argon_packs * argon_pack_price + service_contracts + insurance +
    cleaning + it_lims + regulatory + other_fixed
)

contribution_margin = avg_revenue - variable_cost
break_even_samples = np.inf if contribution_margin <= 0 else monthly_fixed / contribution_margin

# Scenario profitability
monthly_revenue = expected_samples * avg_revenue
monthly_variable = expected_samples * variable_cost
monthly_profit = monthly_revenue - monthly_variable - monthly_fixed

# -----------------------------------------------------------------------------
# Main Page
# -----------------------------------------------------------------------------
st.title("🧪 KELP Lab Financial Simulator")

# Top‑level KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Fixed Burn", f"${monthly_fixed:,.0f}")
col2.metric("Contribution Margin / sample", f"${contribution_margin:,.0f}")
col3.metric("Break‑even samples / month", f"{break_even_samples:,.0f}")
col4.metric("Profit @ {expected_samples} samples", f"${monthly_profit:,.0f}")

# Legend / definitions
with st.expander("ℹ️ Terminology / Legend"):
    st.markdown("""
* **Monthly Fixed Burn** – payroll, rent, leases, utilities, insurance & other costs that do **not** change with sample volume.
* **Variable Cost / sample** – reagents, gases, consumables, QC extras & disposable waste that scale directly with each sample analysed.
* **Contribution Margin** – revenue minus variable cost for one sample; each processed sample contributes this amount toward covering fixed costs.
* **Break‑even samples / month** – the volume where total contribution margin exactly equals fixed burn, i.e. zero profit/loss.
* **Profit @ X samples** – projected net operating profit (before taxes) for your chosen throughput scenario.
    """)

st.divider()

# Profit curve vs. throughput
st.header("📈 Profit vs. Throughput")
max_samples = st.slider("Plot up to this many samples / month", 0, 5_000, 2_500, 100)
samples = np.arange(0, max_samples + 1, 100)
profit = (avg_revenue - variable_cost) * samples - monthly_fixed
plot_df = pd.DataFrame({"Monthly Samples": samples, "Profit ($)": profit})

line = alt.Chart(plot_df).mark_line(size=3).encode(
    x="Monthly Samples", y="Profit ($)",
    tooltip=["Monthly Samples", "Profit ($)"]
).properties(height=400)

be_rule = alt.Chart(pd.DataFrame({"x": [break_even_samples]})).mark_rule(strokeDash=[6,3], color="red").encode(x="x")

st.altair_chart(line + be_rule, use_container_width=True)
st.caption("🟥 Red dashed line = break‑even volume")

# -----------------------------------------------------------------------------
# Five‑year projection (optional)
# -----------------------------------------------------------------------------
with st.expander("📊 Five‑Year Projection"):
    st.write("Adjust growth & inflation assumptions to explore long‑term performance.")
    growth = st.slider("Annual sample‑volume growth (%)", 0, 100, 20)
    price_increase = st.slider("Annual price increase (%)", 0, 20, 3)
    inflation = st.slider("Annual fixed‑cost inflation (%)", 0, 20, 4)

    years = np.arange(0, 5)
    volumes = expected_samples * (1 + growth/100) ** years
    revenues = volumes * avg_revenue * (1 + price_increase/100) ** years
    variables = volumes * variable_cost * (1 + inflation/100) ** years
    fixed_stream = monthly_fixed * (1 + inflation/100) ** years * 12
    ebitda = revenues - variables - fixed_stream

    df = pd.DataFrame({
        "Year": launch_year + years,
        "Samples / yr": volumes * 12,
        "Revenue": revenues,
        "Variable Cost": variables,
        "Fixed Cost": fixed_stream,
        "EBITDA": ebitda,
    })

    st.dataframe(df.style.format({
        "Samples / yr": "{:,.0f}",
        "Revenue": "${:,.0f}",
        "Variable Cost": "${:,.0f}",
        "Fixed Cost": "${:,.0f}",
        "EBITDA": "${:,.0f}"
    }), use_container_width=True)

    st.altair_chart(
        alt.Chart(df).mark_bar(size=40).encode(
            x="Year:O",
            y="EBITDA",
            color=alt.condition(alt.datum.EBITDA > 0, alt.value("#4caf50"), alt.value("#e53935"))
        ).properties(height=300),
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.write("---")
st.markdown("*This interactive tool is for planning purposes only. Validate all inputs against actual quotes, contracts, and market data before making financial commitments.*")
