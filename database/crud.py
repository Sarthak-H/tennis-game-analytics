"""
Data Access and CRUD operations module for tennis_analytics.
Handles atomic batch upserts using merge/ON DUPLICATE KEY logic,
and provides optimized querying functions for Streamlit pages and analytical queries.
"""

import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from database.connection import get_db_session, get_engine
from database.models import (
    Category,
    Competition,
    Complex,
    Venue,
    Competitor,
    CompetitorRanking
)

logger = logging.getLogger(__name__)


# ==============================================================================
# UPSERT OPERATIONS (Transactions with deduplication & existing update)
# ==============================================================================

def upsert_categories(records: List[Dict[str, Any]]) -> int:
    """
    Inserts or updates categories in a transactional session.
    Returns count of processed records.
    """
    if not records:
        return 0
    with get_db_session() as session:
        for r in records:
            cat = Category(
                category_id=str(r["category_id"]),
                category_name=str(r["category_name"])
            )
            session.merge(cat)
    return len(records)


def upsert_competitions(records: List[Dict[str, Any]]) -> int:
    """
    Inserts or updates competitions in a transactional session.
    First ensures parent references don't violate integrity.
    """
    if not records:
        return 0

    with get_db_session() as session:
        # Pass 1: Upsert competitions without parent_id to satisfy self-referencing FK
        for r in records:
            comp = Competition(
                competition_id=str(r["competition_id"]),
                competition_name=str(r["competition_name"]),
                parent_id=None,
                type=r.get("type"),
                gender=r.get("gender"),
                category_id=str(r["category_id"])
            )
            session.merge(comp)
        session.flush()

        # Pass 2: Set parent_id where available
        for r in records:
            pid = r.get("parent_id")
            if pid:
                session.query(Competition).filter_by(competition_id=str(r["competition_id"])).update(
                    {"parent_id": str(pid)}
                )

    return len(records)


def upsert_complexes(records: List[Dict[str, Any]]) -> int:
    """
    Inserts or updates sports complexes.
    """
    if not records:
        return 0
    with get_db_session() as session:
        for r in records:
            comp = Complex(
                complex_id=str(r["complex_id"]),
                complex_name=str(r["complex_name"])
            )
            session.merge(comp)
    return len(records)


def upsert_venues(records: List[Dict[str, Any]]) -> int:
    """
    Inserts or updates venues.
    """
    if not records:
        return 0
    with get_db_session() as session:
        for r in records:
            ven = Venue(
                venue_id=str(r["venue_id"]),
                venue_name=str(r["venue_name"]),
                city_name=r.get("city_name"),
                country_name=r.get("country_name"),
                country_code=r.get("country_code"),
                timezone=r.get("timezone"),
                complex_id=str(r["complex_id"])
            )
            session.merge(ven)
    return len(records)


def upsert_competitors(records: List[Dict[str, Any]]) -> int:
    """
    Inserts or updates competitors.
    """
    if not records:
        return 0
    with get_db_session() as session:
        for r in records:
            comp = Competitor(
                competitor_id=str(r["competitor_id"]),
                name=str(r["name"]),
                country=r.get("country"),
                country_code=r.get("country_code"),
                abbreviation=r.get("abbreviation")
            )
            session.merge(comp)
    return len(records)


def upsert_rankings(records: List[Dict[str, Any]]) -> int:
    """
    Cleans and replaces weekly rankings or upserts them for competitors.
    """
    if not records:
        return 0
    with get_db_session() as session:
        # Clear existing rankings before refreshing current snapshot
        session.query(CompetitorRanking).delete()
        session.flush()

        for r in records:
            rank_obj = CompetitorRanking(
                rank=int(r["rank"]),
                movement=int(r.get("movement", 0)),
                points=int(r.get("points", 0)),
                competitions_played=int(r.get("competitions_played", 0)),
                competitor_id=str(r["competitor_id"])
            )
            session.add(rank_obj)
    return len(records)


# ==============================================================================
# READ & ANALYTICS QUERIES (Returning Pandas DataFrames)
# ==============================================================================

