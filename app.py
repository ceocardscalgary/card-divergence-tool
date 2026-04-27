import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Terminal Styling & Page Config
st.set_page_config(page_title="SlabMetrics Alpha V5", layout="wide")

# Custom CSS for a professional "Fintech Terminal" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] { 
        background-color: white; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    [data-testid="stExpander"] { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Sync
# REPLACE with your 'Publish to Web' CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=1605600764&single=true&output=csv"

@st.cache_data(ttl=300)
def load_terminal_data():
    try:
        # Load data and handle the asterisk/text issues silently
        df = pd.read_csv(SHEET_URL, skipinitialspace=True)
        # Clean numeric columns to ensure math doesn't break
        cols_to_fix = ['bWAR', 'SPI', 'Secondary_1', 'Secondary_2', 'CL_Value', 'Alpha_Rank']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return None

df = load_terminal_data()

# 3. Decision Logic & Sidebar Controls
st.title("🛡️ SlabMetrics Alpha V5: The Blue-Chip Terminal")
st.caption("Institutional Sabermetric Arbitrage | Career Equity vs. Market Value")

if df is not None:
    # Sidebar: Market Sentiment (The eBay Gap)
    st.sidebar.header("🕹️ Market Controls")
    ebay_discount = st.sidebar.slider("eBay 'Live' Discount (%)", 0, 25, 0)
    
    # Recalculate based on live user input
    df['Adj_Value'] = df['CL_Value'] * (1 - (ebay_discount / 100))
    # Alpha = (SPI / Price) * 100 -- ensures numbers are readable
    df['Adj_Alpha'] = (df['SPI'] * 100) / df['Adj_Value'].replace(0, 1)

    # --- TOP LEVEL KPIs ---
    m1, m2, m3, m4 = st.columns(4)
    top_card = df.sort_values(by='Adj_Alpha', ascending=False).iloc[0]
    m1.metric("Highest Alpha Opportunity", top_card['Player'], f"{top_card['Adj_Alpha']:.2f}")
    m2.metric("Market Coverage", f"{len(df['Player'].unique())} Stars", "50 Cards Total")
    m3.metric("Avg Market Premium", f"{df['Adj_Alpha'].mean():.2f}")
    m4.metric("Terminal Status", "Live", "Verified 2026")

    # --- THE ALPHA MATRIX (Bubble Chart) ---
    st.divider()
    st.subheader("📍 The Alpha Matrix: Performance vs. Valuation")
    st.info("💡 Top-Left Quadrant: High Career Equity (SPI) at Low Market Cost (Value).")
    
    fig = px.scatter(df, x="Adj_Value", y="SPI", 
                     size="Adj_Alpha", color="Adj_Alpha",
                     hover_name="Card_Name", text="Player",
                     color_continuous_scale="RdYlGn",
                     labels={"Adj_Value": "Effective Market Price ($)", "SPI": "SlabMetric Performance Index"})
    
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

    # --- THE ALPHA 50 PORTFOLIO (Grouped by Player) ---
    st.divider()
    st.header("🏆 The Alpha 50 Portfolio")
    
    # Grouping logic to prevent a "wall of text"
    players = df['Player'].unique()
    for player in players:
        p_cards = df[df['Player'] == player].sort_values(by='Adj_Alpha', ascending=False)
        avg_p_alpha = p_cards['Adj_Alpha'].mean()
        
        with st.expander(f"👤 {player} | Portfolio Alpha: {avg_p_alpha:.2f}"):
            cols = st.columns(5)
            for i, (_, card) in enumerate(p_cards.iterrows()):
                with cols[i]:
                    st.metric(card['Card_Name'], f"${card['Adj_Value']:,.0f}", f"{card['Adj_Alpha']:.2f} Alpha")
                    # PRE-FILLED EBAY SOLD SEARCH
                    search_query = f"{card['Player']} {card['Card_Name']} PSA 10 Sold".replace(" ", "+")
                    ebay_link = f"https://www.ebay.com/sch/i.html?_nkw={search_query}&LH_Sold=1&LH_Complete=1"
                    st.link_button("🔥 Check eBay", ebay_link)

else:
    st.warning("🔄 Reconnecting to SlabMetrics Engine... Ensure your CSV link is correct.")
