"""
Page 5: Venues and Complexes
Explore world-class tennis venues, sports facilities, stadiums, court capacities,
and geographic distributions.
"""

import streamlit as st
import pandas as pd
from database.crud import get_all_venues_complexes, get_complex_counts
from services.analytics import create_venues_by_country_chart

st.set_page_config(page_title="Venues & Complexes | Tennis Analytics", page_icon="🏟️", layout="wide")

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

st.markdown('<div class="page-title">🏟️ Tennis Complexes and Stadium Venues</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Facility infrastructure, stadium courts, locations, and timezones from the SportRadar complexes registry.</div>', unsafe_allow_html=True)

venues_df = get_all_venues_complexes()
complex_counts_df = get_complex_counts()

if venues_df.empty:
    st.info("No venue or complex records found. Please synchronize data in Data Management.")
    st.stop()

# KPI Metrics
vk1, vk2, vk3, vk4 = st.columns(4)
vk1.metric("Total Complexes", len(complex_counts_df))
vk2.metric("Total Venues / Courts", len(venues_df))
multi_venue_complexes = complex_counts_df[complex_counts_df["venue_count"] > 1]
vk3.metric("Multi-Court Complexes", len(multi_venue_complexes))
vk4.metric("Countries with Facilities", venues_df["country_name"].nunique())

st.markdown("<br>", unsafe_allow_html=True)

# Filters
with st.expander("🔍 Search and Filter Venues", expanded=True):
    vf1, vf2, vf3 = st.columns(3)
    with vf1:
        search_v = st.text_input("Search Venue Name or City", placeholder="e.g., Centre Court, Paris, London...")
    with vf2:
        countries = ["All Countries"] + sorted([c for c in venues_df["country_name"].dropna().unique()])
        sel_country = st.selectbox("Filter Country", countries)
    with vf3:
        complex_names = ["All Complexes"] + sorted([c for c in venues_df["complex_name"].dropna().unique()])
        sel_complex = st.selectbox("Filter Sports Complex", complex_names)

filtered_venues = venues_df.copy()

if search_v:
    mask = (
        filtered_venues["venue_name"].str.contains(search_v, case=False, na=False) |
        filtered_venues["city_name"].str.contains(search_v, case=False, na=False)
    )
    filtered_venues = filtered_venues[mask]

if sel_country != "All Countries":
    filtered_venues = filtered_venues[filtered_venues["country_name"] == sel_country]

if sel_complex != "All Complexes":
    filtered_venues = filtered_venues[filtered_venues["complex_name"] == sel_complex]

# Visualization
col_vchart1, col_vchart2 = st.columns(2)
with col_vchart1:
    fig_v_country = create_venues_by_country_chart(filtered_venues)
    if fig_v_country:
        st.plotly_chart(fig_v_country, use_container_width=True)

with col_vchart2:
    st.markdown("#### 🏢 Venues Per Complex")
    st.dataframe(
        complex_counts_df.rename(columns={
            "complex_id": "Complex ID",
            "complex_name": "Sports Complex",
            "venue_count": "Number of Venues"
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("### 📋 Venues Directory")
display_venues = filtered_venues[[
    "complex_id",
    "complex_name",
    "venue_id",
    "venue_name",
    "city_name",
    "country_name",
    "country_code",
    "timezone"
]].rename(columns={
    "complex_id": "Complex ID",
    "complex_name": "Complex Name",
    "venue_id": "Venue ID",
    "venue_name": "Venue / Court",
    "city_name": "City",
    "country_name": "Country",
    "country_code": "Code",
    "timezone": "Timezone"
})
st.dataframe(display_venues, use_container_width=True, hide_index=True)

# Complexes with Multiple Courts
st.markdown("### 🏟️ Complexes with Multiple Arenas / Courts")
if not multi_venue_complexes.empty:
    st.info(f"Identified {len(multi_venue_complexes)} premier complexes with multiple tournament arenas:")
    st.dataframe(
        multi_venue_complexes.rename(columns={
            "complex_id": "Complex ID",
            "complex_name": "Facility Name",
            "venue_count": "Active Arenas"
        }),
        use_container_width=True,
        hide_index=True
    )

