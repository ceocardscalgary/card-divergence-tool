import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Terminal Styling & Page Config
st.set_page_config(page_title="Alpha Terminal V3.1", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] { 
        background-color: white; padding: 20px; border-radius: 12px; 
        border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Data Sync
# REPLACE WITH YOUR GOOGLE SHEET CSV LINK
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=300)
def load_terminal_data():
    try:
        # We use 'skipinitialspace' to handle accidental spaces in your Google Sheet headers
        df = pd.read_csv(SHEET_URL, skipinitialspace=True)
        # Force numeric types to prevent math errors
        numeric_cols = ['OPS', 'Price', 'Divergence_Score', 'CL_Value', 'CL_Premium', 'Alpha_Rank']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return None

df = load_terminal_data()

# 3. Decision Logic & Header
st.title("🛡️ Star Divergence V3: The Alpha Terminal")
st.caption(f"Proprietary Market Intelligence | Card Ladder Benchmark Integrated")

if df is not None:
    # CHECK IF REQUIRED COLUMNS EXIST
    required_cols = ['Alpha_Rank', 'Divergence_Score', 'CL_Premium']
    if all(col in df.columns for col in required_cols):
        
        # --- TOP LEVEL KPIs ---
        top_asset = df.sort_values(by='Alpha_Rank', ascending=False).iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Highest Alpha Signal", top_asset['Name'], f"{top_asset['Alpha_Rank']:.2f} Score")
        m2.metric("Market Premium Avg", f"{df['CL_Premium'].mean():.2f}x")
        m3.metric("Max Performance Gap", f"{df['Divergence_Score'].max():.2f}")
        m4.metric("Asset Coverage", len(df), "Active Stars")

        # --- OPPORTUNITY MATRIX (Bubble Chart) ---
        st.divider()
        col_chart, col_leader = st.columns([2, 1])
        
        with col_chart:
            st.subheader("📍 The Alpha Matrix")
            st.info("💡 Top-Left Quadrant: High Performance (Divergence) vs Low Market Hype (Premium).")
            # Size of bubble is Alpha_Rank
            fig = px.scatter(df, x="CL_Premium", y="Divergence_Score",
                             size="Alpha_Rank", color="Alpha_Rank",
                             hover_name="Name", text="Name",
                             color_continuous_scale="RdYlGn",
                             labels={"CL_Premium": "Hype Factor (Price / Card Ladder Value)", 
                                     "Divergence_Score": "Performance Gap (OPS vs Price)"})
            fig.update_traces(textposition='top center')
            fig.add_hline(y=df['Divergence_Score'].mean(), line_dash="dot", annotation_text="Avg Performance")
            st.plotly_chart(fig, use_container_width=True)

        with col_leader:
            st.subheader("🏆 Market Leaderboard")
            st.dataframe(df[['Name', 'Alpha_Rank', 'Status']].sort_values(by='Alpha_Rank', ascending=False), 
                         hide_index=True, use_container_width=True)

        # --- SIDEBAR INSIGHTS (Safe within the 'if' block) ---
        st.sidebar.header("Terminal Insights")
        st.sidebar.success(f"**Top Value Asset:** {top_asset['Name']}")
        st.sidebar.write(f"This asset is currently yielding the highest efficiency relative to the Card Ladder benchmark.")
        
        # --- HEAD-TO-HEAD BATTLE ---
        st.divider()
        st.subheader("⚔️ Star Battle: Head-to-Head Comparison")
        star_options = df['Name'].tolist()
        c1, c2 = st.columns(2)
        with c1:
            p1 = st.selectbox("Select Player A", star_options, index=0)
            p1_data = df[df['Name'] == p1].iloc[0]
            st.metric(f"{p1} Alpha", f"{p1_stats['Alpha_Rank']:.2f}" if 'p1_stats' in locals() else f"{p1_data['Alpha_Rank']:.2f}")
            st.progress(min(p1_data['Alpha_Rank'] / 2, 1.0))
        with c2:
            p2 = st.selectbox("Select Player B", star_options, index=1)
            p2_data = df[df['Name'] == p2].iloc[0]
            st.metric(f"{p2} Alpha", f"{p2_data['Alpha_Rank']:.2f}")
            st.progress(min(p2_data['Alpha_Rank'] / 2, 1.0))

    else:
        st.error(f"Missing columns in Google Sheet. Found: {list(df.columns)}")
        st.info("Ensure your Sheet has: Alpha_Rank, Divergence_Score, CL_Premium")
else:
    st.warning("🔄 Syncing with Google Sheets Master... Verify your CSV link is 'Published to Web'.")
