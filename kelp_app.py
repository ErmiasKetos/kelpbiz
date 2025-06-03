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
  • “Reset to defaults” button to revert inputs

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

# ----------------------------------------------------------------------------
# Default values dictionary for resetting
# ----------------------------------------------------------------------------
defaults = {
    "num_director": 1,
    "director_sal": 125000,
    "num_scientist": 4,
    "scientist_sal": 93000,
    "num_tech": 2,
    "tech_sal": 51000,
    "num_admin": 0.5,
    "admin_sal": 49000,
    "benefit_load": 0.25,
    "lab_rent": 21945,
    "instr_lease": 14000,
    "utilities": 2000,
    "argon_packs": 1,
    "argon_price": 5324,
    "service_contr": 5000,
    "insurance": 2500,
    "cleaning": 1500,
    "it_lims": 4000,
    "regulatory": 1960,
    "other_fixed": 500,
    "per_sample_revenue": 120,
    "variable_cost": 22,
    "monthly_samples": 1400,
}

# ----------------------------------------------------------------------------
# Reset logic
# ----------------------------------------------------------------------------
if "reset" not in st.session_state:
    for key, val in defaults.items():
        st.session_state[key] = val
    st.session_state["csv_file"] = None
    st.session_state["price_file"] = None
    st.session_state["selected"] = []
    st.session_state["cost_from_csv"] = 0.0
    st.session_state["reagents_from_csv"] = 0.0
    st.session_state["analyte_prices"] = {}
    st.session_state["launch_year"] = datetime.now().year
    st.session_state["company_name"] = "KELP Laboratory LLC"
    st.session_state["reset"] = False

if st.sidebar.button("🔄 Reset to defaults"):
    for key, val in defaults.items():
        st.session_state[key] = val
    st.session_state["csv_file"] = None
    st.session_state["price_file"] = None
    st.session_state["selected"] = []
    st.session_state["cost_from_csv"] = 0.0
    st.session_state["reagents_from_csv"] = 0.0
    st.session_state["analyte_prices"] = {}
    st.session_state["launch_year"] = datetime.now().year
    st.session_state["company_name"] = "KELP Laboratory LLC"
    st.session_state["reset"] = True

###############################################################################
# Sidebar – Data Uploads & Assumptions
###############################################################################
st.sidebar.title("🔧 Model Assumptions")

# 1. Operating-budget CSV upload (optional)
csv_file = st.sidebar.file_uploader(
    "Upload Operating-Budget CSV (Name, Monthly USD)", type="csv",
    key="csv_file"
)
cost_from_csv = 0.0
reagents_from_csv = 0.0
if csv_file is not None:
    df_csv = pd.read_csv(csv_file)
    if "Monthly USD" not in df_csv.columns:
        st.sidebar.error("CSV must include a 'Monthly USD' column.")
    else:
        cost_from_csv = df_csv["Monthly USD"].sum()
        mask = df_csv["Name"].str.contains("consumable|reagent|media|chem", case=False, na=False)
        reagents_from_csv = df_csv.loc[mask, "Monthly USD"].sum()
        st.sidebar.success(f"Loaded {len(df_csv)} rows • Total cost = ${cost_from_csv:,.0f}/mo")

# 2. Analyte price list CSV upload
price_df = None
analyte_prices = {}
price_file = st.sidebar.file_uploader(
    "Upload Analyte Price List CSV (Analyte, Price)", type="csv",
    key="price_file"
)
if price_file is not None:
    price_df = pd.read_csv(price_file)
    if "Analyte" not in price_df.columns or "Price" not in price_df.columns:
        st.sidebar.error("Price CSV must include 'Analyte' and 'Price' columns.")
    else:
        analyte_prices = dict(zip(price_df["Analyte"], price_df["Price"]))
        st.sidebar.success(f"Loaded {len(analyte_prices)} analytes.")

# 3. Company snapshot
company_name = st.sidebar.text_input(
    "LLC name", value=st.session_state["company_name"], key="company_name"
)
launch_year = st.sidebar.number_input(
    "Launch year", 2000, 2100, value=st.session_state["launch_year"], key="launch_year"
)

# 4. Payroll assumptions
num_director  = st.sidebar.number_input("Lab Directors",     0, 5, value=st.session_state["num_director"], key="num_director")
director_sal  = st.sidebar.number_input(
    "Director salary ($)", 50_000, 300_000, value=st.session_state["director_sal"], key="director_sal", step=5_000
)
num_scientist = st.sidebar.number_input(
    "Sr Scientists", 0, 20, value=st.session_state["num_scientist"], key="num_scientist"
)
scientist_sal = st.sidebar.number_input(
    "Scientist salary ($)", 40_000, 200_000, value=st.session_state["scientist_sal"], key="scientist_sal", step=5_000
)
num_tech      = st.sidebar.number_input("Lab Techs", 0, 20, value=st.session_state["num_tech"], key="num_tech")
tech_sal      = st.sidebar.number_input(
    "Tech salary ($)", 30_000, 120_000, value=st.session_state["tech_sal"], key="tech_sal", step=5_000
)
num_admin     = st.sidebar.number_input(
    "Admin (FTE)", 0.0, 5.0, value=st.session_state["num_admin"], key="num_admin", step=0.5
)
admin_sal     = st.sidebar.number_input(
    "Admin salary ($)", 30_000, 120_000, value=st.session_state["admin_sal"], key="admin_sal", step=5_000
)
benefit_load  = st.sidebar.slider(
    "Benefits & payroll-tax (%)", 0.0, 0.5, value=st.session_state["benefit_load"], key="benefit_load", step=0.01
)

# 5. Fixed monthly costs
lab_rent      = st.sidebar.number_input(
    "Lab rent ($)", 0, 100_000, value=st.session_state["lab_rent"], key="lab_rent", step=1_000
)
instr_lease   = st.sidebar.number_input(
    "Instrument leases ($)", 0, 50_000, value=st.session_state["instr_lease"], key="instr_lease", step=500
)
utilities     = st.sidebar.number_input(
    "Utilities (Pwr+Water) ($)", 0, 20_000, value=st.session_state["utilities"], key="utilities", step=100
)
argon_packs   = st.sidebar.number_input(
    "UHP argon packs / mo", 0, 10, value=st.session_state["argon_packs"], key="argon_packs"
)
argon_price   = st.sidebar.number_input(
    "Price per argon pack ($)", 0, 20_000, value=st.session_state["argon_price"], key="argon_price", step=100
)
service_contr = st.sidebar.number_input(
    "OEM service contracts ($)", 0, 20_000, value=st.session_state["service_contr"], key="service_contr", step=500
)
insurance     = st.sidebar.number_input(
    "Insurance (BOP+WC) ($)", 0, 20_000, value=st.session_state["insurance"], key="insurance", step=100
)
cleaning      = st.sidebar.number_input(
    "Lab cleaning ($)", 0, 10_000, value=st.session_state["cleaning"], key="cleaning", step=100
)
it_lims       = st.sidebar.number_input(
    "IT & LIMS SaaS ($)", 0, 20_000, value=st.session_state["it_lims"], key="it_lims", step=100
)
regulatory    = st.sidebar.number_input(
    "Regulatory & PT fees ($)", 0, 20_000, value=st.session_state[```
