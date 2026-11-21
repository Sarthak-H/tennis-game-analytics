"""
Page 3: Leaderboards
Elite doubles competitor leaderboards featuring Top 5 podium, Top 10/20 showcases,
highest scoring players, and best ranking climbers.
"""

import streamlit as st
import pandas as pd
from database.crud import get_all_rankings
from utils.helpers import format_movement, format_number

st.set_page_config(page_title="Leaderboards | Tennis Analytics", page_icon="🌟", layout="wide")

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
    .podium-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .podium-gold {
        border-top: 5px solid #FFD700;
    }
    .podium-silver {
        border-top: 5px solid #C0C0C0;
    }
    .podium-bronze {
        border-top: 5px solid #CD7F32;
    }
    .podium-rank {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .podium-name {
        font-size: 16px;
        font-weight: 700;
        color: #0B192C;
        margin-bottom: 6px;
    }
    .podium-points {
        font-size: 20px;
        font-weight: 800;
        color: #00C853;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🌟 Doubles Tennis Leaderboards</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">The premier standings in doubles tennis: top tier performers, point leaders, and momentum climbers.</div>', unsafe_allow_html=True)

ranks_df = get_all_rankings()

if ranks_df.empty:
    st.info("No ranking records found in database. Please synchronize data in Data Management.")
    st.stop()

# Sort by rank ASC
sorted_by_rank = ranks_df.sort_values(by="rank", ascending=True)

# -----------------------------------------------------------------------------
# TOP 3 PODIUM DISPLAY
# -----------------------------------------------------------------------------
if len(sorted_by_rank) >= 3:
    st.markdown("### 🏆 Podium Finishers (World Top 3)")
    p1 = sorted_by_rank.iloc[0]
    p2 = sorted_by_rank.iloc[1]
    p3 = sorted_by_rank.iloc[2]

    c2, c1, c3 = st.columns([1, 1.2, 1])

    with c1:
        st.markdown(f"""
        <div class="podium-card podium-gold">
            <div class="podium-rank">🥇 Rank 1</div>
            <div class="podium-name">{p1['competitor_name']}</div>
            <div>🌍 {p1['country']} ({p1['country_code']})</div>
            <div class="podium-points">{format_number(p1['points'])} pts</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 4px;">{format_movement(p1['movement'])} movement • {p1['competitions_played']} played</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="podium-card podium-silver">
            <div class="podium-rank">🥈 Rank 2</div>
            <div class="podium-name">{p2['competitor_name']}</div>
            <div>🌍 {p2['country']} ({p2['country_code']})</div>
            <div class="podium-points">{format_number(p2['points'])} pts</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 4px;">{format_movement(p2['movement'])} movement • {p2['competitions_played']} played</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="podium-card podium-bronze">
            <div class="podium-rank">🥉 Rank 3</div>
            <div class="podium-name">{p3['competitor_name']}</div>
            <div>🌍 {p3['country']} ({p3['country_code']})</div>
            <div class="podium-points">{format_number(p3['points'])} pts</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 4px;">{format_movement(p3['movement'])} movement • {p3['competitions_played']} played</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Leaderboard Tabs
tab_top5, tab_top10, tab_top20, tab_points, tab_climbers = st.tabs([
    "🎖️ Top 5",
    "🔟 Top 10",
    "🏅 Top 20",
    "💎 Highest Points",
    "🚀 Best Movers"
])

def render_table(df_subset, highlight_col=None):
    df_disp = df_subset.copy()
    df_disp["Movement"] = df_disp["movement"].apply(format_movement)
    df_disp["Points"] = df_disp["points"].apply(format_number)
    table = df_disp[[
        "rank",
        "competitor_name",
        "country",
        "country_code",
        "Points",
        "Movement",
        "competitions_played"
    ]].rename(columns={
        "rank": "Rank",
        "competitor_name": "Competitor / Team",
        "country": "Country",
        "country_code": "ISO Code",
        "competitions_played": "Tournaments Played"
    })
    st.dataframe(table, use_container_width=True, hide_index=True)


with tab_top5:
    st.markdown("#### Top 5 Ranked Competitors")
    render_table(sorted_by_rank.head(5))

with tab_top10:
    st.markdown("#### Top 10 Ranked Competitors")
    render_table(sorted_by_rank.head(10))

with tab_top20:
    st.markdown("#### Top 20 Ranked Competitors")
    render_table(sorted_by_rank.head(20))

with tab_points:
    st.markdown("#### Competitors with Highest Ranking Points")
    pts_leaders = ranks_df.sort_values(by="points", ascending=False).head(20)
    render_table(pts_leaders)

with tab_climbers:
    st.markdown("#### Greatest Positive Ranking Movement (This Week's Top Climbers)")
    climbers = ranks_df[ranks_df["movement"] > 0].sort_values(by="movement", ascending=False)
    if not climbers.empty:
        render_table(climbers)
    else:
        st.info("No competitors recorded positive rank movement in this current dataset.")

