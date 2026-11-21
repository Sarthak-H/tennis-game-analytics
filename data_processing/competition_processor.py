"""
Data Processing Module A: Competitions and Categories.
Transforms raw nested SportRadar competitions JSON into validated, deduplicated
Pandas DataFrames ready for relational database insertion.
"""

import logging
import pandas as pd
from typing import Dict, Any, Tuple
from utils.validators import validate_category_record, validate_competition_record

logger = logging.getLogger(__name__)


def process_competitions_data(raw_json: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parses nested competitions JSON response.

    Extracts:
    1. Categories:
       - category_id (PRIMARY KEY)
       - category_name
    2. Competitions:
       - competition_id (PRIMARY KEY)
       - competition_name
       - parent_id
       - type
       - gender
       - category_id (FOREIGN KEY)

    Returns:
        (categories_df, competitions_df)
    """
    if not raw_json or not isinstance(raw_json, dict):
        logger.warning("Empty or non-dictionary competitions JSON provided.")
        return pd.DataFrame(), pd.DataFrame()

    competitions_raw = raw_json.get("competitions", [])
    if not isinstance(competitions_raw, list):
        logger.warning(f"Unexpected competitions structure. Keys: {list(raw_json.keys())}")
        return pd.DataFrame(), pd.DataFrame()

    categories_map: Dict[str, Dict[str, Any]] = {}
    competitions_list = []

    for item in competitions_raw:
        if not isinstance(item, dict):
            continue

        comp_id = str(item.get("id", "")).strip()
        comp_name = str(item.get("name", "")).strip()

        # Extract Category
        cat_obj = item.get("category", {})
        if isinstance(cat_obj, dict):
            cat_id = str(cat_obj.get("id", "")).strip()
            cat_name = str(cat_obj.get("name", "")).strip()
        else:
            cat_id = str(item.get("category_id", "")).strip()
            cat_name = str(item.get("category_name", "")).strip()

        # If category ID is missing, assign a fallback grouping
        if not cat_id:
            cat_id = "sr:category:unknown"
            cat_name = "General Tennis"

        if cat_id not in categories_map:
            cat_record = {"category_id": cat_id, "category_name": cat_name or "Unknown Category"}
            if validate_category_record(cat_record):
                categories_map[cat_id] = cat_record

        # Extract Parent ID
        parent_id = item.get("parent_id")
        if not parent_id and isinstance(item.get("parent_competition"), dict):
            parent_id = item["parent_competition"].get("id")

        if parent_id:
            parent_id = str(parent_id).strip()
            # If parent_id refers to self, eliminate cyclical self-reference
            if parent_id == comp_id:
                parent_id = None
        else:
            parent_id = None

        # Extract Type & Gender
        comp_type = item.get("type")
        if comp_type:
            comp_type = str(comp_type).strip()

        gender = item.get("gender")
        if gender:
            gender = str(gender).strip()

        comp_record = {
            "competition_id": comp_id,
            "competition_name": comp_name,
            "parent_id": parent_id,
            "type": comp_type,
            "gender": gender,
            "category_id": cat_id
        }

        if validate_competition_record(comp_record):
            competitions_list.append(comp_record)

    # Convert to DataFrames and deduplicate
    categories_df = pd.DataFrame(list(categories_map.values()))
    if not categories_df.empty:
        categories_df = categories_df.drop_duplicates(subset=["category_id"])

    competitions_df = pd.DataFrame(competitions_list)
    if not competitions_df.empty:
        competitions_df = competitions_df.drop_duplicates(subset=["competition_id"])

    logger.info(
        f"Extracted {len(categories_df)} categories and {len(competitions_df)} competitions from raw API response."
    )
    return categories_df, competitions_df

