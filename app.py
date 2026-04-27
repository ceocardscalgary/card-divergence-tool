import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Professional Page Setup
st.set_page_config(page_title="Star Divergence V2", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a "Terminal" Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Data Connection
# Replace with your 'Publish to Web' CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600)
def load_v2_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Force numeric types to prevent chart errors
        df['OPS'] = pd.to_numeric(df['OPS'], errors='coerce').fillna(0)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(1) # Avoid div by zero
        df['Divergence_Score'] = pd.to_numeric(df['Divergence_Score'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Engine Error: {e}")
        return None

df = load_v2_data()

# 3. Header & KPI Section
st.title("🛡️ Star Divergence V2: Market Intelligence")
st.caption("Sabermetric Arbitrage Engine | Verified 2026 Data")

if df is not None:
    # High-Level Metrics
    top_buy = df.sort_values(by='Divergence_Score', ascending=False).iloc[0]
    avg_ops = df['OPS'].mean()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Top Alpha Opportunity", top_buy['Name'], f"Score: {top_buy['Divergence_Score']:.2f}")
    m2.metric("Market Benchmark (OPS)", f"{avg_ops:.3f}")
    m3.metric("Engine Status", "Online", "v2.0.4 Stable")

    st.divider()

    # 4. Visual Analysis Section
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Performance vs. Valuation Matrix")
        # Creating the scatter plot
        fig = px.scatter(df, x="Price", y="OPS", text="Name", 
                         size="Divergence_Score", color="Divergence_Score",
                         color_continuous_scale="Viridis",
                         labels={"Price": "Market Price ($)", "OPS": "Season OPS"})
        
        fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Market Leaderboard")
        # Displaying a clean sorted list
        leaderboard = df[['Name', 'Status', 'Divergence_Score']].sort_values(by='Divergence_Score', ascending=False)
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)

    # 5. Full Data View
    with st.expander("🔍 View Full Technical Dataset"):
        st.dataframe(df, use_container_width=True)

    # 6. Sidebar Analysis
    st.sidebar.header("Gemini Alpha Notes")
    st.sidebar.write(f"""
        **Market Inefficiency Found:** {top_buy['Name']} is currently generating an OPS of {top_buy['OPS']:.3f} 
        at a price point of ${top_buy['Price']:.0f}. 
        
        This divergence of **{top_buy['Divergence_Score']:.2f}** represents a premium buying window 
        relative to established stars like Shohei Ohtani.
    """)
    st.sidebar.divider()
    st.sidebar.button("Manual Refresh Data")

else:
    st.warning("🔄 Connecting to Google Sheets... Ensure your CSV link is correct.")
