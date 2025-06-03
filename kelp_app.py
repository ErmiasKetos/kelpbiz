"""kelp_lab_finance_app.py
---------------------------------------------------------------------
Streamlit Cloud application to model the operating economics of an
analytical water laboratory (e.g., KELP Laboratory LLC), incorporating
per-analyte pricing for customizable revenue calculations.

Features
  • Manual input **or** CSV upload for cost assumptions
  • Upload analyte price list CSV and select analytes per sample
  • Dynamic break-even & profit-vs-throughput explorer
  • Five-year scenario projection (volume growth, price escalation,
    cost inflation)
  • Responsive Altair visualisations

Requirements: streamlit, pandas, numpy, altair
Deploy on Streamlit Cloud (Python ≥3.9)
---------------------------------------------------------------------
"""
###############################################################################
# Imports & Page Config
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
# Sidebar – Data Uploads & Assumptions
###############################################################################
st.sidebar.title("🔧 Model Assumptions")

# ── 1. Operating-budget CSV upload (optional) ─────────────────────────────────
csv_file = None
cost_from_csv = 0.0
reagents_from_csv = 0.0
with st.sidebar.expander("Upload Operating-Budget CSV (optional)"):
    csv_file = st.file_uploader("Drag & drop CSV (Name, Monthly USD)", type="csv")
    if csv_file is not None:
        df_csv = pd.read_csv(csv_file)
        if "Monthly USD" not in df_csv.columns:
            st.error("CSV must include a 'Monthly USD' column.")
        else:
            cost_from_csv = df_csv["Monthly USD"].sum()
            mask = df_csv["Name"].str.contains("consumable|reagent|media|chem", case=False, na=False)
            reagents_from_csv = df_csv.loc[mask, "Monthly USD"].sum()
            st.success(f"Loaded {len(df_csv)} rows • Total cost = ${cost_from_csv:,.0f}/mo")

# ── 2. Analyte price list CSV upload ──────────────────────────────────────────
price_df = None
analyte_prices = {}
with st.sidebar.expander("Upload Analyte Price List CSV"):
    price_file = st.file_uploader("Drag & drop price list CSV", type="csv")
    if price_file is not None:
        price_df = pd.read_csv(price_file)
        if "Analyte" not in price_df.columns or "Price" not in price_df.columns:
            st.error("Price CSV must include 'Analyte' and 'Price' columns.")
        else:
            analyte_prices = dict(zip(price_df["Analyte"], price_df["Price"]))
            st.success(f"Loaded {len(analyte_prices)} analytes.")

# ── 3. Company snapshot ──────────────────────────────────────────────────────
st.sidebar.subheader("Company Info")
company_name = st.sidebar.text_input("LLC name", "KELP Laboratory LLC")
launch_year = st.sidebar.number_input("Launch year", 2000, 2100, datetime.now().year)

# ── 4. Payroll assumptions ───────────────────────────────────────────────────
st.sidebar.subheader("Payroll")
num_director  = st.sidebar.number_input("Lab Directors",     0, 5, 1)
director_sal  = st.sidebar.number_input("Director salary ($)", 50_000, 300_000, 125_000, 5_000)
num_scientist = st.sidebar.number_input("Sr Scientists",       0, 20, 4)
scientist_sal = st.sidebar.number_input("Scientist salary ($)", 40_000, 200_000, 93_000, 5_000)
num_tech      = st.sidebar.number_input("Lab Techs",           0, 20, 2)
tech_sal      = st.sidebar.number_input("Tech salary ($)",     30_000, 120_000, 51_000, 5_000)
num_admin     = st.sidebar.number_input("Admin (FTE)",         0.0, 5.0, 0.5, 0.5)
admin_sal     = st.sidebar.number_input("Admin salary ($)",    30_000, 120_000, 49_000, 5_000)
benefit_load  = st.sidebar.slider("Benefits & payroll-tax (%)", 0.0, 0.5, 0.25, 0.01)

# ── 5. Fixed monthly costs ───────────────────────────────────────────────────
st.sidebar.subheader("Fixed Costs – Monthly")
lab_rent      = st.sidebar.number_input("Lab rent ($)",               0, 100_000, 21_945, 1_000)
instr_lease   = st.sidebar.number_input("Instrument leases ($)",    0, 50_000, 14_000, 500)
utilities     = st.sidebar.number_input("Utilities (Pwr+Water) ($)", 0, 20_000, 2_000, 100)
argon_packs   = st.sidebar.number_input("UHP argon packs / mo",       0, 10, 1)
argon_price   = st.sidebar.number_input("Price per argon pack ($)",  0, 20_000, 5_324, 100)
service_contr = st.sidebar.number_input("OEM service contracts ($)", 0, 20_000, 5_000, 500)
insurance     = st.sidebar.number_input("Insurance (BOP+WC) ($)",      0, 20_000, 2_500, 100)
cleaning      = st.sidebar.number_input("Lab cleaning ($)",           0, 10_000, 1_500, 100)
it_lims       = st.sidebar.number_input("IT & LIMS SaaS ($)",        0, 20_000, 4_000, 100)
regulatory    = st.sidebar.number_input("Regulatory & PT fees ($)",  0, 20_000, 1_960, 100)
other_fixed   = st.sidebar.number_input("Other fixed G&A ($)",       0, 20_000, 500,   100)

