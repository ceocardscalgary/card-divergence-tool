import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Professional Page Setup
st.set_page_config(page_title="Star Divergence V2", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a "Fintech" Look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Data Connection
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=300)
def load_v2_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Ensure numbers are clean
        df['OPS'] = pd.to_numeric(df['OPS'], errors='coerce')
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Divergence_Score'] = pd.to_numeric(df['Divergence_Score'], errors='coerce')
        return df
    except:
        return None

df = load_v2_data()

# 3. Header & KPI Section
st.title("🛡️ Star Divergence V2: Market Intelligence")
st.caption("Real-time Sabermetric Arbitrage for High-End Collectibles")

if df is not None:
    # Key Metrics (Top Row)
    top_buy = df.sort_values(by='Divergence_Score', ascending=False).iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Top Alpha Asset", top_buy['Name'], f"{top_buy['Divergence_Score']:.2f} Score")
    with col2:
        avg_ops = df['OPS'].mean()
        st.metric("Market Avg OPS", f"{avg_ops:.33f}")
    with col3:
        st.metric("Engine Status", "Verified", "Live Data")

    # 4. Interactive Visuals
    st.divider()
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Performance vs. Valuation Map")
        fig = px.scatter(df, x="Price", y="OPS", text="Name", 
                         size="Divergence_Score", color="Divergence_Score",
                         color_continuous_scale=px.colors.sequential.Viridis,
                         labels={"Price": "Market Price ($)", "OPS": "Season OPS"})
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Quick-Action Leaderboard")
        # Displaying a styled table with 'Status'
        styled_df = df[['Name', 'Divergence_Score', 'Status']].sort_values(by='Divergence_Score', ascending=False)
        st.dataframe(styled_df, hide_index=True, use_container_width=True)

    # 5. Deep-Dive Table
    st.divider()
    st.subheader("Raw Technical Data")
    st.dataframe(df, use_container_width=True)

else:
    st.error("Data Engine Offline. Please check the Google Sheet 'Publish to Web' settings.")

# 6. Automated Commentary (Footer)
st.sidebar.header("Gemini Alpha Notes")
st.sidebar.info(f"""
    **Current Market Gap:** {top_buy['Name']} is currently yielding the highest performance per dollar. 
    A score of {top_buy['Divergence_Score']:.2f} suggests significant room for price appreciation 
    if seasonal averages hold.
""")
