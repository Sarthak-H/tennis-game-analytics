"""
Page 4: Country-Wise Analysis
Comprehensive international participation metrics: competitor counts,
points distributions, averages, and best national representatives.
"""

import streamlit as st
import pandas as pd
from database.crud import get_country_aggregates, get_all_rankings
from services.analytics import (
    create_competitors_by_country_chart,
    create_country_points_chart
)
from utils.helpers import format_number

st.set_page_config(page_title="Country Analysis | Tennis Analytics", page_icon="🌍", layout="wide")

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
    .country-kpi {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        border-top: 3px solid #00C853;
    }
    .country-val {
        font-size: 24px;
        font-weight: 800;
        color: #0B192C;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🌍 Country-Wise Participation & Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Examine global tennis strength: competitor volume, aggregate scoring power, and national best performers.</div>', unsafe_allow_html=True)

country_df = get_country_aggregates()
ranks_df = get_all_rankings()

if country_df.empty or ranks_df.empty:
    st.info("No competitor data available. Please synchronize data in Data Management.")
    st.stop()

# Overall Global Summary
g1, g2, g3, g4 = st.columns(4)
g1.metric("Total Nations Represented", len(country_df))
g2.metric("Total Ranked Players", int(country_df["competitor_count"].sum()))
g3.metric("World Total Points", format_number(int(country_df["total_points"].sum())))
top_nation = country_df.iloc[0]["country"]
g4.metric("Leading Nation (by Count)", top_nation)

st.markdown("<br>", unsafe_allow_html=True)

# Interactive Charts
c_tab1, c_tab2, c_tab3 = st.tabs([
    "📊 Competitor Distribution",
    "📈 Average Points per Country",
    "💰 Total Points per Country"
])

with c_tab1:
    fig_comp = create_competitors_by_country_chart(country_df)
    if fig_comp:
        st.plotly_chart(fig_comp, use_container_width=True)

with c_tab2:
    fig_avg = create_country_points_chart(country_df, metric="avg_points")
    if fig_avg:
        st.plotly_chart(fig_avg, use_container_width=True)

with c_tab3:
    fig_tot = create_country_points_chart(country_df, metric="total_points")
    if fig_tot:
        st.plotly_chart(fig_tot, use_container_width=True)

st.markdown("---")
st.markdown("### 🔍 Specific Country Deep-Dive")

all_countries = sorted([c for c in country_df["country"].unique() if c != "Unknown"])
selected_country = st.selectbox("Select Country to Inspect:", all_countries)

if selected_country:
    country_row = country_df[country_df["country"] == selected_country].iloc[0]
    roster = ranks_df[ranks_df["country"] == selected_country].sort_values(by="rank", ascending=True)

    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1:
        st.markdown(f"""
        <div class="country-kpi">
            <div style="font-size: 11px; color: #64748B; font-weight: 700;">TOTAL PLAYERS</div>
            <div class="country-val">{country_row['competitor_count']}</div>
        </div>
        """, unsafe_allow_html=True)
    with ck2:
        st.markdown(f"""
        <div class="country-kpi">
            <div style="font-size: 11px; color: #64748B; font-weight: 700;">CUMULATIVE POINTS</div>
            <div class="country-val">{format_number(country_row['total_points'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with ck3:
        st.markdown(f"""
        <div class="country-kpi">
            <div style="font-size: 11px; color: #64748B; font-weight: 700;">AVERAGE POINTS</div>
            <div class="country-val">{format_number(country_row['avg_points'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with ck4:
        st.markdown(f"""
        <div class="country-kpi">
            <div style="font-size: 11px; color: #64748B; font-weight: 700;">HIGHEST RANK</div>
            <div class="country-val">#{int(country_row['best_rank'])}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"#### Roster of Competitors from {selected_country}")
    st.dataframe(
        roster[["rank", "competitor_name", "country_code", "points", "movement", "competitions_played"]].rename(
            columns={
                "rank": "Rank",
                "competitor_name": "Player / Team",
                "country_code": "ISO",
                "points": "Points",
                "movement": "Movement",
                "competitions_played": "Competitions Played"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