# ── 6. Per-sample analyte selection ─────────────────────────────────────────
st.sidebar.subheader("Analyte Selection & Pricing")
if analyte_prices:
    selected = st.sidebar.multiselect("Select analytes per sample", list(analyte_prices.keys()))
    per_sample_revenue = sum(analyte_prices[a] for a in selected)
    st.sidebar.metric("Revenue / sample based on selection", f"${per_sample_revenue:,.2f}")
else:
    selected = []
    per_sample_revenue = st.sidebar.number_input("Average revenue / sample ($)", 0, 1_000, 120, 5)

# ── 7. Per-sample variable cost ──────────────────────────────────────────────
st.sidebar.subheader("Per-sample Variable Cost")
var_hint = 22 if reagents_from_csv == 0 else round(reagents_from_csv / (monthly_samples or 1), 2)
variable_cost = st.sidebar.number_input("Variable cost / sample ($)", 0, 500, var_hint, 1)

# ── 8. Throughput selector ───────────────────────────────────────────────────
st.sidebar.subheader("Throughput Scenario")
monthly_samples = st.sidebar.number_input("Expected samples / month", 0, 10_000, 1_400, 50)

###############################################################################
# Derived Financials
###############################################################################
# Payroll total
annual_payroll = (
    num_director  * director_sal +
    num_scientist * scientist_sal +
    num_tech      * tech_sal +
    num_admin     * admin_sal
)
monthly_payroll = annual_payroll * (1 + benefit_load) / 12

# Manual fixed cost sum
manual_fixed = (
    monthly_payroll + lab_rent + instr_lease + utilities +
    argon_packs * argon_price + service_contr + insurance +
    cleaning + it_lims + regulatory + other_fixed
)

# Override fixed if CSV provided
monthly_fixed = cost_from_csv if csv_file is not None else manual_fixed

# Break-even & profit
time_margin = per_sample_revenue - variable_cost
break_even = np.inf if time_margin <= 0 else monthly_fixed / time_margin
revenue = monthly_samples * per_sample_revenue
variable_tot = monthly_samples * variable_cost
monthly_profit = revenue - variable_tot - monthly_fixed

###############################################################################
# Main UI – KPIs
###############################################################################
st.title("🧪 KELP Lab Financial Simulator")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Fixed Burn",          f"${monthly_fixed:,.0f}")
col2.metric("Contribution Margin / sample", f"${time_margin:,.2f}")
col3.metric("Break-even samples / mo",      f"{break_even:,.0f}")
col4.metric(f"Profit @ {monthly_samples} samples", f"${monthly_profit:,.0f}")

with st.expander("ℹ️ Legend & Notes"):
    st.markdown("""
* **Monthly Fixed Burn** – costs independent of volume (payroll, rent, leases, etc.).
* **Variable Cost / sample** – direct costs per sample (e.g., consumables, gases, reagents, QC duplicates, hazardous waste disposal). This is calculated by estimating the total cost of these items for a typical mix of analyses and dividing by the number of samples.
* **Contribution Margin** – incremental margin per sample (revenue minus variable cost).
* **Break-even samples / mo** – sample volume where total contribution margin covers fixed burn.
* **Analyte selection** – when a price list CSV is uploaded, select analytes; revenue/sample = sum of selected analyte prices.
* **Summary Recommendation** – Typical per-sample revenue based on customer requests ranges from $100 to $250. Lower-end clients order basic tests (IC + a few metals + microbiology), higher-end clients include PFAS and large panels, pushing revenue to $300–$500. Use the analyzer selection tool above to calculate your precise average.
""")

st.markdown("---")

###############################################################################
# Profit vs. Throughput Chart
###############################################################################
st.subheader("📈 Profit vs. Throughput")
max_plot = st.slider("Plot up to (samples/mo)", 0, 5_000, 2_500, 100)
arr = np.arange(0, max_plot + 1, 100)
profit_curve = (per_sample_revenue - variable_cost) * arr - monthly_fixed
curve_df = pd.DataFrame({"Samples": arr, "Profit": profit_curve})

chart = (
    alt.Chart(curve_df).
