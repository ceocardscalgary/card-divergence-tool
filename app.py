import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Terminal Styling
st.set_page_config(page_title="Alpha Terminal V3", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    [data-testid="stMetric"] { background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #007bff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Sync
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=300)
def load_terminal_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Ensure numeric columns are clean
        for col in ['OPS', 'Price', 'Divergence_Score', 'CL_Value', 'CL_Premium', 'Alpha_Rank']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return None

df = load_terminal_data()

# 3. Decision Logic & KPIs
st.title("🛡️ Star Divergence V3: The Alpha Terminal")
st.caption(f"Proprietary Market Intelligence | Last Updated: April 26, 2026")

if df is not None and 'Alpha_Rank' in df.columns:
    # Key Stats Row
    top_asset = df.sort_values(by='Alpha_Rank', ascending=False).iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Highest Alpha Signal", top_asset['Name'], f"{top_asset['Alpha_Rank']:.2f} Score")
    m2.metric("Market Premium Avg", f"{df['CL_Premium'].mean():.2x}x")
    m3.metric("Current Asset Load", len(df), "Active Stars")
    m4.metric("Divergence Peak", f"{df['Divergence_Score'].max():.2f}")

    # 4. Asset Opportunity Matrix
    st.divider()
    col_chart, col_leader = st.columns([2, 1])
    
    with col_chart:
        st.subheader("📍 Opportunity Matrix")
        # Bubble chart: X=Market Premium, Y=Divergence, Size=Alpha Rank
        fig = px.scatter(df, x="CL_Premium", y="Divergence_Score",
                         size="Alpha_Rank", color="Alpha_Rank",
                         hover_name="Name", text="Name",
                         color_continuous_scale="RdYlGn",
                         labels={"CL_Premium": "Card Ladder Premium (Market Price / CL)", "Divergence_Score": "Perf Divergence"})
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

    with col_leader:
        st.subheader("🏆 Alpha Leaderboard")
        st.dataframe(df[['Name', 'Alpha_Rank', 'Status']].sort_values(by='Alpha_Rank', ascending=False), 
                     hide_index=True, use_container_width=True)

    # 5. Head-to-Head Comparison
    st.divider()
    st.subheader("⚔️ Star Battle: Comparative Value Analysis")
    p_options = df['Name'].tolist()
    c1, c2 = st.columns(2)
    
    with c1:
        p1 = st.selectbox("Compare Player A", p_options, index=0)
        p1_stats = df[df['Name'] == p1].iloc[0]
        st.metric(f"{p1} Alpha", f"{p1_stats['Alpha_Rank']:.2f}")
        st.progress(min(p1_stats['Alpha_Rank'] / 2, 1.0))
        
    with c2:
        p2 = st.selectbox("Compare Player B", p_options, index=1)
        p2_stats = df[df['Name'] == p2].iloc[0]
        st.metric(f"{p2} Alpha", f"{p2_stats['Alpha_Rank']:.2f}")
        st.progress(min(p2_stats['Alpha_Rank'] / 2, 1.0))

else:
    st.warning("⚠️ Critical Alert: 'Alpha_Rank' column not found in Google Sheet. Please add Column H to your sheet and refresh.")

# 6. Sidebar Market Notes
st.sidebar.header("Terminal Insights")
if df is not None:
    st.sidebar.success(f"**Top Buy:** {top_asset['Name']} is currently the most efficient performance asset relative to Card Ladder benchmarks.")
st.sidebar.info("Methodology: Alpha Rank = Divergence Score / Card Ladder Premium. It identifies players whose performance gap is wider than their market hype.")
