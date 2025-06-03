import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# -----------------------------------------------------------------------------
# Sidebar – Key Assumptions & (optional) CSV Upload
# -----------------------------------------------------------------------------
"""A one‑page Streamlit app to model KELP Laboratory LLC cash‑flow, break‑even,
   and five‑year EBITDA.  Upload a CSV of cost lines *or* tweak numbers manually.
"""

st.sidebar.header("🔧 Model Assumptions")

# Optional budget CSV uploader -------------------------------------------------
with st.sidebar.expander("📄 Upload Operating‑Budget CSV (optional)"):
    csv_file = st.file_uploader("Drag & drop CSV", type=["csv"])
    cost_from_csv = 0.0
    reagents_from_csv = 0.0
    if csv_file is not None:
        df_csv = pd.read_csv(csv_file)
        # Expect columns: Name, Monthly USD, Category (optional)
        if "Monthly USD" in df_csv.columns:
            cost_from_csv = df_csv["Monthly USD"].sum()
            # Try to auto‑detect consumables row keywords
            mask_reagent = df_csv["Name"].str.contains("reagent|consumable", case=False, na=False)
            reagents_from_csv = df_csv.loc[mask_reagent, "Monthly USD"].sum()
            st.success(f"Loaded {len(df_csv)} rows • Total fixed + variable cost = ${cost_from_csv:,.0f}/mo")
        else:
            st.error("CSV must include a 'Monthly USD' column.")

# ◼ Company snapshot -----------------------------------------------------------
st.sidebar.subheader("Lab identity")
company_name = st.sidebar.text_input("LLC name", "KELP Laboratory LLC")
launch_year = st.sidebar.number_input("Launch year", value=datetime.now().year, step=1)

# ◼ Personnel ------------------------------------------------------------------
st.sidebar.subheader("Payroll")
num_director = st.sidebar.number_input("Lab Director(s)", 0, 5, 1)
director_salary = st.sidebar.number_input("Director base salary ($)", 50_000, 300_000, 125_000, 5_000)
num_scientists = st.sidebar.number_input("Sr. Scientists", 0, 20, 4)
scientist_salary = st.sidebar.number_input("Scientist base salary ($)", 40_000, 200_000, 93_000, 5_000)
num_techs = st.sidebar.number_input("Lab Techs", 0, 20, 2)
tech_salary = st.sidebar.number_input("Tech base salary ($)", 30_000, 120_000, 51_000, 5_000)
num_admin = st.sidebar.number_input("Admin (FTE)", 0.0, 5.0, 0.5, 0.5)
admin_salary = st.sidebar.number_input("Admin base salary ($)", 30_000, 120_000, 49_000, 5_000)
benefit_load = st.sidebar.slider("Benefits & payroll‑tax loading (%)", 0.0, 0.5, 0.25, 0.01)

# ◼ Fixed & semi‑fixed monthly costs -------------------------------------------
st.sidebar.subheader("Facilities & leases (monthly)")
lab_rent = st.sidebar.number_input("Lab rent", 0, 100_000, 21_945, 1_000)
instrument_lease = st.sidebar.number_input("Instrument leases", 0, 50_000, 14_000, 500)
utilities = st.sidebar.number_input("Utilities", 0, 20_000, 2_000, 100)
argon_packs = st.sidebar.number_input("UHP argon packs / month", 0, 10, 1)
argon_pack_price = st.sidebar.number_input("Price per argon pack ($)", 0, 20_000, 5_324, 100)
service_contracts = st.sidebar.number_input("OEM & facility service", 0, 20_000, 5_000, 500)
insurance = st.sidebar.number_input("Insurance", 0, 20_000, 2_500, 100)
cleaning = st.sidebar.number_input("Lab cleaning / janitorial", 0, 10_000, 1_500, 100)
it_lims = st.sidebar.number_input("IT + LIMS SaaS", 0, 20_000, 4_000, 100)
regulatory = st.sidebar.number_input("Regulatory & PT fees", 0, 20_000, 1_960, 100)
other_fixed = st.sidebar.number_input("Other fixed G&A", 0, 20_000, 500, 100)

