"""kelp_lab_finance_app.py
---------------------------------------------------------------------
Streamlit Cloud application to model the operating economics of an
analytical water laboratory (e.g., KELP Laboratory LLC).

Features
  • Manual input **or** CSV upload for cost assumptions
  • Real‑time break‑even & profit‑vs‑throughput explorer
  • Five‑year scenario projection (volume growth, price escalation,
    cost inflation)
  • Clean Altair visualisations + mobile‑friendly layout

Requirements (auto‑installed on Streamlit Cloud):
  streamlit ≥ 1.32, pandas, numpy, altair
---------------------------------------------------------------------
"""
###############################################################################
# Imports & page config
###############################################################################
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(
    page_title="KELP Lab Financial Model",
    page_icon="🧪",
    layout="wide",
)

###############################################################################
# Sidebar – Assumptions + optional CSV upload
###############################################################################
st.sidebar.title("🔧 Model Assumptions")

# ── 1. Optional CSV upload ───────────────────────────────────────────────────
csv_file = None
cost_from_csv = 0.0
reagents_from_csv = 0.0
with st.sidebar.expander("📄 Upload Operating‑Budget CSV (optional)"):
    csv_file = st.file_uploader("Drag & drop CSV", type="csv")
    if csv_file is not None:
        df_csv = pd.read_csv(csv_file)
        if "Monthly USD" not in df_csv.columns:
            st.error("CSV must include a 'Monthly USD' column.")
        else:
            cost_from_csv = df_csv["Monthly USD"].sum()
            mask = df_csv["Name"].str.contains("consumable|reagent|media|chem", case=False, na=False)
            reagents_from_csv = df_csv.loc[mask, "Monthly USD"].sum()
            st.success(f"Loaded {len(df_csv)} rows • Total cost = ${cost_from_csv:,.0f}/mo")

# ── 2. Company snapshot ──────────────────────────────────────────────────────
st.sidebar.subheader("Company info")
company_name = st.sidebar.text_input("LLC name", "KELP Laboratory LLC")
launch_year = st.sidebar.number_input("Launch year", 2000, 2100, datetime.now().year)

# ── 3. Payroll assumptions ───────────────────────────────────────────────────
st.sidebar.subheader("Payroll")
num_director   = st.sidebar.number_input("Lab Director(s)",  0, 5, 1)
director_sal   = st.sidebar.number_input("Director salary", 50_000, 300_000, 125_000, 5_000)
num_scientist  = st.sidebar.number_input("Sr Scientists",    0, 20, 4)
scientist_sal  = st.sidebar.number_input("Scientist salary", 40_000, 200_000, 93_000, 5_000)
num_tech       = st.sidebar.number_input("Lab Techs",         0, 20, 2)
tech_sal       = st.sidebar.number_input("Tech salary",       30_000, 120_000, 51_000, 5_000)
num_admin      = st.sidebar.number_input("Admin (FTE)",       0.0, 5.0, 0.5, 0.5)
admin_sal      = st.sidebar.number_input("Admin salary",      30_000, 120_000, 49_000, 5_000)
benefit_load   = st.sidebar.slider("Benefits & payroll‑tax (%)", 0.0, 0.5, 0.25, 0.01)

# ── 4. Fixed monthly costs ───────────────────────────────────────────────────
st.sidebar.subheader("Fixed costs – monthly")
lab_rent        = st.sidebar.number_input("Lab rent",                 0, 100_000, 21_945, 1_000)
instr_lease     = st.sidebar.number_input("Instrument leases",       0,  50_000, 14_000,   500)
utilities       = st.sidebar.number_input("Utilities (Pwr+Water)",   0,  20_000,  2_000,   100)
argon_packs     = st.sidebar.number_input("UHP argon packs / mo",    0,      10,       1)
argon_price     = st.sidebar.number_input("Price per argon pack",    0,  20_000,  5_324,   100)
service_contr   = st.sidebar.number_input("OEM service contracts",   0,  20_000,  5_000,   500)
insurance       = st.sidebar.number_input("Insurance (BOP+WC)",      0,  20_000,  2_500,   100)
cleaning        = st.sidebar.number_input("Lab cleaning / janitorial",0,  10_000,  1_500,   100)
it_lims         = st.sidebar.number_input("IT & LIMS SaaS",          0,  20_000,  4_000,   100)
regulatory      = st.sidebar.number_input("Regulatory & PT fees",    0,  20_000,  1_960,   100)
other_fixed     = st.sidebar.number_input("Other fixed G&A",         0,  20_000,    500,   100)

