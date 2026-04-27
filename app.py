import streamlit as st
import pandas as pd
from pybaseball import batting_stats

# --- APP CONFIG ---
st.set_page_config(page_title="High-End Star Divergence", layout="wide")
st.header("📈 High-End Star Divergence Tracker (2026)")
st.markdown("Comparing current 2026 performance against 3-year historical benchmarks.")

# --- DATA FETCHING ---
@st.cache_data
def fetch_player_data():
    """Fetches 2026 live stats and 2023-2025 historical stats."""
    # Current 2026 stats
    df_2026 = batting_stats(2026)
    # 3-Year Average (2023-2025)
    df_hist = batting_stats(2023, 2025)
    return df_2026, df_hist

try:
    df_2026, df_hist = fetch_player_data()
    target_players = ["Yordan Alvarez", "Aaron Judge", "Shohei Ohtani"]

    # --- SIDEBAR INPUTS ---
    st.sidebar.subheader("Manual Price Input")
    prices = {}
    for player in target_players:
        prices[player] = st.sidebar.number_input(f"Price for {player}:", min_value=1.0, value=100.0)

    # --- DATA PROCESSING ---
    processed_data = []

    for name in target_players:
        # Get 2026 OPS
        p_2026 = df_2026[df_2026['Name'] == name]
        current_ops = p_2026['OPS'].values[0] if not p_2026.empty else 0.0
        
        # Get 3-Year Avg OPS
        p_hist = df_hist[df_hist['Name'] == name]
        avg_ops = p_hist['OPS'].values[0] if not p_hist.empty else 0.0
        
        # Calculate Value Score: (OPS * 100) / Price
        price = prices[name]
        value_score = (current_ops * 100) / price
        
        processed_data.append({
            "Player": name,
            "2026 OPS": round(current_ops, 3),
            "3-Yr Avg OPS": round(avg_ops, 3),
            "Price": f"${price}",
            "Value Score": round(value_score, 2)
        })

    results_df = pd.DataFrame(processed_data)

    # --- TABLE HIGHLIGHTING ---
    def highlight_max_value(s):
        is_max = s == s.max()
        return ['background-color: #2e7d32; color: white' if v else '' for v in is_max]

    st.subheader("Current Market Value Analysis")
    st.dataframe(
        results_df.style.apply(highlight_max_value, subset=['Value Score']),
        use_container_width=True
    )

    # --- RECOMMENDATION BUTTON ---
    st.divider()
    if st.button("Generate Buy/Sell Recommendations"):
        cols = st.columns(3)
        for i, row in results_df.iterrows():
            with cols[i]:
                # Divergence Logic: If current > average, they are "Hot" (Sell high). 
                # If current < average, they are "Cold" (Buy low).
                if row["2026 OPS"] > row["3-Yr Avg OPS"]:
                    st.error(f"**SELL** {row['Player']}")
                    st.caption(f"Currently overperforming benchmark by {round(row['2026 OPS'] - row['3-Yr Avg OPS'], 3)} points.")
                else:
                    st.success(f"**BUY** {row['Player']}")
                    st.caption(f"Underperforming benchmark. Mean reversion expected.")

except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.info("Check your internet connection and ensure pybaseball is up to date.")
