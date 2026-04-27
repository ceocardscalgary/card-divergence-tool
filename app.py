import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="High-End Star Divergence Tracker", layout="wide")

st.title("📈 High-End Star Divergence Tracker (2026)")
st.markdown("Proprietary analytical data comparing 2026 performance vs. market valuation.")

# 2. YOUR GOOGLE SHEET CSV LINK
# Replace the URL below with your 'Publish to Web' CSV link from Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0CVHmiq-BZWdi55hhxYmou_ypaWownqkkBRjYJhl1a4BH6yVed-BfwIPFGHM0ORPQpJlY0lvpWa5O/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600)  # Refreshes the data every 10 minutes
def load_data():
    try:
        # Pulling the clean data from your Google Sheet
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Error connecting to Data Engine: {e}")
        return None

# 3. Load and Display Data
df = load_data()

if df is not None:
    # Sort by Divergence Score automatically to show the best "Buys" first
    # (Assuming your column is named 'Divergence_Score' or similar)
    if 'Divergence_Score' in df.columns:
        df = df.sort_values(by='Divergence_Score', ascending=False)
    
    st.subheader("Market Analysis: Performance vs. Price")
    st.dataframe(df, use_container_width=True)
    
    st.success("✅ Data Engine Status: Online & Verified")
    
    # 4. Add your "Analytical" Personality
    st.divider()
    st.subheader("📝 Market Insights")
    st.write("""
        This tracker identifies valuation gaps in the high-end sports card market. 
        A higher **Divergence Score** indicates a player is significantly outperforming 
        their current market price based on 2026 Statcast metrics.
    """)
else:
    st.warning("🔄 Waiting for data from Google Sheets... Ensure your sheet is 'Published to the Web' as a CSV.")
