"""
Unit tests for database connection, models, and CRUD operations.
Uses an isolated in-memory or temporary SQLite database to verify all operations.
"""

import os

try:
    import pytest
except ImportError:
    pass

from database.connection import Base
from database.crud import (
    upsert_categories,
    upsert_competitions,
    upsert_complexes,
    upsert_venues,
    upsert_competitors,
    upsert_rankings,
    get_kpi_summary,
    get_all_competitions,
    get_all_rankings,
    get_country_aggregates,
    get_all_venues_complexes
)
from services.data_sync import load_sample_dataset


def test_schema_and_upsert_operations():
    # Load the complete sample dataset into the active database engine
    res = load_sample_dataset()
    assert res["success"] is True

    # Test KPI Summary
    kpis = get_kpi_summary()
    assert kpis["total_competitors"] >= 20
    assert kpis["total_countries"] >= 5
    assert kpis["total_competitions"] >= 10
    assert kpis["total_venues"] >= 5
    assert kpis["highest_points"] >= 5000

    # Test Competitions Query
    comps_df = get_all_competitions()
    assert not comps_df.empty
    assert "Grand Slam" in comps_df["category_name"].values
    assert "Wimbledon" in comps_df["competition_name"].values

    # Test Rankings Query
    ranks_df = get_all_rankings()
    assert not ranks_df.empty
    assert len(ranks_df) >= 20
    assert ranks_df.iloc[0]["rank"] == 1
    assert "Mektic, Nikola / Pavic, Mate" in ranks_df["competitor_name"].values

    # Test Country Aggregates
    country_df = get_country_aggregates()
    assert not country_df.empty
    assert "Croatia" in country_df["country"].values

    # Test Venues and Complexes
    venues_df = get_all_venues_complexes()
    assert not venues_df.empty
    assert "Centre Court" in venues_df["venue_name"].values
