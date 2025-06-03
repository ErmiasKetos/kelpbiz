# Reset logic: only initialize non-widget keys
if "reset" not in st.session_state:
    for key, val in defaults.items():
        st.session_state[key] = val
    st.session_state["cost_from_csv"] = 0.0
    st.session_state["reagents_from_csv"] = 0.0
    st.session_state["analyte_prices"] = {}
    st.session_state["launch_year"] = datetime.now().year
    st.session_state["company_name"] = "KELP Laboratory LLC"
    st.session_state["reset"] = False

if st.sidebar.button("🔄 Reset to defaults"):
    for key, val in defaults.items():
        st.session_state[key] = val
    st.session_state["cost_from_csv"] = 0.0
    st.session_state["reagents_from_csv"] = 0.0
    st.session_state["analyte_prices"] = {}
    st.session_state["launch_year"] = datetime.now().year
    st.session_state["company_name"] = "KELP Laboratory LLC"
    st.session_state["reset"] = True

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
    "Regulatory & PT fees ($)", 0, 20_000, value=st.session_state["regulatory"], key="regulatory", step=100
)
other_fixed   = st.sidebar.number_input(
    "Other fixed G&A ($)", 0, 20_000, value=st.session_state["other_fixed"], key="other_fixed", step=100
)

# 6. Per-sample analyte selection
if analyte_prices:
    selected = st.sidebar.multiselect("Select analytes per sample", list(analyte_prices.keys()), key="selected")
    per_sample_revenue = sum(analyte_prices[a] for a in selected)
    st.sidebar.metric("Revenue / sample based on selection", f"${per_sample_revenue:,.2f}")
else:
    selected = []
    per_sample_revenue = st.sidebar.number_input("Average revenue / sample ($)", 0, 1_000, value=st.session_state["per_sample_revenue"], key="per_sample_revenue", step=5)

# 7. Per-sample variable cost
var_hint = 22 if reagents_from_csv == 0 else round(reagents_from_csv / (st.session_state["monthly_samples"] or 1), 2)
variable_cost = st.sidebar.number_input("Variable cost / sample ($)", 0, 500, value=var_hint, key="variable_cost", step=1)

# 8. Throughput selector
monthly_samples = st.sidebar.number_input("Expected samples / month", 0, 10_000, value=st.session_state["monthly_samples"], key="monthly_samples", step=50)

###############################################################################
# Derived Financials
###############################################################################
# Payroll total
annual_payroll = (
    st.session_state["num_director"]  * st.session_state["director_sal"] +
    st.session_state["num_scientist"] * st.session_state["scientist_sal"] +
    st.session_state["num_tech"]      * st.session_state["tech_sal"] +
    st.session_state["num_admin"]     * st.session_state["admin_sal"]
)
monthly_payroll = annual_payroll * (1 + st.session_state["benefit_load"]) / 12

# Manual fixed cost sum
manual_fixed = (
    monthly_payroll + st.session_state["lab_rent"] + st.session_state["instr_lease"] + st.session_state["utilities"] +
    st.session_state["argon_packs"] * st.session_state["argon_price"] + st.session_state["service_contr"] + st.session_state["insurance"] +
    st.session_state["cleaning"] + st.session_state["it_lims"] + st.session_state["regulatory"] + st.session_state["other_fixed"]
)

# Override fixed if CSV provided
monthly_fixed = cost_from_csv if csv_file is not None else manual_fixed

# Break-even & profit
time_margin = per_sample_revenue - st.session_state["variable_cost"]
break_even   = np.inf if time_margin <= 0 else monthly_fixed / time_margin
revenue      = monthly_samples * per_sample_revenue
variable_tot = monthly_samples * st.session_state["variable_cost"]
monthly_profit = revenue - variable_tot - monthly_fixed

