"""
Data Processing Module C: Doubles Competitor Rankings.
Transforms raw nested SportRadar doubles competitor rankings JSON into validated,
deduplicated Pandas DataFrames for competitors and their ranking positions.
"""

import logging
import pandas as pd
from typing import Dict, Any, Tuple
from utils.validators import validate_competitor_record, validate_ranking_record

logger = logging.getLogger(__name__)


def process_rankings_data(raw_json: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parses doubles competitor rankings JSON response.

    Extracts:
    1. Competitors:
       - competitor_id (PRIMARY KEY)
       - name
       - country
       - country_code
       - abbreviation
    2. Competitor_Rankings:
       - rank
       - movement
       - points
       - competitions_played
       - competitor_id (FOREIGN KEY)

    Returns:
        (competitors_df, rankings_df)
    """
    if not raw_json or not isinstance(raw_json, dict):
        logger.warning("Empty or non-dictionary rankings JSON provided.")
        return pd.DataFrame(), pd.DataFrame()

    # Sportradar doubles rankings can provide lists under 'rankings' or 'competitor_rankings'
    ranking_entries = []
    if "rankings" in raw_json and isinstance(raw_json["rankings"], list):
        for group in raw_json["rankings"]:
            if isinstance(group, dict):
                group_entries = group.get("competitor_rankings", [])
                if isinstance(group_entries, list):
                    ranking_entries.extend(group_entries)
    elif "competitor_rankings" in raw_json and isinstance(raw_json["competitor_rankings"], list):
        ranking_entries = raw_json["competitor_rankings"]

    competitors_map: Dict[str, Dict[str, Any]] = {}
    rankings_list = []

    for item in ranking_entries:
        if not isinstance(item, dict):
            continue

        comp_dict = item.get("competitor", {})
        if not isinstance(comp_dict, dict):
            continue

        competitor_id = str(comp_dict.get("id", "")).strip()
        comp_name = str(comp_dict.get("name", "")).strip()
        country = comp_dict.get("country")
        country_code = comp_dict.get("country_code")
        abbreviation = comp_dict.get("abbreviation")

        if not competitor_id or not comp_name:
            continue

        competitor_record = {
            "competitor_id": competitor_id,
            "name": comp_name,
            "country": str(country).strip() if country else None,
            "country_code": str(country_code).strip()[:10] if country_code else None,
            "abbreviation": str(abbreviation).strip()[:20] if abbreviation else None
        }

        if validate_competitor_record(competitor_record):
            if competitor_id not in competitors_map:
                competitors_map[competitor_id] = competitor_record

        # Extract Ranking Attributes
        try:
            rank = int(item.get("rank", 0))
            movement = int(item.get("movement", 0))
            points = int(item.get("points", 0))
            competitions_played = int(item.get("competitions_played", 0))
        except (ValueError, TypeError):
            continue

        ranking_record = {
            "rank": rank,
            "movement": movement,
            "points": points,
            "competitions_played": competitions_played,
            "competitor_id": competitor_id
        }

        if validate_ranking_record(ranking_record):
            rankings_list.append(ranking_record)

    competitors_df = pd.DataFrame(list(competitors_map.values()))
    if not competitors_df.empty:
        competitors_df = competitors_df.drop_duplicates(subset=["competitor_id"])

    rankings_df = pd.DataFrame(rankings_list)
    if not rankings_df.empty:
        # If there are duplicate ranks for the same competitor, retain highest points
        rankings_df = rankings_df.sort_values(by="points", ascending=False).drop_duplicates(subset=["competitor_id"])
        rankings_df = rankings_df.sort_values(by="rank", ascending=True)

    logger.info(
        f"Extracted {len(competitors_df)} competitors and {len(rankings_df)} rankings from raw API response."
    )
    return competitors_df, rankings_df

