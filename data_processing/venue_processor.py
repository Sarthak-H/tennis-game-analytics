"""
Data Processing Module B: Complexes and Venues.
Transforms raw nested SportRadar complexes JSON into validated, deduplicated
Pandas DataFrames for sports complexes and their associated tennis court venues.
"""

import logging
import pandas as pd
from typing import Dict, Any, Tuple
from utils.validators import validate_complex_record, validate_venue_record

logger = logging.getLogger(__name__)


def process_complexes_data(raw_json: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parses nested sports complexes and venues JSON response.

    Extracts:
    1. Complexes:
       - complex_id (PRIMARY KEY)
       - complex_name
    2. Venues:
       - venue_id (PRIMARY KEY)
       - venue_name
       - city_name
       - country_name
       - country_code
       - timezone
       - complex_id (FOREIGN KEY)

    Returns:
        (complexes_df, venues_df)
    """
    if not raw_json or not isinstance(raw_json, dict):
        logger.warning("Empty or non-dictionary complexes JSON provided.")
        return pd.DataFrame(), pd.DataFrame()

    complexes_raw = raw_json.get("complexes", [])
    if not isinstance(complexes_raw, list):
        logger.warning(f"Unexpected complexes structure. Keys: {list(raw_json.keys())}")
        return pd.DataFrame(), pd.DataFrame()

    complexes_list = []
    venues_list = []

    for comp_item in complexes_raw:
        if not isinstance(comp_item, dict):
            continue

        complex_id = str(comp_item.get("id", "")).strip()
        complex_name = str(comp_item.get("name", "")).strip()

        complex_record = {
            "complex_id": complex_id,
            "complex_name": complex_name
        }

        if not validate_complex_record(complex_record):
            continue

        complexes_list.append(complex_record)

        # Process nested venues
        raw_venues = comp_item.get("venues", [])
        if isinstance(raw_venues, list):
            for v in raw_venues:
                if not isinstance(v, dict):
                    continue

                v_id = str(v.get("id", "")).strip()
                v_name = str(v.get("name", "")).strip()

                # Extract city
                city_name = v.get("city_name")
                if not city_name and isinstance(v.get("city"), dict):
                    city_name = v["city"].get("name")

                # Extract country
                country_name = v.get("country_name")
                country_code = v.get("country_code")
                if isinstance(v.get("country"), dict):
                    if not country_name:
                        country_name = v["country"].get("name")
                    if not country_code:
                        country_code = v["country"].get("code")

                # Timezone
                timezone = v.get("timezone")

                venue_record = {
                    "venue_id": v_id,
                    "venue_name": v_name,
                    "city_name": str(city_name).strip() if city_name else None,
                    "country_name": str(country_name).strip() if country_name else None,
                    "country_code": str(country_code).strip()[:10] if country_code else None,
                    "timezone": str(timezone).strip() if timezone else None,
                    "complex_id": complex_id
                }

                if validate_venue_record(venue_record):
                    venues_list.append(venue_record)

    complexes_df = pd.DataFrame(complexes_list)
    if not complexes_df.empty:
        complexes_df = complexes_df.drop_duplicates(subset=["complex_id"])

    venues_df = pd.DataFrame(venues_list)
    if not venues_df.empty:
        venues_df = venues_df.drop_duplicates(subset=["venue_id"])

    logger.info(
        f"Extracted {len(complexes_df)} complexes and {len(venues_df)} venues from raw API response."
    )
    return complexes_df, venues_df