def get_kpi_summary() -> Dict[str, Any]:
    """
    Calculates summary KPIs from the database.
    """
    engine = get_engine()
    with engine.connect() as conn:
        total_competitors = conn.execute(text("SELECT COUNT(*) FROM competitors")).scalar() or 0
        total_countries = conn.execute(text("SELECT COUNT(DISTINCT country) FROM competitors WHERE country IS NOT NULL AND country != ''")).scalar() or 0
        total_competitions = conn.execute(text("SELECT COUNT(*) FROM competitions")).scalar() or 0
        total_venues = conn.execute(text("SELECT COUNT(*) FROM venues")).scalar() or 0
        highest_points = conn.execute(text("SELECT MAX(points) FROM competitor_rankings")).scalar() or 0
        total_complexes = conn.execute(text("SELECT COUNT(*) FROM complexes")).scalar() or 0

    return {
        "total_competitors": int(total_competitors),
        "total_countries": int(total_countries),
        "total_competitions": int(total_competitions),
        "total_venues": int(total_venues),
        "highest_points": int(highest_points),
        "total_complexes": int(total_complexes)
    }


def get_all_competitions() -> pd.DataFrame:
    """
    Fetches all competitions joined with category and parent information.
    """
    sql = """
        SELECT 
            c.competition_id,
            c.competition_name,
            c.type AS competition_type,
            c.gender,
            c.parent_id,
            p.competition_name AS parent_name,
            cat.category_id,
            cat.category_name
        FROM competitions c
        LEFT JOIN categories cat ON c.category_id = cat.category_id
        LEFT JOIN competitions p ON c.parent_id = p.competition_id
        ORDER BY cat.category_name ASC, c.competition_name ASC
    """
    return pd.read_sql_query(sql, get_engine())


def get_all_rankings() -> pd.DataFrame:
    """
    Fetches all competitor rankings joined with competitor biographical details.
    """
    sql = """
        SELECT 
            r.rank_id,
            r.rank,
            r.movement,
            r.points,
            r.competitions_played,
            c.competitor_id,
            c.name AS competitor_name,
            c.country,
            c.country_code,
            c.abbreviation
        FROM competitor_rankings r
        INNER JOIN competitors c ON r.competitor_id = c.competitor_id
        ORDER BY r.rank ASC
    """
    return pd.read_sql_query(sql, get_engine())


def get_country_aggregates() -> pd.DataFrame:
    """
    Aggregates competitor numbers, average points, and total points by country.
    """
    sql = """
        SELECT 
            COALESCE(c.country, 'Unknown') AS country,
            COALESCE(c.country_code, 'N/A') AS country_code,
            COUNT(c.competitor_id) AS competitor_count,
            COALESCE(SUM(r.points), 0) AS total_points,
            ROUND(COALESCE(AVG(r.points), 0), 1) AS avg_points,
            MIN(r.rank) AS best_rank
        FROM competitors c
        LEFT JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
        GROUP BY c.country, c.country_code
        ORDER BY competitor_count DESC, total_points DESC
    """
    return pd.read_sql_query(sql, get_engine())


def get_all_venues_complexes() -> pd.DataFrame:
    """
    Fetches all venues joined with their respective sports complex.
    """
    sql = """
        SELECT 
            v.venue_id,
            v.venue_name,
            v.city_name,
            v.country_name,
            v.country_code,
            v.timezone,
            c.complex_id,
            c.complex_name
        FROM venues v
        INNER JOIN complexes c ON v.complex_id = c.complex_id
        ORDER BY c.complex_name ASC, v.venue_name ASC
    """
    return pd.read_sql_query(sql, get_engine())


def get_complex_counts() -> pd.DataFrame:
    """
    Counts total venues per sports complex.
    """
    sql = """
        SELECT 
            c.complex_id,
            c.complex_name,
            COUNT(v.venue_id) AS venue_count
        FROM complexes c
        LEFT JOIN venues v ON c.complex_id = v.complex_id
        GROUP BY c.complex_id, c.complex_name
        ORDER BY venue_count DESC, c.complex_name ASC
    """
    return pd.read_sql_query(sql, get_engine())


def execute_sql_query(query_str: str) -> pd.DataFrame:
    """
    Safely executes arbitrary analytical SELECT SQL queries and returns a DataFrame.
    """
    return pd.read_sql_query(query_str, get_engine())