# ── 5. Per‑sample economics ──────────────────────────────────────────────────
st.sidebar.subheader("Per‑sample economics (blended)")
avg_revenue   = st.sidebar.number_input("Average revenue / sample", 0, 1_000, 120, 5)
var_hint      = 22 if reagents_from_csv == 0 else round(reagents_from_csv / 1_400, 2)
variable_cost = st.sidebar.number_input("Variable cost / sample",   0,   500, var_hint, 1)

# ── 6. Throughput selector ───────────────────────────────────────────────────
st.sidebar.subheader("Throughput scenario")
monthly_samples = st.sidebar.number_input("Expected samples / month", 0, 10_000, 1_400, 50)

###############################################################################
# Derived financials
###############################################################################
annual_payroll = (
    num_director  * director_sal +
    num_scientist * scientist_sal +
    num_tech      * tech_sal +
    num_admin     * admin_sal
)
monthly_payroll = annual_payroll * (1 + benefit_load) / 12
manual_fixed = (
    monthly_payroll + lab_rent + instr_lease + utilities +
    argon_packs * argon_price + service_contr + insurance +
    cleaning + it_lims + regulatory + other_fixed
)
monthly_fixed = cost_from_csv if csv_file is not None else manual_fixed
contrib_margin = avg_revenue - variable_cost
break_even = np.inf if contrib_margin <= 0 else monthly_fixed / contrib_margin
revenue = monthly_samples * avg_revenue
variable_tot = monthly_samples * variable_cost
profit = revenue - variable_tot - monthly_fixed

###############################################################################
# Main UI – KPIs
###############################################################################
st.title("🧪 KELP Lab Financial Simulator")

cols = st.columns(4)
cols[0].metric("Monthly Fixed Burn",          f"${monthly_fixed:,.0f}")
cols[1].metric("Contribution Margin / sample", f"${contrib_margin:,.0f}")
cols[2].metric("Break‑even samples / mo",      f"{break_even:,.0f}")
cols[3].metric(f"Profit @ {monthly_samples} samples", f"${profit:,.0f}")

with st.expander("ℹ️ Legend & CSV behaviour"):
    st.markdown("""
* **Monthly Fixed Burn** – costs independent of volume (payroll, rent, leases, insurance…).
* **Variable Cost / sample** – consumables, gases, reagents, QC extras, disposal fees that scale *with* volume.
* **Contribution Margin** – revenue minus variable cost for a single sample.
* **Break‑even** – sample volume where contribution margin exactly equals fixed burn.
* **CSV override** – upload a CSV with a **Monthly USD** column to auto‑set fixed burn; rows containing *consumable, reagent, media,* or *chem* inform a variable‑cost suggestion.
""")

st.markdown("---")

###############################################################################
# Profit vs. throughput chart
###############################################################################
st.subheader("📈 Profit vs. Throughput")
max_plot = st.slider("Plot up to (samples/mo)", 0, 5_000, 2_500, 100)
arr = np.arange(0, max_plot + 1, 100)
profit_curve = (avg_revenue - variable_cost) * arr - monthly_fixed
curve_df = pd.DataFrame({"Samples": arr, "Profit": profit_curve})

chart = (
    alt.Chart(curve_df).mark_line(size=3).encode(
        x="Samples",
        y=alt.Y("Profit", scale=alt.Scale(zero=False)),
        tooltip=["Samples", alt.Tooltip("Profit", format=",")]
    ).properties(height=400)
    + alt.Chart(pd.DataFrame({"x": [break_even]})).mark_rule(strokeDash=[6,3], color="red").encode(x="x")
)

st.altair_chart(chart, use_container_width=True)
st.caption("🟥 Red dashed line = break‑even volume")

###############################################################################
# Five‑year projection
###############################################################################
with st.expander("📊 Five‑Year Projection"):
    g_col, p_col, i_col = st.columns(3)
    growth    = g_col.slider("Annual sample growth (%)", 0, 100, 20)
    price_inc = p_col.slider("Annual price increase (%)", 0, 20, 3)
    inflate   = i_col.slider("Fixed‑cost inflation (%)", 0, 20, 4)

    
