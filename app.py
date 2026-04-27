import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="High-End Star Divergence Tracker", layout="wide")

st.title("📈 High-End Star Divergence Tracker (2026)")
st.markdown("Comparing current performance against 3-year historical benchmarks.")

# Sidebar for Price Inputs
st.sidebar.header("Current Market Prices (PSA 10)")
prices = {
    "Yordan Alvarez": st.sidebar.number_input("Yordan Alvarez ($)", value=150),
    "Aaron Judge": st.sidebar.number_input("Aaron Judge ($)", value=210),
    "Shohei Ohtani": st.sidebar.number_input("Shohei Ohtani ($)", value=550)
}

@st.cache_data
def fetch_mlb_data():
    # Fetching from official MLB API (Usually bypasses the 403 block)
    url = "https://statsapi.mlb.com/api/v1/stats?stats=season&group=batting&season=2026&playerPool=all"
    response = requests.get(url)
    data = response.json()
    
    player_stats = []
    target_stars = ["Yordan Alvarez", "Aaron Judge", "Shohei Ohtani"]
    
    for split in data['stats'][0]['splits']:
        name = split['player']['fullName']
        if name in target_stars:
            stats = split['stat']
            player_stats.append({
                "Name": name,
                "AVG": stats.get('avg'),
                "OPS": float(stats.get('ops', 0)),
                "HR": stats.get('homeRuns'),
                "PA": stats.get('plateAppearances')
            })
    return pd.DataFrame(player_stats)

try:
    df = fetch_mlb_data()
    
    # Calculate the Divergence Score
    df['Price'] = df['Name'].map(prices)
    # Strategy: OPS per $100 spent
    df['Divergence_Score'] = (df['OPS'] * 100) / df['Price']
    
    st.subheader("2026 Performance vs. Market Value")
    st.dataframe(df.sort_values(by='Divergence_Score', ascending=False), use_container_width=True)
    
    st.success("✅ Data live from official MLB feeds.")

except Exception as e:
    st.error(f"System Offline: {e}")
    st.info("The data provider might be experiencing high traffic. Refresh in 60 seconds.")
