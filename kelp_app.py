"""kelp_lab_finance_app.py
---------------------------------------------------------------------
Pro‑level Streamlit Cloud application to model operating economics for
an analytical water laboratory (e.g., KELP Laboratory LLC).
Features
  • Manual input OR CSV upload of cost lines
  • Real‑time break‑even & profit explorer
  • Five‑year growth / inflation projection
  • Altair visualisations + streamlined UX
Deploy on Streamlit Cloud with Python ≥3.9; required packages:
  streamlit, pandas, numpy, altair
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

# ── 1. Upload existing operating‑budget CSV (optional) ───────────────────────
with st.sidebar.expander("📄 Upload Operating‑Budget CSV (optional)"):
    csv_file = st.file_uploader("Drag & drop CSV", type="csv")
    cost_from_csv = 0.0   # total monthly cost in file
    reagents_from_csv = 0.0  # estimate consumables spend for variable cost hint
    if csv_file is not None:
        df_csv = pd.read_csv(csv_file)
        if "Monthly USD" in df_csv.columns:
            cost_from_csv = df_csv["Monthly USD"].sum()
            mask = df_csv["Name"].str.contains("consumable|reagent|chem|media", case=False, na=False)
            reagents_from_csv = df_csv.loc[mask, "Monthly USD"].sum()
            st.success(f"Loaded {len(df_csv)} rows • Total cost = ${cost_from_csv:,.0f}/mo")
        else:
            st.error("CSV must include a 'Monthly USD' column")

# ── 2. Company snapshot ──────────────────────────────────────────────────────
st.sidebar.subheader("Company info")
company_name = st.sidebar.text_input("LLC name", "KELP Laboratory LLC")
launch_year = st.sidebar.number_input("Launch year", 2000, 2100, datetime.now().year)

# ── 3. Payroll inputs ────────────────────────────────────────────────────────
st.sidebar.subheader("Payroll")
num_director   = st.sidebar.number_input("Lab Director(s)",  0, 5, 1)
director_sal   = st.sidebar.number_input("Director salary", 50_000, 300_000, 125_000, 5_000)
num_scientist  = st.sidebar.number_input("Sr Scientists",   0, 20, 4)
scientist_sal  = st.sidebar.number_input("Scientist salary", 40_000, 200_000, 93_000, 5_000)
num_tech       = st.sidebar.number_input("Lab Techs",        0, 20, 2)
tech_sal       = st.sidebar.number_input("Tech salary",      30_000, 120_000, 51_000, 5_000)
num_admin      = st.sidebar.number_input("Admin (FTE)",      0.0, 5.0, 0.5, 0.5)
admin_sal      = st.sidebar.number_input("Admin salary",     30_000, 120_000, 49_000, 5_000)
benefit_load   = st.sidebar.slider("Benefits & payroll‑tax (%)", 0.0, 0.5, 0.25, 0.01)

# ── 4. Fixed & semi‑fixed cost inputs ────────────────────────────────────────
st.sidebar.subheader("Fixed costs – monthly")
lab_rent        = st.sidebar.number_input("Lab rent",                 0, 100_000, 21_945, 1_000)
instr_lease     = st.sidebar.number_input("Instrument leases",       0,  50_000, 14_000,   500)
utilities       = st.sidebar.number_input("Utilities (Pwr+Water)",   0,  20_000,  2_000,   100)
argon_packs     = st.sidebar.number_input("UHP Argon packs / mo",    0,      10,       1)
argon_price     = st.sidebar.number_input("Price per Argon pack",    0,  20_000,  5_324,   100)
service_contr   = st.sidebar.number_input("OEM service contracts",   0,  20_000,  5_000,   500)
insurance       = st.sidebar.number_input("Insurance (BOP+WC)",      0,  20_000,  2_500,   100)
cleaning        = st.sidebar.number_input("Lab cleaning",             0,  10_000,  1_500,   100)
it_lims         = st.sidebar.number_input("IT & LIMS SaaS",          0,  20_000,  4_000,   100)
regulatory      = st.sidebar.number_input("Regulatory & PT fees",    0,  20_000,  1_960,   100)
other_fixed     = st.sidebar.number_input("Other fixed G&A",         0,  20_000,    500,   100)

# ── 5. Per‑sample economics ──────────────────────────────────────────────────
st.sidebar.subheader("Per‑sample economics (blended)")
avg_revenue   = st.sidebar.number_input("Average revenue / sample", 0, 1_000, 120, 5)
variable_hint = 22 if reagents_from_csv == 0 else round(reagents_from_csv / 1_400, 2)
variable_cost = st.sidebar.number_input("Variable cost / sample",   0,   500, variable_hint, 1)

# ── 6. Throughput selector ───────────────────────────────────────────────────
st.sidebar.subheader("Throughput scenario")
monthly_samples = st.sidebar.number_input("Expected samples / month", 0, 10_000, 1_400, 50)

###############################################################################
# Derived metrics
###############################################################################
# Payroll
annual_payroll = (
    num_director  * director_sal +
    num_scientist * scientist_sal +
    num_tech      * tech_sal +
    num_admin     * admin_sal
)
monthly_payroll = annual_payroll * (1 + benefit_load) / 12

# Manual fixed
manual_fixed = (
    monthly_payroll + lab_rent + instr_lease + utilities +
    argon_packs * argon_price + service_contr + insurance +
    cleaning + it_lims + regulatory + other_fixed
)

# If CSV present, use its total instead
monthly_fixed = cost_from_csv if csv_file is not None else manual_fixed

contrib_margin = avg_revenue - variable_cost
break_even     = np.inf if contrib_margin <= 0 else monthly_fixed / contrib_margin

# Scenario profit
revenue      = monthly_samples * avg_revenue
variable_tot = monthly_samples * variable_cost
profit       = revenue - variable_tot - monthly_fixed

###############################################################################
# Main UI
###############################################################################
st.title("🧪 KELP Lab Financial Simulator")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Monthly Fixed Burn",          f"${monthly_fixed:,.0f}")
kpi2.metric("Contribution Margin / sample", f"${contrib_margin:,.0f}")
kpi3.metric("Break‑even samples / mo",      f"{break_even:,.0f}")
kpi4.metric(f"Profit @ {monthly_samples} samples", f"${profit:,.0f}")

# Legend
with st.expander("ℹ️ Terminology / Legend"):
    st.markdown("""
