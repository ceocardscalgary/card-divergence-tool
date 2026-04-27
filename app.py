import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Terminal Styling & Page Config
st.set_page_config(page_title="Alpha Terminal V3.1", layout="wide")

# Custom CSS for a professional "Fintech" Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] { 
        background-color: white; padding: 20px; border-radius: 12px; 
        border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    .stProgress > div > div > div > div { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Data Sync
# REPLACE the link below with your actual 'Publish to Web' CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=300)
def load_terminal_data():
    try:
        # skipinitialspace handles accidental spaces in Google Sheet headers
        df = pd.read_csv(SHEET_URL, skipinitialspace=True)
        
        # FIX: Handle potential truncation from Google Sheets 'Divergence_Sco'
        if 'Divergence_Sco' in df.columns and 'Divergence_Score' not in df.columns:
            df = df.rename(columns={'Divergence_Sco': 'Divergence_Score'})
            
        # Ensure all core columns are numeric to prevent 0.00 display errors
        numeric_cols = ['OPS', 'Price', 'Divergence_Score', 'CL_Value', 'CL_Premium', 'Alpha_Rank']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return None

df = load_terminal_data()

# 3. Decision Logic & Header
st.title("🛡️ Star Divergence V3: The Alpha Terminal")
st.caption(f"Proprietary Market Intelligence | Last Sync: April 26, 2026")

if df is not None:
    # Verify that the critical Alpha_Rank column exists
    if 'Alpha_Rank' in df.columns:
        
        # --- TOP LEVEL KPIs ---
        # Sorting to find the top buy signal
        top_asset = df.sort_values(by='Alpha_Rank', ascending=False).iloc[0]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Highest Alpha Signal", top_asset['Name'], f"{top_asset['Alpha_Rank']:.2f}")
        m2.metric("Market Premium Avg", f"{df['CL_Premium'].mean():.2f}x")
        m3.metric("Peak Divergence", f"{df['Divergence_Score'].max():.2f}")
        m4.metric("Asset Coverage", len(df), "Active Stars")

        # --- OPPORTUNITY MATRIX (Bubble Chart) ---
        st.divider()
        col_chart, col_leader = st.columns([2, 1])
        
        with col_chart:
            st.subheader("📍 The Alpha Matrix")
            st.info("💡 Top-Left Quadrant: High Performance (Divergence) vs Low Market Hype (Premium).")
            
            fig = px.scatter(df, x="CL_Premium", y="Divergence_Score",
                             size="Alpha_Rank", color="Alpha_Rank",
                             hover_name="Name", text="Name",
                             color_continuous_scale="RdYlGn",
                             labels={
                                 "CL_Premium": "Hype Factor (Market Price / Card Ladder)", 
                                 "Divergence_Score": "Performance Gap (OPS vs Price)"
                             })
            
            fig.update_traces(textposition='top center')
            fig.add_hline(y=df['Divergence_Score'].mean(), line_dash="dot", annotation_text="Avg Performance")
            st.plotly_chart(fig, use_container_width=True)

        with col_leader:
            st.subheader("🏆 Market Leaderboard")
            # Pulling the status and rank from your sheet
            leaderboard_cols = ['Name', 'Alpha_Rank']
            if 'Status' in df.columns:
                leaderboard_cols.append('Status')
                
            st.dataframe(df[leaderboard_cols].sort_values(by='Alpha_Rank', ascending=False), 
                         hide_index=True, use_container_width=True)

        # --- HEAD-TO-HEAD BATTLE ---
        st.divider()
        st.subheader("⚔️ Star Battle: Head-to-Head Comparison")
        star_options = df['Name'].tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            p1 = st.selectbox("Select Player A", star_options, index=0)
            p1_data = df[df['Name'] == p1].iloc[0]
            st.metric(f"{p1} Alpha Score", f"{p1_data['Alpha_Rank']:.2f}")
            # Visual progress bar (capped at 2.0 for scale)
            st.progress(min(float(p1_data['Alpha_Rank']) / 2.0, 1.0))
            
        with c2:
            # Default to index 1 if it exists, otherwise 0
            default_p2 = 1 if len(star_options) > 1 else 0
            p2 = st.selectbox("Select Player B", star_options, index=default_p2)
            p2_data = df[df['Name'] == p2].iloc[0]
            st.metric(f"{p2} Alpha Score", f"{p2_data['Alpha_Rank']:.2f}")
            st.progress(min(float(p2_data['Alpha_Rank']) / 2.0, 1.0))

        # --- FULL TECHNICAL DATA ---
        with st.expander("📊 View Raw Market Data"):
            st.dataframe(df, use_container_width=True, hide_index=True)

        # --- SIDEBAR INSIGHTS ---
        st.sidebar.header("Terminal Insights")
        st.sidebar.success(f"**Top Value Asset:** {top_asset['Name']}")
        st.sidebar.write(f"Currently trading at a {top_asset['CL_Premium']:.2f}x premium relative to Card Ladder, while maintaining a Divergence of {top_asset['Divergence_Score']:.2f}.")
        st.sidebar.divider()
        st.sidebar.info("Methodology: Alpha Rank = Divergence / Card Ladder Premium. Identifying where production outpaces hype.")

    else:
        st.error("⚠️ Column Name Mismatch")
        st.write("Ensure your Google Sheet headers are: Name, OPS, Price, Divergence_Score, CL_Value, CL_Premium, Alpha_Rank")
        st.info("Current Columns Found: " + ", ".join(df.columns))

else:
    st.warning("🔄 Waiting for Data Engine... verify your 'Publish to Web' link in Google Sheets.")