###############################################################################
# Main UI – KPIs
###############################################################################
st.title("🧪 KELP Lab Financial Simulator")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Fixed Burn", f"${monthly_fixed:,.0f}")
col2.metric("Contribution Margin / sample", f"${time_margin:,.2f}")
col3.metric("Break-even samples / mo", f"{break_even:,.0f}")
col4.metric(f"Profit @ {monthly_samples} samples", f"${monthly_profit:,.0f}")

with st.expander("ℹ️ Legend & Notes"):
    st.markdown("""
* **Monthly Fixed Burn** – costs independent of volume (payroll, rent, leases, insurance, etc.).
* **Variable Cost / sample** – direct, sample-specific costs (e.g., consumables, gases, reagents, QC duplicates, waste fees). It is estimated by totaling those item costs for a standard mix of analyses divided by sample count.
* **Contribution Margin** – incremental profit per sample (revenue minus variable cost).
* **Break-even samples / mo** – sample volume at which total contribution margin equals fixed burn.
* **Analyte Selection** – when an analyte price list is uploaded, choose analytes; revenue/sample = sum of selected analyte prices.
* **Summary Recommendation** – Typical per-sample revenue ranges from **$100 to $250**. Lower-end clients order basic tests (IC + a few metals + microbiology), higher-end clients include PFAS or large panels, pushing revenue to $300–$500. Use the analyte selection tool to calculate an exact average.
""")

st.markdown("---")

###############################################################################
# Profit vs. Throughput Chart
###############################################################################
st.subheader("📈 Profit vs. Throughput")
max_plot = st.slider("Plot up to (samples/mo)", 0, 5_000, 2_500, 100)
arr = np.arange(0, max_plot + 1, 100)
profit_curve = (per_sample_revenue - st.session_state["variable_cost"]) * arr - monthly_fixed
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
st.caption("🟥 Red dashed line = break-even volume")

###############################################################################
# Five-Year Projection
###############################################################################
with st.expander("📊 Five-Year Projection"):
    g_col, p_col, i_col = st.columns(3)
    growth    = g_col.slider("Annual sample growth (%)", 0, 100, 20)
    price_inc = p_col.slider("Annual price increase (%)", 0, 20, 3)
    inflate   = i_col.slider("Fixed-cost inflation (%)", 0, 20, 4)

    years = np.arange(0, 5)
    vols  = monthly_samples * (1 + growth/100) ** years
    revs  = vols * per_sample_revenue * (1 + price_inc/100) ** years
    vars  = vols * st.session_state["variable_cost"] * (1 + inflate/100) ** years
    fixed = monthly_fixed * (1 + inflate/100) ** years
    ebitda = revs - vars - fixed

    proj_df = pd.DataFrame({
        "Year": launch_year + years,
        "Samples / yr": vols * 12,
        "Revenue": revs,
        "Variable Cost": vars,
        "Fixed Cost": fixed * 12,
        "EBITDA": ebitda * 12,
    })

    st.dataframe(proj_df.style.format({
        "Samples / yr": "{:,.0f}",
        "Revenue": "${:,.0f}",
        "Variable Cost": "${:,.0f}",
        "Fixed Cost": "${:,.0f}",
        "EBITDA": "${:,.0f}"
    }), use_container_width=True)

    bar = (
        alt.Chart(proj_df).mark_bar(size=40).encode(
            x=alt.X("Year:O", title="Fiscal Year"),
            y=alt.Y("EBITDA", title="Annual EBITDA"),
            color=alt.condition(alt.datum.EBITDA > 0, alt.value("#4caf50"), alt.value("#e53935"))
        ).properties(height=300)
    )
    st.altair_chart(bar, use_container_width=True)
    st.caption("Green = positive EBITDA; Red = negative.")

###############################################################################
# Footer
###############################################################################
st.markdown("---")
st.markdown(
    "*This interactive model is for planning purposes only. Validate all inputs against actual quotes, contracts, and market data before making financial decisions.*"
)