**Monthly Fixed Burn** – costs that stay the same whether you analyse 0 or 3 000 samples (payroll, rent, leases …).

**Variable Cost / sample** – consumables, gases, reagents, QC duplicates, disposal fees that scale *directly* with each sample.

**Contribution Margin** – what each sample contributes toward fixed costs (= revenue – variable cost).

**Break‑even samples / mo** – volume where total contribution margin exactly equals monthly fixed burn.

**CSV override** – if you upload a budget CSV with a **Monthly USD** column, that total replaces manual fixed‑cost inputs. The app also tries to parse consumables rows to suggest a variable‑cost figure.
    """)

st.divider()

###############################################################################
# Profit vs. throughput chart
###############################################################################
max_plot = st.slider("Plot throughput up to (samples/mo)", 0, 5_000, 2_500, 100)
arr = np.arange(0, max_plot + 1, 100)
profit_curve = (avg_revenue - variable_cost) * arr - monthly_fixed
curve_df = pd.DataFrame({"Samples": arr, "Profit": profit_curve})

line = alt.Chart(curve_df).mark_line(size=3).encode(
    x="Samples", y="Profit",
    tooltip=["Samples", alt.Tooltip("Profit", format="," )]
).properties(height=400)
be_rule = alt.Chart(pd.DataFrame({"be": [break_even]})).mark_rule(
    strokeDash=[6,3], color="red").encode(x="be")

st.altair_chart(line + be_rule, use_container_width=True)
st.caption("🟥 Red dashed line = break‑even volume")

###############################################################################
# Five‑year projection
###############################################################################
with st.expander("📊 Five‑Year Projection"):
    colA, colB, colC = st.columns(3)
    growth         = colA.slider("Annual sample growth (%)", 0, 100, 20)
    price_up       = colB.slider("Annual price increase (%)", 0, 20, 3)
    inflation      = colC.slider("Fixed‑cost inflation (%)", 0, 20, 4)

    years = np.arange(0, 5)
    vols  = monthly_samples * (1 + growth/100) ** years
    revs  = vols * avg_revenue * (1 + price_up/100) ** years
    vars  = vols * variable_cost * (1 + inflation/100) ** years
    fixed = monthly_fixed * (1 + inflation/100) ** years
    ebitda = revs - vars - fixed

    proj_df = pd.
