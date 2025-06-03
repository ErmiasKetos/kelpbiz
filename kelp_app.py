import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(
    page_title="KELP Environmental Laboratory - Financial Model",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🧪 KELP Environmental Laboratory Financial Model</h1>', unsafe_allow_html=True)

# Initialize session state with defaults
if 'initialized' not in st.session_state:
    st.session_state.update({
        # Major Equipment (Based on actual Thermo Fisher quotes)
        "icp_ms_cost": 175400,  # iCAP MSX-300 ICP-MS final price from quote
        "ic_system_cost": 48300,  # Dionex Inuvion IC System final price
        "hplc_ms_cost": 303500,  # TSQ Altis Plus LC-MS/MS final price 
        "microscopy_cost": 45000,
        "sample_prep_equipment": 60000,
        "lab_furniture": 40000,
        "other_equipment": 75000,
        
        # Equipment Financing & Leasing (Based on actual quotes)
        "lease_icp_ms": True,
        "lease_ic_system": True,  
        "lease_hplc_ms": True,
        "equipment_financing_rate": 5.5,
        "equipment_financing_years": 7,
        # Actual lease payments: ICP-MS $3,300/mo, IC $1,400/mo, LC-MS/MS $9,300/mo
        "icp_ms_lease_payment": 3300,
        "ic_system_lease_payment": 1400,
        "hplc_ms_lease_payment": 9300,
        
        # Facility 
        "lab_size_sqft": 5000,
        "monthly_rent_per_sqft": 4.50,
        
        # Staffing
        "technical_staff_count": 8,
        "admin_staff_count": 3,
        "technical_salary": 95000,
        "admin_salary": 65000,
        
        # Revenue & Operations
        "monthly_samples": 400,
        "avg_revenue_per_sample": 175,
        
        # Certifications & Compliance
        "nelap_certification_cost": 75000,
        "state_certification_costs": 35000,
        "quality_system_consultant": 25000,
        
        # Growth & Market
        "annual_growth_rate": 15.0,
        "market_penetration": 2.5,
        
        "initialized": True
    })

# Calculations
def calculate_monthly_payment(principal, annual_rate, years):
    """Calculate monthly payment for a loan given principal, annual rate, and term in years"""
    if principal <= 0:
        return 0
    monthly_rate = annual_rate / 100 / 12
    months = years * 12
    if monthly_rate == 0:
        return principal / months
    return principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)

# Sidebar Configuration
st.sidebar.title("🎛️ Configuration")

# Facility Configuration
st.sidebar.subheader("🏭 Facility (Monthly Rental)")
lab_size = st.sidebar.number_input("Laboratory Size (sq ft)", min_value=2000, max_value=20000, step=500, key="lab_size_sqft")
monthly_rent_psf = st.sidebar.number_input("Monthly Rent ($/sq ft)", min_value=1.0, max_value=8.0, step=0.25, key="monthly_rent_per_sqft")

# Major Equipment with Lease Options (Based on actual Thermo Fisher quotes)
st.sidebar.subheader("🔬 Major Equipment & Financing")
st.sidebar.write("*Equipment costs and lease payments from actual Thermo Fisher quotes*")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("**Equipment Costs**")
    icp_ms = st.number_input("ICP-MS System ($)", min_value=50000, max_value=300000, step=10000, key="icp_ms_cost")
    lease_icp = st.checkbox("Lease ICP-MS", key="lease_icp_ms")
    if lease_icp:
        icp_lease_payment = st.number_input("ICP-MS Lease ($/mo)", min_value=1000, max_value=8000, step=100, key="icp_ms_lease_payment")
    
    ic_system = st.number_input("Ion Chromatography ($)", min_value=30000, max_value=120000, step=5000, key="ic_system_cost")
    lease_ic = st.checkbox("Lease IC System", key="lease_ic_system")
    if lease_ic:
        ic_lease_payment = st.number_input("IC System Lease ($/mo)", min_value=500, max_value=3000, step=100, key="ic_system_lease_payment")
    
    hplc_ms = st.number_input("HPLC-MS System ($)", min_value=80000, max_value=500000, step=10000, key="hplc_ms_cost")
    lease_hplc = st.checkbox("Lease HPLC-MS", key="lease_hplc_ms")
    if lease_hplc:
        hplc_lease_payment = st.number_input("HPLC-MS Lease ($/mo)", min_value=3000, max_value=15000, step=500, key="hplc_ms_lease_payment")
    
    other_equipment = st.number_input("Other Equipment ($)", min_value=50000, max_value=200000, step=5000, key="other_equipment")

