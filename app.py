"""
Main Application Entry Point: Tennis Game Analytics Dashboard
Built with Streamlit, Plotly, MySQL, SQLAlchemy, and SportRadar API.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from config import APP_TITLE, APP_SUBTITLE, APP_VERSION
from database.connection import init_database, get_active_dialect, check_database_connection
from database.crud import (
    get_kpi_summary,
    get_all_competitions,
    get_all_rankings,
    get_country_aggregates
)
from services.analytics import (
    create_competitors_by_country_chart,
    create_competition_distribution_chart,
    create_top_competitors_points_chart,
    create_ranking_movement_chart,
    create_competitions_by_category_chart
)
from services.data_sync import get_sync_metadata, load_sample_dataset
from utils.helpers import format_number

# Configure Streamlit page layout
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sports Analytics CSS styling
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #0B192C 0%, #1E3E62 100%);
        border-radius: 12px;
        padding: 24px 30px;
        color: #FFFFFF;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(11, 25, 44, 0.15);
        border-left: 6px solid #00C853;
    }
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #A0AEC0;
        margin-top: 6px;
    }
    
    /* KPI Metric Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-top: 3px solid #00C853;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #0B192C;
        margin: 0;
    }
    .kpi-badge {
        font-size: 11px;
        color: #00C853;
        font-weight: 600;
        margin-top: 4px;
    }
    
    /* Sidebar Styling */
    .sidebar-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 700;
        margin-top: 8px;
    }
    .badge-mysql {
        background-color: #E6FFFA;
        color: #00796B;
        border: 1px solid #80CBC4;
    }
    .badge-sqlite {
        background-color: #FFF8E1;
        color: #F57F17;
        border: 1px solid #FFE082;
    }
    
    /* Alert / Callout Boxes */
    .alert-box {
        padding: 16px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .alert-info {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
    }
</style>
""", unsafe_allow_html=True)


def init_app_state():
    """Initializes app database on first startup."""
    try:
        init_database()
    except Exception as exc:
        st.error(f"Database initialization error: {exc}")


def render_sidebar():
    """Renders persistent sports analytics sidebar."""
    with st.sidebar:
        st.image("assets/logo.png", use_container_width=True)
        st.markdown(f"**Version**: `{APP_VERSION}`")
        st.markdown("---")

        # Database Engine Status
        dialect = get_active_dialect()
        if dialect == "mysql":
            st.markdown('<span class="sidebar-badge badge-mysql">🟢 MySQL 8.x Active</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="sidebar-badge badge-sqlite">🟡 SQLite Fallback Mode</span>', unsafe_allow_html=True)

        # Sync Metadata Status
        sync_meta = get_sync_metadata()
        st.markdown("### 🔄 Data Sync Status")
        if sync_meta["last_sync_time"]:
            st.caption(f"**Last Sync:** {sync_meta['last_sync_time']}")
            status_color = "🟢" if "Success" in sync_meta["status"] else "🔵"
            st.caption(f"**Status:** {status_color} {sync_meta['status']}")
            if sync_meta.get("is_sample_data"):
                st.caption("*(Showing Verified Sample Dataset)*")
        else:
            st.caption("Database not yet synchronized.")

        st.markdown("---")
        st.markdown("### 📋 Navigation Guide")
        st.markdown("""
        - **1. Competition Explorer**: Hierarchy & Filters
        - **2. Player Rankings**: Doubles Standings
        - **3. Leaderboards**: Top Performers & Movers
        - **4. Country Analysis**: Participation Metrics
        - **5. Venues & Complexes**: Tennis Facilities
        - **6. Data Management**: API & MySQL Controls
        """)
        st.markdown("---")
        st.caption("Powered by SportRadar Tennis API & MySQL.")


def main():
    init_app_state()
    render_sidebar()

    # Hero Header Banner
    st.markdown(f"""
    <div class="hero-container">
        <h1 class="hero-title">🎾 {APP_TITLE}</h1>
        <div class="hero-subtitle">{APP_SUBTITLE}</div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch KPI metrics from DB
    try:
        kpis = get_kpi_summary()
        comps_df = get_all_competitions()
        ranks_df = get_all_rankings()
        country_df = get_country_aggregates()
    except Exception as exc:
        st.error(f"Error fetching data from database: {exc}")
        return

    # Check for empty database state
    if kpis["total_competitors"] == 0 and kpis["total_competitions"] == 0:
        st.warning("⚠️ **Database is currently empty.** No records found in `tennis_analytics`.")
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("🚀 Load Demo Dataset Now", type="primary"):
                with st.spinner("Populating database with SportRadar-formatted data..."):
                    load_sample_dataset()
                    st.rerun()
        with col_btn2:
            st.info("Or visit the **Data Management** page in the sidebar to configure your live SportRadar API key and sync live data.")
        st.stop()

    # KPI Metrics Row (6 Cards)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Competitors</div>
            <div class="kpi-value">{format_number(kpis['total_competitors'])}</div>
            <div class="kpi-badge">Ranked Doubles</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Countries</div>
            <div class="kpi-value">{format_number(kpis['total_countries'])}</div>
            <div class="kpi-badge">Global Reach</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Competitions</div>
            <div class="kpi-value">{format_number(kpis['total_competitions'])}</div>
            <div class="kpi-badge">Tournaments</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Venues</div>
            <div class="kpi-value">{format_number(kpis['total_venues'])}</div>
            <div class="kpi-badge">Courts & Arenas</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Peak Points</div>
            <div class="kpi-value">{format_number(kpis['highest_points'])}</div>
            <div class="kpi-badge">Rank 1 Standing</div>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Complexes</div>
            <div class="kpi-value">{format_number(kpis['total_complexes'])}</div>
            <div class="kpi-badge">Facilities</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations Row 1
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_points = create_top_competitors_points_chart(ranks_df, top_n=10)
        if fig_points:
            st.plotly_chart(fig_points, use_container_width=True)

    with col_chart2:
        fig_comp_type = create_competition_distribution_chart(comps_df)
        if fig_comp_type:
            st.plotly_chart(fig_comp_type, use_container_width=True)

    # Visualizations Row 2
    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        fig_country = create_competitors_by_country_chart(country_df)
        if fig_country:
            st.plotly_chart(fig_country, use_container_width=True)

    with col_chart4:
        fig_movement = create_ranking_movement_chart(ranks_df)
        if fig_movement:
            st.plotly_chart(fig_movement, use_container_width=True)

    # Category Bar Chart
    fig_cat = create_competitions_by_category_chart(comps_df)
    if fig_cat:
        st.plotly_chart(fig_cat, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption("Data source: SportRadar Tennis API • Stored in MySQL `tennis_analytics` • Dashboard built with Streamlit & Plotly.")


if __name__ == "__main__":
    main()

