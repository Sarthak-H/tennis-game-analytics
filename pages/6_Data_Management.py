"""
Page 6: Data Management & Administration
Administer database connectivity, test SportRadar API credentials, perform granular
or full database updates, inspect real-time sync logs, or populate verification sample datasets.
"""

import streamlit as st
import pandas as pd
from config import SPORTRADAR_API_KEY, SPORTRADAR_BASE_URL, DB_NAME, DB_HOST, DB_PORT
from database.connection import check_database_connection, get_active_dialect
from database.crud import (
    get_kpi_summary,
    execute_sql_query
)
from api.sportradar_client import SportRadarClient
from services.data_sync import (
    sync_competitions_service,
    sync_complexes_service,
    sync_rankings_service,
    sync_all_service,
    load_sample_dataset,
    get_sync_metadata
)

st.set_page_config(page_title="Data Management | Tennis Analytics", page_icon="⚙️", layout="wide")

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
    .status-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">⚙️ Data Management & API Administration</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Test database and API health, trigger ETL pipelines, review operational logs, and manage storage.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SYSTEM CONNECTIVITY CHECKS
# -----------------------------------------------------------------------------
st.markdown("### 🔌 System Connectivity Diagnostics")

col_conn1, col_conn2 = st.columns(2)

with col_conn1:
    st.markdown("#### Database Engine Health")
    if st.button("🔍 Test Database Connection", key="btn_test_db"):
        is_conn, msg, dialect, host_info = check_database_connection()
        if is_conn:
            st.success(f"✅ {msg}")
        else:
            st.warning(f"⚠️ {msg}")
            st.caption("Application is safely operating in SQLite fallback mode. Start your MySQL service on port 3306 to use MySQL.")
    else:
        curr_dialect = get_active_dialect()
        st.info(f"Active Engine: **{curr_dialect.upper()}** (Target: MySQL `{DB_NAME}` at `{DB_HOST}:{DB_PORT}`)")

with col_conn2:
    st.markdown("#### SportRadar API Key Verification")
    has_key = bool(SPORTRADAR_API_KEY)
    masked_key = f"{SPORTRADAR_API_KEY[:4]}...{SPORTRADAR_API_KEY[-4:]}" if (has_key and len(SPORTRADAR_API_KEY) > 8) else ("Configured" if has_key else "Not Configured")
    st.caption(f"Status: **{masked_key}** (Base: `{SPORTRADAR_BASE_URL}`)")

    # Optional key override in session state (without exposing secrets)
    custom_key = st.text_input("Enter or Override SportRadar API Key (optional):", type="password", placeholder="Enter trial API key...")

    if st.button("🌐 Test SportRadar API Connection", key="btn_test_api"):
        test_client = SportRadarClient(api_key=custom_key.strip() if custom_key else None)
        with st.spinner("Connecting to SportRadar Tennis API..."):
            res = test_client.test_connection()
            if res["success"]:
                st.success(f"✅ {res['message']}")
                st.caption(f"Endpoints responded with keys: {res.get('data_keys', [])}")
            else:
                st.error(f"❌ API Test Failed: {res['message']}")
                st.info("💡 Register for an official trial API key at https://console.sportradar.com/signup.")

st.markdown("---")

# -----------------------------------------------------------------------------
# DATABASE RECORD AUDIT
# -----------------------------------------------------------------------------
st.markdown("### 📊 Database Relational Tables Audit")

kpis = get_kpi_summary()
tb1, tb2, tb3, tb4, tb5, tb6 = st.columns(6)
tb1.metric("Categories", kpis.get("categories", "—") if "categories" in kpis else execute_sql_query("SELECT COUNT(*) as c FROM categories")["c"].values[0])
tb2.metric("Competitions", kpis["total_competitions"])
tb3.metric("Complexes", kpis["total_complexes"])
tb4.metric("Venues", kpis["total_venues"])
tb5.metric("Competitors", kpis["total_competitors"])
rank_count = execute_sql_query("SELECT COUNT(*) as c FROM competitor_rankings")["c"].values[0]
tb6.metric("Rankings", int(rank_count))

st.markdown("---")

# -----------------------------------------------------------------------------
# DATA SYNCHRONIZATION CONTROLS
# -----------------------------------------------------------------------------
st.markdown("### 🔄 Data Synchronization Controls")
st.markdown("Synchronize the database with live SportRadar data or load the verified sample dataset.")

sync_client = SportRadarClient(api_key=custom_key.strip() if custom_key else None)

sc1, sc2 = st.columns([1.5, 1])

with sc1:
    st.markdown("#### Module ETL Triggers")

    col_btn_a, col_btn_b = st.columns(2)
    with col_btn_a:
        if st.button("📥 Sync Module A: Competitions", use_container_width=True):
            with st.spinner("Extracting & Processing Competitions..."):
                try:
                    res = sync_competitions_service(sync_client)
                    st.success(f"Success! Upserted {res['categories']} categories and {res['competitions']} competitions.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Sync error: {exc}")

        if st.button("🏟️ Sync Module B: Complexes & Venues", use_container_width=True):
            with st.spinner("Extracting & Processing Complexes..."):
                try:
                    res = sync_complexes_service(sync_client)
                    st.success(f"Success! Upserted {res['complexes']} complexes and {res['venues']} venues.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Sync error: {exc}")

    with col_btn_b:
        if st.button("🥇 Sync Module C: Doubles Rankings", use_container_width=True):
            with st.spinner("Extracting & Processing Doubles Rankings..."):
                try:
                    res = sync_rankings_service(sync_client)
                    st.success(f"Success! Upserted {res['competitors']} competitors and {res['rankings']} rankings.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Sync error: {exc}")

        # Full Sync with confirmation checkbox
        confirm_full = st.checkbox("Confirm Full Synchronization")
        if st.button("⚡ Run Full Sync (All Modules)", type="primary", disabled=not confirm_full, use_container_width=True):
            with st.spinner("Executing full end-to-end SportRadar API pipeline..."):
                full_res = sync_all_service(sync_client)
                if full_res["success"]:
                    st.success("✅ Full synchronization completed successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Synchronization failed: {full_res.get('error')}")

with sc2:
    st.markdown("#### Sample Dataset Loader")
    st.markdown(
        "If you do not have an active SportRadar API key, you can load a complete, "
        "verified sample dataset matching the exact official schema for evaluation."
    )
    if st.button("🧪 Load Verified Sample Data", use_container_width=True):
        with st.spinner("Loading verified SportRadar dataset into relational schema..."):
            sample_res = load_sample_dataset()
            st.success("✅ Sample dataset loaded successfully!")
            st.caption("Tables now contain official Grand Slam, ATP/WTA, venue, and doubles ranking records.")
            st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# LIVE SYNCHRONIZATION LOGS
# -----------------------------------------------------------------------------
st.markdown("### 📜 Synchronization Activity Logs")
sync_meta = get_sync_metadata()

status_col1, status_col2 = st.columns([1, 3])
with status_col1:
    st.markdown(f"**Last Sync Time:** `{sync_meta['last_sync_time'] or 'Never'}`")
    st.markdown(f"**Current Status:** `{sync_meta['status']}`")
    if sync_meta.get("is_sample_data"):
        st.warning("🏷️ Active Dataset: **Sample / Demo Mode**")
    elif sync_meta.get("status") == "Success":
        st.success("🏷️ Active Dataset: **Live SportRadar API**")

with status_col2:
    logs = sync_meta.get("logs", [])
    if logs:
        st.text_area("Operational Logs", value="\n".join(logs), height=140, disabled=True)
    else:
        st.caption("No sync logs recorded in this session yet.")

