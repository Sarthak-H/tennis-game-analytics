"""
Page 2: Player Rankings
Doubles Competitor Standings explorer with comprehensive search,
multi-attribute filters, sorting, and pagination.
"""

import streamlit as st
import pandas as pd
from database.crud import get_all_rankings
from utils.helpers import format_movement, format_number

st.set_page_config(page_title="Player Rankings | Tennis Analytics", page_icon="🥇", layout="wide")

st.markdown("""
<style>
    .page-title {
        font-size: 26px;
        font-weight: 800;
        color: #0B192C;
        margin-bottom: 4px;
    }
    .page-desc {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🥇 Doubles Competitor Rankings</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Official doubles tennis standings, ranking movement, cumulative points, and participation data.</div>', unsafe_allow_html=True)

ranks_df = get_all_rankings()

if ranks_df.empty:
    st.info("No competitor rankings data found. Please synchronize data in Data Management.")
    st.stop()

# Filters & Controls
with st.expander("🔍 Filters & Search Controls", expanded=True):
    r1, r2 = st.columns([2, 2])
    with r1:
        search_name = st.text_input("Search Competitor / Player Name", placeholder="e.g., Mektic, Pavic, Ram...")
    with r2:
        countries = ["All Countries"] + sorted([c for c in ranks_df["country"].dropna().unique() if c])
        selected_country = st.selectbox("Country", countries)

    r3, r4, r5 = st.columns(3)
    min_rank_val = int(ranks_df["rank"].min())
    max_rank_val = int(ranks_df["rank"].max())

    with r3:
        rank_range = st.slider(
            "Rank Range",
            min_value=min_rank_val,
            max_value=max_rank_val,
            value=(min_rank_val, max_rank_val)
        )

    with r4:
        min_pts_possible = int(ranks_df["points"].min())
        max_pts_possible = int(ranks_df["points"].max())
        min_pts_filter = st.number_input(
            "Minimum Ranking Points",
            min_value=0,
            max_value=max_pts_possible,
            value=0,
            step=100
        )

    with r5:
        sort_choice = st.selectbox(
            "Sort Order",
            ["Rank: 1 to N (Ascending)", "Rank: N to 1 (Descending)", "Points: High to Low", "Movement: Climbers First"]
        )

# Filtering logic
filtered_ranks = ranks_df.copy()

if search_name:
    filtered_ranks = filtered_ranks[filtered_ranks["competitor_name"].str.contains(search_name, case=False, na=False)]

if selected_country != "All Countries":
    filtered_ranks = filtered_ranks[filtered_ranks["country"] == selected_country]

filtered_ranks = filtered_ranks[
    (filtered_ranks["rank"] >= rank_range[0]) &
    (filtered_ranks["rank"] <= rank_range[1]) &
    (filtered_ranks["points"] >= min_pts_filter)
]

# Sorting
if sort_choice == "Rank: 1 to N (Ascending)":
    filtered_ranks = filtered_ranks.sort_values(by="rank", ascending=True)
elif sort_choice == "Rank: N to 1 (Descending)":
    filtered_ranks = filtered_ranks.sort_values(by="rank", ascending=False)
elif sort_choice == "Points: High to Low":
    filtered_ranks = filtered_ranks.sort_values(by="points", ascending=False)
elif sort_choice == "Movement: Climbers First":
    filtered_ranks = filtered_ranks.sort_values(by="movement", ascending=False)

# KPI Summary of Filtered Results
s1, s2, s3, s4 = st.columns(4)
s1.metric("Competitors Matching", len(filtered_ranks))
if not filtered_ranks.empty:
    s2.metric("Top Rank in View", f"#{int(filtered_ranks['rank'].min())}")
    s3.metric("Highest Points", format_number(int(filtered_ranks['points'].max())))
    s4.metric("Average Points", format_number(int(filtered_ranks['points'].mean())))

st.markdown("<br>", unsafe_allow_html=True)

# Pagination Controls
page_size = st.selectbox("Rows per page", [10, 20, 50, 100], index=1)
total_rows = len(filtered_ranks)
total_pages = max(1, (total_rows + page_size - 1) // page_size)

page_col1, page_col2 = st.columns([1, 4])
with page_col1:
    page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
with page_col2:
    st.caption(f"Showing page {page_number} of {total_pages} ({total_rows} total competitors)")

start_idx = (page_number - 1) * page_size
end_idx = start_idx + page_size
page_data = filtered_ranks.iloc[start_idx:end_idx].copy()

# Table formatting
page_data["Formatted Movement"] = page_data["movement"].apply(format_movement)
page_data["Formatted Points"] = page_data["points"].apply(format_number)

table_display = page_data[[
    "rank",
    "competitor_name",
    "country",
    "country_code",
    "Formatted Points",
    "Formatted Movement",
    "competitions_played"
]].rename(columns={
    "rank": "Rank",
    "competitor_name": "Competitor / Team",
    "country": "Country",
    "country_code": "Code",
    "Formatted Points": "Points",
    "Formatted Movement": "Weekly Movement",
    "competitions_played": "Tournaments Played"
})

st.dataframe(table_display, use_container_width=True, hide_index=True)

# Export Data Button
csv = filtered_ranks.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Filtered Rankings to CSV",
    data=csv,
    file_name="tennis_doubles_rankings.csv",
    mime="text/csv"
)

