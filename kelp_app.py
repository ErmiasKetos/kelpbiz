"""
KELP Environmental Laboratory - Comprehensive Financial Model

A complete Streamlit application for modeling all aspects of running an environmental 
testing laboratory, including startup costs, operations, regulatory compliance, 
equipment requirements, and multi-year financial projections.

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
    page_title="KELP Environmental Lab Financial Model",
    page_icon="🧪",
    layout="wide",
)

# Comprehensive default values based on research
defaults = {
    # Company Info
    "company_name": "KELP Environmental Laboratory LLC",
    "launch_year": datetime.now().year,
    "location": "California",
    
    # Facility & Infrastructure (Based on lab fit-out costs $771-$986 psf)
    "lab_size_sqft": 5000,
    "lab_fitout_cost_per_sqft": 850,
    "monthly_rent_per_sqft": 3.50,
    "utilities_monthly": 8000,
    "lab_cleaning": 2500,
    "waste_disposal": 4000,
    
    # Major Equipment (Based on ICP-MS $50k-$250k, other equipment)
    "icp_ms_cost": 180000,
    "gc_ms_cost": 120000,
    "hplc_cost": 80000,
    "microscopy_cost": 45000,
    "sample_prep_equipment": 60000,
    "lab_furniture": 40000,
    "other_equipment": 85000,
    
    # Equipment Financing & Maintenance
    "equipment_financing_rate": 5.5,
    "equipment_financing_years": 7,
    "annual_maintenance_percent": 12,
    "equipment_replacement_reserve": 8,
    
    # Staffing (Research-based salaries)
    "laboratory_director": 1,
    "director_salary": 150000,
    "senior_scientists": 2,
    "scientist_salary": 85000,
    "lab_technicians": 4,
    "technician_salary": 55000,
    "quality_manager": 1,
    "qa_manager_salary": 95000,
    "admin_staff": 1.5,
    "admin_salary": 48000,
    "benefits_percent": 28,
    
    # Certification & Compliance
    "nelap_certification_cost": 15000,
    "annual_nelap_renewal": 8000,
    "state_certification_costs": 12000,
    "proficiency_testing_annual": 25000,
    "quality_system_consultant": 18000,
    
    # Laboratory Consumables & Operations
    "reagents_monthly": 12000,
    "reference_standards": 8000,
    "gases_monthly": 3500,
    "labware_consumables": 6000,
    "maintenance_contracts": 15000,
    
    # IT & Data Management
    "lims_system_annual": 24000,
    "it_infrastructure": 8000,
    "data_backup_security": 3600,
    "software_licenses": 12000,
    
    # Insurance & Legal
    "general_liability": 4500,
    "professional_liability": 6000,
    "property_insurance": 3200,
    "workers_comp": 8500,
    "legal_regulatory": 12000,
    
    # Testing Pricing (Market research-based)
    "pfas_test_price": 450,
    "metals_analysis_price": 180,
    "microbiology_price": 85,
    "voc_analysis_price": 220,
    "general_chemistry_price": 120,
    "specialty_testing_price": 350,
    
    # Sample Volume & Mix
    "monthly_samples": 800,
    "pfas_percent": 15,
    "metals_percent": 35,
    "microbiology_percent": 25,
    "voc_percent": 15,
    "general_chem_percent": 8,
    "specialty_percent": 2,
    
    # Variable Costs per Sample Type
    "pfas_variable_cost": 75,
    "metals_variable_cost": 25,
    "microbiology_variable_cost": 15,
    "voc_variable_cost": 35,
    "general_chem_variable_cost": 18,
    "specialty_variable_cost": 65,
}

# Initialize session state
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Title and Introduction
st.title("🧪 KELP Environmental Laboratory")
st.subheader("Comprehensive Financial Model for Environmental Testing Operations")

with st.expander("ℹ️ About This Model"):
    st.markdown("""
    This financial model is designed specifically for environmental testing laboratories and includes:
    
    **🏗️ Startup & Infrastructure**: Lab buildout, equipment procurement, certification costs
    
    **🔬 Operations**: Staffing, consumables, maintenance, regulatory compliance
    
    **📊 Revenue Modeling**: Test-specific pricing based on market rates for PFAS, metals, microbiology, etc.
    
    **📈 Growth Projections**: Multi-year forecasts with industry-specific growth rates
    
    **💰 Break-even Analysis**: Understanding the volume needed to achieve profitability
    
    *Data based on 2025 industry research including equipment costs, salary surveys, and market pricing.*
    """)

# Sidebar Configuration
st.sidebar.header("🔧 Laboratory Configuration")

# Reset button
if st.sidebar.button("🔄 Reset to Defaults", type="secondary"):
    for key, value in defaults.items():
        st.session_state[key] = value
    st.rerun()

# Company Information
st.sidebar.subheader("🏢 Company Information")
company_name = st.sidebar.text_input("Laboratory Name", key="company_name")
launch_year = st.sidebar.number_input("Launch Year", min_value=2020, max_value=2030, key="launch_year")
location = st.sidebar.selectbox("Primary Location", 
    ["California", "Texas", "Florida", "New York", "Illinois", "Pennsylvania", "Other"], 
    key="location")

# Facility Configuration
st.sidebar.subheader("🏭 Facility & Infrastructure")
lab_size = st.sidebar.number_input("Laboratory Size (sq ft)", min_value=2000, max_value=20000, step=500, key="lab_size_sqft")
fitout_cost = st.sidebar.number_input("Lab Fit-out Cost ($/sq ft)", min_value=500, max_value=1500, step=25, key="lab_fitout_cost_per_sqft")
monthly_rent_psf = st.sidebar.number_input("Monthly Rent ($/sq ft)", min_value=1.0, max_value=8.0, step=0.25, key="monthly_rent_per_sqft")

# Major Equipment
st.sidebar.subheader("🔬 Major Equipment Costs")
icp_ms = st.sidebar.number_input("ICP-MS System ($)", min_value=50000, max_value=300000, step=10000, key="icp_ms_cost")
gc_ms = st.sidebar.number_input("GC-MS System ($)", min_value=60000, max_value=200000, step=5000, key="gc_ms_cost")
hplc = st.sidebar.number_input("HPLC System ($)", min_value=40000, max_value=150000, step=5000, key="hplc_cost")
other_equipment = st.sidebar.number_input("Other Equipment ($)", min_value=50000, max_value=200000, step=5000, key="other_equipment")

# Equipment Financing
equipment_total = icp_ms + gc_ms + hplc + st.session_state.microscopy_cost + st.session_state.sample_prep_equipment + st.session_state.lab_furniture + other_equipment
st.sidebar.metric("Total Equipment Cost", f"${equipment_total:,.0f}")

financing_rate = st.sidebar.slider("Equipment Financing Rate (%)", 3.0, 8.0, step=0.1, key="equipment_financing_rate")
financing_years = st.sidebar.slider("Financing Term (years)", 3, 10, key="equipment_financing_years")

# Staffing
st.sidebar.subheader("👥 Staffing Plan")
director_count = st.sidebar.number_input("Laboratory Director", min_value=0, max_value=2, key="laboratory_director")
director_sal = st.sidebar.number_input("Director Salary ($)", min_value=100000, max_value=250000, step=5000, key="director_salary")

scientist_count = st.sidebar.number_input("Senior Scientists", min_value=0, max_value=10, key="senior_scientists")
scientist_sal = st.sidebar.number_input("Scientist Salary ($)", min_value=60000, max_value=150000, step=2500, key="scientist_salary")

tech_count = st.sidebar.number_input("Lab Technicians", min_value=0, max_value=15, key="lab_technicians")
tech_sal = st.sidebar.number_input("Technician Salary ($)", min_value=35000, max_value=80000, step=2500, key="technician_salary")

qa_count = st.sidebar.number_input("QA/QC Manager", min_value=0, max_value=2, key="quality_manager")
qa_sal = st.sidebar.number_input("QA Manager Salary ($)", min_value=70000, max_value=150000, step=2500, key="qa_manager_salary")

admin_count = st.sidebar.number_input("Admin Staff (FTE)", min_value=0.0, max_value=5.0, step=0.5, key="admin_staff")
admin_sal = st.sidebar.number_input("Admin Salary ($)", min_value=35000, max_value=80000, step=2500, key="admin_salary")

benefits_pct = st.sidebar.slider("Benefits & Payroll Tax (%)", 20, 40, key="benefits_percent")

# Test Portfolio & Pricing
st.sidebar.subheader("🧪 Test Portfolio & Pricing")
monthly_samples = st.sidebar.number_input("Monthly Sample Volume", min_value=100, max_value=5000, step=50, key="monthly_samples")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("**Test Mix (%)**")
    pfas_pct = st.number_input("PFAS", min_value=0, max_value=100, key="pfas_percent")
    metals_pct = st.number_input("Metals", min_value=0, max_value=100, key="metals_percent")
    micro_pct = st.number_input("Microbiology", min_value=0, max_value=100, key="microbiology_percent")

with col2:
    st.write("**Pricing ($)**")
    pfas_price = st.number_input("PFAS Price", min_value=200, max_value=800, step=25, key="pfas_test_price")
    metals_price = st.number_input("Metals Price", min_value=50, max_value=400, step=10, key="metals_analysis_price")
    micro_price = st.number_input("Micro Price", min_value=30, max_value=200, step=5, key="microbiology_price")

# Calculations
def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 100 / 12
    months = years * 12
    if monthly_rate == 0:
        return principal / months
    return principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)

# Startup Costs
initial_fitout = lab_size * fitout_cost
equipment_down_payment = equipment_total * 0.2
certification_costs = (st.session_state.nelap_certification_cost + 
                      st.session_state.state_certification_costs + 
                      st.session_state.quality_system_consultant)
working_capital = 180000  # 3 months operating expenses
total_startup = initial_fitout + equipment_down_payment + certification_costs + working_capital

# Monthly Fixed Costs
monthly_rent = lab_size * monthly_rent_psf
equipment_payment = calculate_monthly_payment(equipment_total * 0.8, financing_rate, financing_years)

annual_payroll = (director_count * director_sal + 
                 scientist_count * scientist_sal + 
                 tech_count * tech_sal + 
                 qa_count * qa_sal + 
                 admin_count * admin_sal)
monthly_payroll = annual_payroll * (1 + benefits_pct/100) / 12

monthly_fixed = (monthly_rent + 
                equipment_payment +
                monthly_payroll +
                st.session_state.utilities_monthly +
                st.session_state.lab_cleaning +
                st.session_state.waste_disposal +
                st.session_state.reagents_monthly +
                st.session_state.gases_monthly +
                st.session_state.labware_consumables +
                st.session_state.maintenance_contracts +
                st.session_state.lims_system_annual/12 +
                st.session_state.it_infrastructure/12 +
                (st.session_state.general_liability + st.session_state.professional_liability + 
                 st.session_state.property_insurance + st.session_state.workers_comp)/12 +
                st.session_state.annual_nelap_renewal/12)

# Revenue and Variable Cost Calculations
test_mix = {
    'PFAS': pfas_pct/100,
    'Metals': metals_pct/100,
    'Microbiology': micro_pct/100,
    'VOCs': st.session_state.voc_percent/100,
    'General Chemistry': st.session_state.general_chem_percent/100,
    'Specialty': st.session_state.specialty_percent/100
}

test_prices = {
    'PFAS': pfas_price,
    'Metals': metals_price,
    'Microbiology': micro_price,
    'VOCs': st.session_state.voc_analysis_price,
    'General Chemistry': st.session_state.general_chemistry_price,
    'Specialty': st.session_state.specialty_testing_price
}

test_variable_costs = {
    'PFAS': st.session_state.pfas_variable_cost,
    'Metals': st.session_state.metals_variable_cost,
    'Microbiology': st.session_state.microbiology_variable_cost,
    'VOCs': st.session_state.voc_variable_cost,
    'General Chemistry': st.session_state.general_chem_variable_cost,
    'Specialty': st.session_state.specialty_variable_cost
}

# Calculate weighted averages
avg_revenue_per_sample = sum(test_mix[test] * test_prices[test] for test in test_mix)
avg_variable_cost_per_sample = sum(test_mix[test] * test_variable_costs[test] for test in test_mix)

monthly_revenue = monthly_samples * avg_revenue_per_sample
monthly_variable_costs = monthly_samples * avg_variable_cost_per_sample
contribution_margin = avg_revenue_per_sample - avg_variable_cost_per_sample

# Break-even calculation
if contribution_margin > 0:
    break_even_samples = monthly_fixed / contribution_margin
else:
    break_even_samples = float('inf')

monthly_ebitda = monthly_revenue - monthly_variable_costs - monthly_fixed

# Main Dashboard
st.header("📊 Financial Dashboard")

# Top-level metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Startup Investment", f"${total_startup:,.0f}")
    
with col2:
    st.metric("Monthly Fixed Costs", f"${monthly_fixed:,.0f}")
    
with col3:
    st.metric("Break-even Volume", f"{break_even_samples:,.0f} samples/mo" if break_even_samples != float('inf') else "∞")
    
with col4:
    color = "normal" if monthly_ebitda >= 0 else "inverse"
    st.metric("Monthly EBITDA", f"${monthly_ebitda:,.0f}", delta_color=color)

# Test Portfolio Analysis
st.subheader("🧪 Test Portfolio Analysis")

portfolio_data = []
for test_type in test_mix:
    samples = monthly_samples * test_mix[test_type]
    revenue = samples * test_prices[test_type]
    variable_cost = samples * test_variable_costs[test_type]
    contribution = revenue - variable_cost
    
    portfolio_data.append({
        'Test Type': test_type,
        'Volume': f"{samples:,.0f}",
        'Revenue': f"${revenue:,.0f}",
        'Variable Cost': f"${variable_cost:,.0f}",
        'Contribution': f"${contribution:,.0f}",
        'Margin %': f"{(contribution/revenue*100):,.1f}%" if revenue > 0 else "0%"
    })

portfolio_df = pd.DataFrame(portfolio_data)
st.dataframe(portfolio_df, use_container_width=True)

# Revenue Chart
chart_data = pd.DataFrame({
    'Test Type': list(test_mix.keys()),
    'Monthly Revenue': [monthly_samples * test_mix[test] * test_prices[test] for test in test_mix]
})

chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('Test Type:N', sort='-y'),
    y=alt.Y('Monthly Revenue:Q', title='Monthly Revenue ($)'),
    color=alt.Color('Test Type:N', scale=alt.Scale(scheme='category10')),
    tooltip=['Test Type:N', alt.Tooltip('Monthly Revenue:Q', format='$,.0f')]
).properties(
    height=300,
    title='Revenue by Test Type'
)

st.altair_chart(chart, use_container_width=True)

# Profit vs Volume Analysis
st.subheader("📈 Profit vs Volume Analysis")

max_samples = st.slider("Maximum samples for analysis", 500, 3000, 2000, 100)
sample_range = np.arange(0, max_samples + 1, 50)
profit_data = []

for samples in sample_range:
    revenue = samples * avg_revenue_per_sample
    variable = samples * avg_variable_cost_per_sample
    profit = revenue - variable - monthly_fixed
    profit_data.append({'Samples': samples, 'Monthly Profit': profit})

profit_df = pd.DataFrame(profit_data)

line_chart = alt.Chart(profit_df).mark_line(size=3, color='blue').encode(
    x=alt.X('Samples:Q', title='Monthly Sample Volume'),
    y=alt.Y('Monthly Profit:Q', title='Monthly Profit ($)', scale=alt.Scale(zero=False)),
    tooltip=[alt.Tooltip('Samples:Q'), alt.Tooltip('Monthly Profit:Q', format='$,.0f')]
)

break_even_line = alt.Chart(pd.DataFrame({'x': [break_even_samples]})).mark_rule(
    strokeDash=[5,5], 
    color='red', 
    size=2
).encode(x='x:Q') if break_even_samples != float('inf') and break_even_samples <= max_samples else alt.Chart()

zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='gray').encode(y='y:Q')

combined_chart = line_chart + break_even_line + zero_line
st.altair_chart(combined_chart, use_container_width=True)
st.caption("🟥 Red dashed line = break-even volume")

# Five-Year Projections
with st.expander("📊 Five-Year Financial Projections"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sample_growth = st.slider("Annual Sample Growth (%)", 0, 50, 15)
    with col2:
        price_growth = st.slider("Annual Price Increase (%)", 0, 15, 4)
    with col3:
        cost_inflation = st.slider("Cost Inflation (%)", 0, 15, 5)
    
    years = np.arange(0, 5)
    projection_data = []
    
    for year in years:
        year_samples = monthly_samples * (1 + sample_growth/100) ** year * 12
        year_revenue = year_samples * avg_revenue_per_sample * (1 + price_growth/100) ** year
        year_variable = year_samples * avg_variable_cost_per_sample * (1 + cost_inflation/100) ** year
        year_fixed = monthly_fixed * 12 * (1 + cost_inflation/100) ** year
        year_ebitda = year_revenue - year_variable - year_fixed
        
        projection_data.append({
            'Year': launch_year + year,
            'Samples': f"{year_samples:,.0f}",
            'Revenue': f"${year_revenue:,.0f}",
            'Variable Costs': f"${year_variable:,.0f}",
            'Fixed Costs': f"${year_fixed:,.0f}",
            'EBITDA': f"${year_ebitda:,.0f}",
            'EBITDA Margin': f"{(year_ebitda/year_revenue*100):,.1f}%" if year_revenue > 0 else "0%"
        })
    
    proj_df = pd.DataFrame(projection_data)
    st.dataframe(proj_df, use_container_width=True)

# Cost Breakdown
st.subheader("💰 Monthly Cost Breakdown")

cost_categories = {
    'Payroll & Benefits': monthly_payroll,
    'Facility Rent': monthly_rent,
    'Equipment Financing': equipment_payment,
    'Utilities & Cleaning': st.session_state.utilities_monthly + st.session_state.lab_cleaning,
    'Consumables & Reagents': st.session_state.reagents_monthly + st.session_state.labware_consumables,
    'Maintenance & Service': st.session_state.maintenance_contracts,
    'IT & Software': (st.session_state.lims_system_annual + st.session_state.it_infrastructure)/12,
    'Insurance & Legal': (st.session_state.general_liability + st.session_state.professional_liability + 
                         st.session_state.property_insurance + st.session_state.workers_comp)/12,
    'Certification & QA': st.session_state.annual_nelap_renewal/12,
    'Other Operations': st.session_state.waste_disposal + st.session_state.gases_monthly
}

cost_df = pd.DataFrame(list(cost_categories.items()), columns=['Category', 'Monthly Cost'])
cost_df['Percentage'] = (cost_df['Monthly Cost'] / cost_df['Monthly Cost'].sum() * 100).round(1)

pie_chart = alt.Chart(cost_df).mark_arc().encode(
    theta='Monthly Cost:Q',
    color=alt.Color('Category:N', scale=alt.Scale(scheme='category20')),
    tooltip=['Category:N', alt.Tooltip('Monthly Cost:Q', format='$,.0f'), 'Percentage:Q']
).properties(
    height=400,
    title='Monthly Fixed Cost Breakdown'
)

st.altair_chart(pie_chart, use_container_width=True)

# Key Insights and Recommendations
st.subheader("💡 Key Insights & Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**💰 Financial Health**")
    if monthly_ebitda > 0:
        st.success(f"✅ Profitable at current volume ({monthly_samples:,} samples/mo)")
    else:
        st.warning(f"⚠️ Need {break_even_samples:,.0f} samples/mo to break even")
    
    margin_pct = (monthly_ebitda / monthly_revenue * 100) if monthly_revenue > 0 else 0
    if margin_pct > 15:
        st.success(f"✅ Strong EBITDA margin: {margin_pct:.1f}%")
    elif margin_pct > 5:
        st.info(f"📊 Moderate EBITDA margin: {margin_pct:.1f}%")
    else:
        st.error(f"❌ Low/negative EBITDA margin: {margin_pct:.1f}%")

with col2:
    st.markdown("**🎯 Optimization Opportunities**")
    
    # Find highest margin test
    test_margins = {test: (test_prices[test] - test_variable_costs[test])/test_prices[test] 
                   for test in test_prices}
    best_test = max(test_margins, key=test_margins.get)
    
    st.info(f"🔬 Focus on {best_test} testing (highest margin: {test_margins[best_test]*100:.1f}%)")
    
    if monthly_payroll / monthly_fixed > 0.6:
        st.warning("👥 Payroll >60% of fixed costs - consider efficiency gains")
    
    if avg_revenue_per_sample < 200:
        st.info("💰 Consider premium testing services to increase revenue/sample")

# Footer
st.markdown("---")
st.markdown("""
*This model is based on 2025 industry research and should be used for planning purposes only. 
Validate all assumptions with current market data, equipment vendors, and regulatory requirements 
before making business decisions.*

**Key Sources**: Environmental testing market data, 
salary surveys, and lab construction costs.
""")