with col2:
    st.write("**Financing Terms**")
    financing_rate = st.slider("Purchase Financing Rate (%)", 3.0, 8.0, step=0.1, key="equipment_financing_rate")
    financing_years = st.slider("Financing Term (years)", 3, 10, key="equipment_financing_years")
    
    st.write("**Actual Lease Examples:**")
    st.info("• ICP-MS: $3,300/mo")
    st.info("• IC System: $1,400/mo") 
    st.info("• LC-MS/MS: $9,300/mo")

# Calculate total equipment costs and payments
leased_equipment = 0
purchased_equipment = 0
monthly_lease_total = 0

if lease_icp:
    leased_equipment += icp_ms
    monthly_lease_total += st.session_state.get('icp_ms_lease_payment', 3300)
else:
    purchased_equipment += icp_ms

if lease_ic:
    leased_equipment += ic_system
    monthly_lease_total += st.session_state.get('ic_system_lease_payment', 1400)
else:
    purchased_equipment += ic_system
    
if lease_hplc:
    leased_equipment += hplc_ms
    monthly_lease_total += st.session_state.get('hplc_ms_lease_payment', 9300)
else:
    purchased_equipment += hplc_ms

# Always purchased equipment
purchased_equipment += st.session_state.microscopy_cost + st.session_state.sample_prep_equipment + st.session_state.lab_furniture + other_equipment

equipment_total = leased_equipment + purchased_equipment
monthly_equipment_financing = calculate_monthly_payment(purchased_equipment * 0.8, financing_rate, financing_years)

st.sidebar.metric("Total Equipment Value", f"${equipment_total:,.0f}")
if leased_equipment > 0:
    st.sidebar.metric("Leased Equipment Value", f"${leased_equipment:,.0f}")
if purchased_equipment > 0:
    st.sidebar.metric("Purchased Equipment", f"${purchased_equipment:,.0f}")
st.sidebar.metric("Monthly Equipment Payments", f"${monthly_lease_total + monthly_equipment_financing:,.0f}")

# Monthly Operating Expenses
st.sidebar.subheader("💰 Monthly Operating Expenses")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("**Consumables & Services**")
    uhp_argon_packs = st.number_input("UHP argon packs / mo", min_value=0, max_value=10, step=1)
    argon_pack_price = st.number_input("Price per argon pack ($)", min_value=0, max_value=20000, step=100)
    oem_service_contracts = st.number_input("OEM service contracts ($)", min_value=0, max_value=20000, step=500)
    insurance_costs = st.number_input("Insurance (BOP+WC) ($)", min_value=0, max_value=20000, step=100)

with col2:
    st.write("**Operations & Compliance**")
    lab_cleaning = st.number_input("Lab cleaning ($)", min_value=0, max_value=10000, step=100)
    it_lims_saas = st.number_input("IT & LIMS SaaS ($)", min_value=0, max_value=20000, step=100)
    regulatory_pt_fees = st.number_input("Regulatory & PT fees ($)", min_value=0, max_value=20000, step=100)
    other_fixed_ga = st.number_input("Other fixed G&A ($)", min_value=0, max_value=20000, step=100)

# Calculate total argon costs
monthly_argon_cost = uhp_argon_packs * argon_pack_price

# Calculate total additional operating costs
additional_monthly_costs = (monthly_argon_cost + oem_service_contracts + insurance_costs + 
                          lab_cleaning + it_lims_saas + regulatory_pt_fees + other_fixed_ga)

st.sidebar.metric("Total Additional Monthly Costs", f"${additional_monthly_costs:,.0f}")

# Staffing Configuration  
st.sidebar.subheader("👥 Staffing")
technical_staff = st.sidebar.number_input("Technical Staff", min_value=1, max_value=20, key="technical_staff_count")
admin_staff = st.sidebar.number_input("Administrative Staff", min_value=1, max_value=10, key="admin_staff_count")
avg_technical_salary = st.sidebar.number_input("Avg Technical Salary ($)", min_value=60000, max_value=150000, step=5000, key="technical_salary")
avg_admin_salary = st.sidebar.number_input("Avg Admin Salary ($)", min_value=45000, max_value=100000, step=2500, key="admin_salary")

# Calculate total staff costs
total_annual_salaries = (technical_staff * avg_technical_salary + admin_staff * avg_admin_salary)
total_monthly_salaries = total_annual_salaries / 12