# ◼ Per‑sample economics (averaged) -------------------------------------------
st.sidebar.subheader("Per‑sample economics (blended)")
avg_revenue = st.sidebar.number_input("Avg. revenue per sample ($)", 0, 1_000, 120, 5)
variable_cost_default = 22 if reagents_from_csv == 0 else round(reagents_from_csv / 1_400, 2)
variable_cost = st.sidebar.number_input("Variable cost per sample ($)", 0, 500, variable_cost_default, 1)

# ◼ Throughput scenario selector ----------------------------------------------
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

# Fixed cost from manual inputs
manual_fixed = (
    monthly_payroll + lab_rent + instrument_lease + utilities +
    argon_packs * argon_pack_price + service_contracts + insurance +
    cleaning + it_lims + regulatory + other_fixed
)

# Override with CSV total if uploaded
monthly_fixed = cost_from_csv if csv_file is not None else manual_fixed

contribution_margin = avg_revenue - variable_cost
break_even_samples = np.inf if contribution_margin <= 0 else monthly_fixed / contribution_margin

monthly_revenue = expected_samples * avg_revenue
monthly_variable = expected_samples * variable_cost
monthly_profit = monthly_revenue - monthly_variable - monthly_fixed

# -----------------------------------------------------------------------------
# Main Page
# -----------------------------------------------------------------------------
st.title("🧪 KELP Lab Financial Simulator")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Fixed Burn", f"${monthly_fixed:,.0f}")
col2.metric("Contribution Margin / sample", f"${contribution_margin:,.0f}")
col3.metric("Break-even samples / month", f"{break_even_samples:,.0f}")
col4.metric(f"Profit @ {expected_samples} samples", f"${monthly_profit:,.0f}")

with st.expander("ℹ️ Terminology / Legend"):
    st.markdown("""
* **Monthly Fixed Burn** – payroll, rent, leases, utilities, insurance & other overheads that do **not** vary with workload.
* **Variable Cost / sample** – reagents, consumables, gases, QC duplicates, disposal costs that scale directly with each sample.
* **Contribution Margin** – revenue minus variable cost for *one* sample; used to pay fixed costs.
* **Break-even** – sample volume where contribution margin exactly offsets fixed burn (profit = $0).
* **CSV override** – if you upload a budget CSV, the model sums its ‘Monthly USD’ column and uses it as fixed burn; it also tries to auto-deduce a variable-cost suggestion from any row containing ‘consumable’ or ‘reagent’.
    """)

st.divider()

# Profit curve ---------------------------------------------------------------
st.header("📈 Profit vs. Throughput")
max_samples = st.slider("Plot up to this many samples / month", 0, 5_000, 2_500, 100)
samples = np.arange(0, max_samples + 1, 100)
profit_curve = (avg_revenue - variable_cost) * samples - monthly_fixed
curve_df = pd.DataFrame({"Monthly Samples": samples, "Profit ($)": profit_curve})

line = alt.Chart(curve_df).mark_line(size=3).encode(
    x="Monthly Samples", y="Profit ($)", tooltip=["Monthly Samples", "Profit ($)"]
).properties(height=400)
be_rule = alt.Chart(pd.DataFrame({"x": [break_even_samples]})).mark_rule(strokeDash=[6,3], color="red").encode(x="x")

st.altair_chart(line + be_rule, use_container_width=True)
st.caption("🟥 Red dashed line = break-even volume")

# 5‑year projection -----------------------------------------------------------
with st.expander("📊 Five-Year Projection"):
    st.write("Adjust growth & inflation assumptions to explore long-term performance.")
    growth = st.slider("Annual sample growth (%)", 0, 100, 20)
    price_increase = st.slider("Price increase (%)", 0, 20, 3)
    inflation = st.slider("Inflation on fixed cost (%)", 0, 20
