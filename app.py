import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Fintech Styling
st.set_page_config(page_title="Star Divergence V3", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 15px; border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Data Sync
# ENSURE THIS LINK HAS gid=0 (or the GID of your Dashboard tab)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=300)
def load_v3_data():
    try:
        df = pd.read_csv(SHEET_URL)
        numeric_cols = ['OPS', 'Price', 'Divergence_Score', 'CL_Value', 'CL_Premium', 'Alpha_Rank']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except:
        return None

df = load_v3_data()

# 3. V3 Dashboard Interface
st.title("🛡️ Star Divergence V3: The Alpha Terminal")
st.caption("Advanced Sabermetric Arbitrage | Card Ladder Benchmark Integrated")

if df is not None:
    # Top Level KPI Row
    top_alpha = df.sort_values(by='Alpha_Rank', ascending=False).iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Top Alpha Buy", top_alpha['Name'], f"Rank: {top_alpha['Alpha_Rank']:.2f}")
    m2.metric("Market Premium Avg", f"{df['CL_Premium'].mean():.2f}x")
    m3.metric("Max Divergence", f"{df['Divergence_Score'].max():.2f}")
    m4.metric("Asset Coverage", len(df), "Active Stars")

    # 4. The Decision Matrix (Bubble Chart)
    st.divider()
    st.subheader("📍 Asset Opportunity Matrix")
    st.info("Top-Left Quadrant = High Performance, Low Market Premium (The Alpha Zone)")
    
    fig = px.scatter(df, x="CL_Premium", y="Divergence_Score",
                     size="Alpha_Rank", color="Name",
                     hover_data=['Price', 'OPS'],
                     labels={"CL_Premium": "Market Premium (Price / Card Ladder)", 
                             "Divergence_Score": "Performance Divergence (OPS vs Price)"})
    st.plotly_chart(fig, use_container_width=True)

    # 5. Star Comparison Battle
    st.divider()
    st.subheader("⚔️ Star Battle: Head-to-Head Comparison")
    star_options = df['Name'].tolist()
    col_a, col_b = st.columns(2)
    
    with col_a:
        p1 = st.selectbox("Select Player 1", star_options, index=0)
        p1_data = df[df['Name'] == p1].iloc[0]
        st.write(f"**{p1} Alpha Rank:** {p1_data['Alpha_Rank']:.2f}")
        st.progress(min(p1_data['Alpha_Rank']/2, 1.0)) # Visual scale
        
    with col_b:
        p2 = st.selectbox("Select Player 2", star_options, index=1)
        p2_data = df[df['Name'] == p2].iloc[0]
        st.write(f"**{p2} Alpha Rank:** {p2_data['Alpha_Rank']:.2f}")
        st.progress(min(p2_data['Alpha_Rank']/2, 1.0))

    # 6. Technical Data Table
    with st.expander("📊 View Detailed Market Logs"):
        st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Connection Error. Ensure your Google Sheet is published and the URL is correct.")