# Revenue Configuration
st.sidebar.subheader("📊 Revenue & Testing")
monthly_samples = st.sidebar.number_input("Samples per Month", min_value=50, max_value=2000, step=25, key="monthly_samples")
avg_revenue_per_sample = st.sidebar.number_input("Avg Revenue per Sample ($)", min_value=50, max_value=500, step=25, key="avg_revenue_per_sample")

monthly_revenue = monthly_samples * avg_revenue_per_sample
annual_revenue = monthly_revenue * 12

# Calculate monthly costs (after all variables are defined)
monthly_rent = lab_size * monthly_rent_psf
monthly_equipment_payments = monthly_lease_total + monthly_equipment_financing
monthly_fixed_costs = (monthly_rent + monthly_equipment_payments + total_monthly_salaries + 
                      additional_monthly_costs)

# Startup Costs (no facility buildout since renting)
equipment_down_payment = purchased_equipment * 0.2  # Only for purchased equipment
certification_costs = (st.session_state.nelap_certification_cost + 
                      st.session_state.state_certification_costs + 
                      st.session_state.quality_system_consultant)
working_capital = 180000  # 3 months operating expenses
total_startup = equipment_down_payment + certification_costs + working_capital

# ======================================
# MAIN DASHBOARD
# ======================================

# Key Metrics Overview
st.subheader("📊 Key Financial Metrics")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Monthly Revenue", f"${monthly_revenue:,.0f}", f"{monthly_samples} samples")
with col2:
    st.metric("Monthly Fixed Costs", f"${monthly_fixed_costs:,.0f}")
with col3:
    net_monthly = monthly_revenue - monthly_fixed_costs
    st.metric("Monthly Net Income", f"${net_monthly:,.0f}", 
              f"{'✅ Profitable' if net_monthly > 0 else '❌ Loss'}")
with col4:
    break_even_samples = monthly_fixed_costs / avg_revenue_per_sample if avg_revenue_per_sample > 0 else 0
    st.metric("Break-even Samples", f"{break_even_samples:,.0f}")
with col5:
    st.metric("Startup Investment", f"${total_startup:,.0f}")

