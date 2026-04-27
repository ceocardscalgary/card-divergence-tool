import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Terminal Styling & Page Config
st.set_page_config(page_title="SlabMetrics Alpha V5.1", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] { 
        background-color: white; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Sync
# GID verified from your screenshot as 1605600764
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=1605600764&single=true&output=csv"

@st.cache_data(ttl=300)
def load_terminal_data():
    try:
        df = pd.read_csv(SHEET_URL, skipinitialspace=True)
        
        # DEFENSIVE FIX: Fill empty card names so st.metric doesn't crash
        if 'Card_Name' in df.columns:
            df['Card_Name'] = df['Card_Name'].fillna("Unnamed Asset").astype(str)
        
        # Clean numeric columns
        cols_to_fix = ['bWAR', 'SPI', 'Secondary_1', 'Secondary_2', 'CL_Value', 'Alpha_Rank']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return None

df = load_terminal_data()

# 3. Decision Logic & Sidebar
st.title("🛡️ SlabMetrics Alpha V5.1: The Blue-Chip Terminal")
st.caption("Institutional Sabermetric Arbitrage | Career Equity vs. Market Value")

if df is not None and not df.empty:
    # Sidebar: Market Controls
    st.sidebar.header("🕹️ Market Controls")
    ebay_discount = st.sidebar.slider("eBay 'Live' Discount (%)", 0, 25, 0)
    
    # Calculate Adjusted Values
    # We replace 0 with a small number to avoid the 'Infinity' Alpha Rank you saw
    df['Adj_Value'] = df['CL_Value'].apply(lambda x: x if x > 0 else 1) * (1 - (ebay_discount / 100))
    df['Adj_Alpha'] = (df['SPI'] * 100) / df['Adj_Value']

    # --- TOP LEVEL KPIs ---
    m1, m2, m3, m4 = st.columns(4)
    # Filter out 0 prices for the "Top Alpha" to make it meaningful
    valid_alpha_df = df[df['CL_Value'] > 0]
    
    if not valid_alpha_df.empty:
        top_card = valid_alpha_df.sort_values(by='Adj_Alpha', ascending=False).iloc[0]
        m1.metric("Highest Alpha Opportunity", top_card['Player'], f"{top_card['Adj_Alpha']:.2f}")
        m3.metric("Avg Alpha Rank", f"{valid_alpha_df['Adj_Alpha'].mean():.2f}")
    else:
        m1.metric("Highest Alpha Opportunity", "N/A", "Input Prices")
        m3.metric("Avg Alpha Rank", "0.00")

    m2.metric("Market Coverage", f"{len(df['Player'].unique())} Stars", "50 Cards Loaded")
    m4.metric("Terminal Status", "Live", "Verified 2026")

    # --- THE ALPHA MATRIX ---
    st.divider()
    st.subheader("📍 The Alpha Matrix: Performance vs. Valuation")
    
    if not valid_alpha_df.empty:
        fig = px.scatter(df, x="Adj_Value", y="SPI", 
                         size="Adj_Alpha", color="Adj_Alpha",
                         hover_name="Card_Name", text="Player",
                         color_continuous_scale="RdYlGn",
                         labels={"Adj_Value": "Market Price ($)", "SPI": "SlabMetric Index"})
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Input values in the 'CL_Value' column of your Google Sheet to generate the Matrix.")

    # --- THE ALPHA 50 PORTFOLIO ---
    st.divider()
    st.header("🏆 The Alpha 50 Portfolio")
    
    players = df['Player'].unique()
    for player in players:
        p_cards = df[df['Player'] == player].sort_values(by='Adj_Alpha', ascending=False)
        avg_p_alpha = p_cards['Adj_Alpha'].mean()
        
        with st.expander(f"👤 {player} | Portfolio Alpha: {avg_p_alpha:.2f}"):
            # Display cards in a grid
            card_cols = st.columns(min(len(p_cards), 5))
            for i, (_, card) in enumerate(p_cards.iterrows()):
                with card_cols[i % 5]:
                    # Format the metric to be safe even if names are missing
                    label = card['Card_Name'] if card['Card_Name'] != "Unnamed Asset" else "Investment Option"
                    st.metric(label, f"${card['CL_Value']:,.0f}", f"{card['Adj_Alpha']:.2f} Alpha")
                    
                    # eBay Integration
                    query = f"{card['Player']} {card['Card_Name']} PSA 10 Sold".replace(" ", "+")
                    st.link_button("🔥 Check eBay", f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1&LH_Complete=1")

else:
    st.warning("🔄 Reconnecting to SlabMetrics Engine... verify your 'Master_Alpha_50' tab is populated.")
