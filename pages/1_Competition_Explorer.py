"""
Page 1: Competition Explorer
Allows comprehensive exploration of tennis tournaments, hierarchy (parent/sub-competitions),
and categorical breakdowns with interactive filters and charts.
"""

import streamlit as st
import pandas as pd
from database.crud import get_all_competitions
from services.analytics import (
    create_competitions_by_category_chart,
    create_competition_distribution_chart
)

st.set_page_config(page_title="Competition Explorer | Tennis Analytics", page_icon="🏆", layout="wide")

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

st.markdown('<div class="page-title">🏆 Competition Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Filter, search, and analyze international tennis competitions, parent tournaments, and categories.</div>', unsafe_allow_html=True)

comps_df = get_all_competitions()

if comps_df.empty:
    st.info("No competition data found in the database. Please visit Data Management to synchronize or load sample data.")
    st.stop()

# Filter Controls in an Expander or Columns
with st.expander("🔍 Search and Filter Options", expanded=True):
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        search_query = st.text_input("Search Competition Name", placeholder="e.g., Wimbledon, French Open...")

    with f2:
        categories = ["All Categories"] + sorted([c for c in comps_df["category_name"].dropna().unique()])
        selected_category = st.selectbox("Category", categories)

    with f3:
        genders = ["All Genders"] + sorted([g for g in comps_df["gender"].dropna().unique()])
        selected_gender = st.selectbox("Gender", genders)

    with f4:
        types = ["All Types"] + sorted([t for t in comps_df["competition_type"].dropna().unique()])
        selected_type = st.selectbox("Competition Type", types)

# Apply Filters
filtered_df = comps_df.copy()

if search_query:
    filtered_df = filtered_df[filtered_df["competition_name"].str.contains(search_query, case=False, na=False)]

if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["category_name"] == selected_category]

if selected_gender != "All Genders":
    filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

if selected_type != "All Types":
    filtered_df = filtered_df[filtered_df["competition_type"] == selected_type]

# Metrics Summary
m1, m2, m3, m4 = st.columns(4)
m1.metric("Competitions Found", len(filtered_df))
m2.metric("Categories Represented", filtered_df["category_name"].nunique())
top_level_count = (filtered_df["parent_id"].isna() | (filtered_df["parent_id"] == "")).sum()
m3.metric("Top-Level Competitions", int(top_level_count))
sub_comp_count = len(filtered_df) - top_level_count
m4.metric("Sub-Competitions", int(sub_comp_count))

st.markdown("<br>", unsafe_allow_html=True)

# Visual Distribution
col_c1, col_c2 = st.columns(2)
with col_c1:
    fig_cat = create_competitions_by_category_chart(filtered_df)
    if fig_cat:
        st.plotly_chart(fig_cat, use_container_width=True)
with col_c2:
    fig_type = create_competition_distribution_chart(filtered_df)
    if fig_type:
        st.plotly_chart(fig_type, use_container_width=True)

st.markdown("### 📋 Competitions Data Table")

# Format display columns
display_cols = [
    "competition_id",
    "competition_name",
    "category_name",
    "competition_type",
    "gender",
    "parent_name"
]
rename_map = {
    "competition_id": "Competition ID",
    "competition_name": "Competition Name",
    "category_name": "Category",
    "competition_type": "Format / Type",
    "gender": "Gender",
    "parent_name": "Parent Tournament"
}

formatted_table = filtered_df[display_cols].rename(columns=rename_map).fillna("None (Top-Level)")
st.dataframe(formatted_table, use_container_width=True, hide_index=True)

# Parent / Sub-Competition Hierarchy Drill-down
st.markdown("### 🌳 Parent & Sub-Competition Hierarchy View")
parent_comps = comps_df[comps_df["parent_id"].isna() | (comps_df["parent_id"] == "")]
selected_parent_name = st.selectbox(
    "Select Parent Tournament to Inspect Sub-Competitions:",
    ["Select a Tournament..."] + sorted(parent_comps["competition_name"].dropna().unique().tolist())
)

if selected_parent_name != "Select a Tournament...":
    parent_id_val = parent_comps.loc[parent_comps["competition_name"] == selected_parent_name, "competition_id"].values[0]
    sub_comps = comps_df[comps_df["parent_id"] == parent_id_val]

    if not sub_comps.empty:
        st.success(f"Found {len(sub_comps)} sub-competitions under **{selected_parent_name}**:")
        st.dataframe(
            sub_comps[["competition_id", "competition_name", "competition_type", "gender", "category_name"]].rename(
                columns={"competition_id": "ID", "competition_name": "Sub-Competition", "competition_type": "Type"}
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(f"No sub-competitions are linked to '{selected_parent_name}'. It operates as an independent tournament.")