# Cost Breakdown
st.subheader("💰 Monthly Cost Breakdown")
with st.expander("📋 Detailed Cost Analysis", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly Rent", f"${monthly_rent:,.0f}")
        st.metric("Equipment Payments", f"${monthly_equipment_payments:,.0f}")
    with col2:
        st.metric("Staff Salaries", f"${total_monthly_salaries:,.0f}")
        st.metric("Operating Costs", f"${additional_monthly_costs:,.0f}")
    with col3:
        st.metric("Total Monthly Fixed", f"${monthly_fixed_costs:,.0f}")
        st.metric("Daily Fixed Costs", f"${monthly_fixed_costs * 12 / 365:,.0f}")

# Equipment Investment Analysis
st.subheader("🔬 Equipment Investment Analysis")
col1, col2 = st.columns(2)

with col1:
    # Equipment cost breakdown pie chart
    equipment_data = {
        'Category': ['ICP-MS', 'IC System', 'HPLC-MS', 'Other Equipment'],
        'Cost': [icp_ms, ic_system, hplc_ms, other_equipment],
        'Lease Status': ['Leased' if lease_icp else 'Purchased',
                        'Leased' if lease_ic else 'Purchased', 
                        'Leased' if lease_hplc else 'Purchased',
                        'Purchased']
    }
    
    fig = px.pie(equipment_data, values='Cost', names='Category', 
                title="Equipment Cost Distribution",
                color='Lease Status',
                color_discrete_map={'Leased': '#ff7f0e', 'Purchased': '#1f77b4'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Monthly equipment payments
    payment_data = {
        'Equipment': [],
        'Monthly Payment': []
    }
    
    if lease_icp:
        payment_data['Equipment'].append('ICP-MS Lease')
        payment_data['Monthly Payment'].append(st.session_state.get('icp_ms_lease_payment', 3300))
    
    if lease_ic:
        payment_data['Equipment'].append('IC System Lease')
        payment_data['Monthly Payment'].append(st.session_state.get('ic_system_lease_payment', 1400))
    
    if lease_hplc:
        payment_data['Equipment'].append('HPLC-MS Lease')
        payment_data['Monthly Payment'].append(st.session_state.get('hplc_ms_lease_payment', 9300))
    
    if monthly_equipment_financing > 0:
        payment_data['Equipment'].append('Equipment Financing')
        payment_data['Monthly Payment'].append(monthly_equipment_financing)
    
    if payment_data['Equipment']:
        fig = px.bar(payment_data, x='Equipment', y='Monthly Payment',
                    title="Monthly Equipment Payments",
                    color='Monthly Payment',
                    color_continuous_scale='Blues')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Break-even Analysis
st.subheader("📈 Break-even Analysis")
sample_range = np.arange(50, 1000, 25)
revenue_scenarios = sample_range * avg_revenue_per_sample
break_even_point = monthly_fixed_costs

fig = go.Figure()
fig.add_trace(go.Scatter(x=sample_range, y=revenue_scenarios, 
                        mode='lines', name='Monthly Revenue', line=dict(color='green', width=3)))
fig.add_hline(y=break_even_point, line_dash="dash", line_color="red", 
              annotation_text=f"Break-even: ${break_even_point:,.0f}")
fig.add_vline(x=break_even_samples, line_dash="dash", line_color="orange",
              annotation_text=f"Break-even: {break_even_samples:.0f} samples")

fig.update_layout(
    title="Revenue vs Fixed Costs by Sample Volume",
    xaxis_title="Monthly Samples",
    yaxis_title="Monthly Revenue ($)",
    showlegend=True
)
st.plotly_chart(fig, use_container_width=True)

# 5-Year Financial Projection
st.subheader("📅 5-Year Financial Projection")
years = np.arange(1, 6)
annual_growth = st.sidebar.slider("Annual Growth Rate (%)", 5.0, 30.0, 15.0, 0.5)

# Project revenues and costs
projected_revenues = [annual_revenue * (1 + annual_growth/100)**(year-1) for year in years]
projected_fixed_costs = [monthly_fixed_costs * 12 * (1.05)**(year-1) for year in years]  # 5% cost inflation
projected_net_income = [rev - cost for rev, cost in zip(projected_revenues, projected_fixed_costs)]

projection_df = pd.DataFrame({
    'Year': years,
    'Revenue': projected_revenues,
    'Fixed Costs': projected_fixed_costs,
    'Net Income': projected_net_income
})

fig = go.Figure()
fig.add_trace(go.Bar(x=projection_df['Year'], y=projection_df['Revenue'], 
                    name='Revenue', marker_color='lightgreen'))
fig.add_trace(go.Bar(x=projection_df['Year'], y=projection_df['Fixed Costs'], 
                    name='Fixed Costs', marker_color='lightcoral'))
fig.add_trace(go.Scatter(x=projection_df['Year'], y=projection_df['Net Income'], 
                        mode='lines+markers', name='Net Income', 
                        line=dict(color='blue', width=3), marker=dict(size=8)))

fig.update_layout(
    title=f"5-Year Financial Projection ({annual_growth}% Annual Growth)",
    xaxis_title="Year",
    yaxis_title="Amount ($)",
    barmode='group'
)
st.plotly_chart(fig, use_container_width=True)

# Summary table
st.subheader("📋 5-Year Summary")
projection_df['Revenue'] = projection_df['Revenue'].apply(lambda x: f"${x:,.0f}")
projection_df['Fixed Costs'] = projection_df['Fixed Costs'].apply(lambda x: f"${x:,.0f}")
projection_df['Net Income'] = projection_df['Net Income'].apply(lambda x: f"${x:,.0f}")
st.dataframe(projection_df, use_container_width=True)

# Key Assumptions and Notes
with st.expander("ℹ️ About This Model"):
    st.markdown("""
    This financial model is designed specifically for environmental testing laboratories and includes:
    
    **🏗️ Startup & Infrastructure**: Lab buildout, equipment procurement, certification costs
    
    **🔬 Operations**: Staffing, consumables, maintenance, regulatory compliance
    
    **📊 Revenue Modeling**: Test-specific pricing based on market rates for PFAS, metals, microbiology, etc.
    
    **📈 Growth Projections**: Multi-year forecasts with industry-specific growth rates
    
    **💰 Break-even Analysis**: Understanding the volume needed to achieve profitability
    
    **🎯 Real Equipment Data**: Based on actual Thermo Fisher quotes:
    - ICP-MS System: $175,400 (lease: $3,300/mo)
    - IC System: $48,300 (lease: $1,400/mo) 
    - LC-MS/MS System: $303,500 (lease: $9,300/mo)
    - Total leased equipment: $14,000/month
    
    *Data based on 2025 industry research, actual equipment quotes, and Bay Area salary surveys.*
    """)

# Footer
st.markdown("---")
st.markdown("*KELP Environmental Laboratory Financial Model v2.0 - Built with Streamlit*")
