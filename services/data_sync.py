"""
Data Synchronization Service.
Orchestrates API retrieval, data validation/transformation, and atomic relational upserts.
Also provides a dedicated sample dataset loading mode for evaluation when no API key is set.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from api.sportradar_client import SportRadarClient, SportRadarAPIError
from api.competitions import fetch_competitions_raw
from api.complexes import fetch_complexes_raw
from api.rankings import fetch_doubles_rankings_raw
from data_processing.competition_processor import process_competitions_data
from data_processing.venue_processor import process_complexes_data
from data_processing.ranking_processor import process_rankings_data
from database.crud import (
    upsert_categories,
    upsert_competitions,
    upsert_complexes,
    upsert_venues,
    upsert_competitors,
    upsert_rankings
)
from database.connection import init_database

logger = logging.getLogger(__name__)

# State tracking for last sync operation
_SYNC_METADATA = {
    "last_sync_time": None,
    "status": "Never Run",
    "is_sample_data": False,
    "stats": {},
    "logs": []
}


def log_sync_message(msg: str):
    """Appends to live synchronization log buffer."""
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    _SYNC_METADATA["logs"].append(entry)
    logger.info(msg)


def get_sync_metadata() -> Dict[str, Any]:
    """Returns status and metrics of last sync run."""
    return _SYNC_METADATA


def sync_competitions_service(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Syncs Competitions and Categories from Sportradar API into MySQL.
    """
    init_database()
    log_sync_message("Initiating Competitions & Categories synchronization...")
    raw = fetch_competitions_raw(client)
    cats_df, comps_df = process_competitions_data(raw)

    n_cats = upsert_categories(cats_df.to_dict(orient="records")) if not cats_df.empty else 0
    n_comps = upsert_competitions(comps_df.to_dict(orient="records")) if not comps_df.empty else 0

    log_sync_message(f"Competitions sync complete: {n_cats} categories, {n_comps} competitions saved.")
    return {"categories": n_cats, "competitions": n_comps}


def sync_complexes_service(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Syncs Complexes and Venues from Sportradar API into MySQL.
    """
    init_database()
    log_sync_message("Initiating Complexes & Venues synchronization...")
    raw = fetch_complexes_raw(client)
    complexes_df, venues_df = process_complexes_data(raw)

    n_complexes = upsert_complexes(complexes_df.to_dict(orient="records")) if not complexes_df.empty else 0
    n_venues = upsert_venues(venues_df.to_dict(orient="records")) if not venues_df.empty else 0

    log_sync_message(f"Complexes sync complete: {n_complexes} complexes, {n_venues} venues saved.")
    return {"complexes": n_complexes, "venues": n_venues}


def sync_rankings_service(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Syncs Doubles Competitor Rankings from Sportradar API into MySQL.
    """
    init_database()
    log_sync_message("Initiating Doubles Competitor Rankings synchronization...")
    raw = fetch_doubles_rankings_raw(client)
    competitors_df, rankings_df = process_rankings_data(raw)

    n_competitors = upsert_competitors(competitors_df.to_dict(orient="records")) if not competitors_df.empty else 0
    n_rankings = upsert_rankings(rankings_df.to_dict(orient="records")) if not rankings_df.empty else 0

    log_sync_message(f"Rankings sync complete: {n_competitors} competitors, {n_rankings} rankings saved.")
    return {"competitors": n_competitors, "rankings": n_rankings}


def sync_all_service(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Executes full end-to-end synchronization across all 3 modules.
    """
    if client is None:
        client = SportRadarClient()

    _SYNC_METADATA["logs"].clear()
    _SYNC_METADATA["status"] = "In Progress"
    start_time = datetime.utcnow()

    try:
        init_database()
        res_comp = sync_competitions_service(client)
        res_cplx = sync_complexes_service(client)
        res_rank = sync_rankings_service(client)

        _SYNC_METADATA["last_sync_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        _SYNC_METADATA["status"] = "Success"
        _SYNC_METADATA["is_sample_data"] = False
        _SYNC_METADATA["stats"] = {**res_comp, **res_cplx, **res_rank}
        log_sync_message("All modules successfully synchronized from official SportRadar API.")
        return {"success": True, "stats": _SYNC_METADATA["stats"]}

    except SportRadarAPIError as exc:
        _SYNC_METADATA["status"] = f"Failed: {exc.message}"
        log_sync_message(f"Sync failed due to API error: {exc.message}")
        return {"success": False, "error": str(exc.message)}
    except Exception as exc:
        _SYNC_METADATA["status"] = f"Error: {exc}"
        log_sync_message(f"Unexpected sync error: {exc}")
        return {"success": False, "error": str(exc)}


# ==============================================================================
# Sample Data Loader (For testing & offline evaluation when no API key is set)
# ==============================================================================

SAMPLE_DATA_PAYLOAD = {
    "categories": [
        {"category_id": "sr:category:1", "category_name": "Grand Slam"},
        {"category_id": "sr:category:2", "category_name": "ATP Tour"},
        {"category_id": "sr:category:3", "category_name": "WTA Tour"},
        {"category_id": "sr:category:4", "category_name": "ITF Men"},
        {"category_id": "sr:category:5", "category_name": "ITF Women"}
    ],
    "competitions": [
        {"competition_id": "sr:competition:1", "competition_name": "Wimbledon", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:2", "competition_name": "Wimbledon Men Doubles", "parent_id": "sr:competition:1", "type": "doubles", "gender": "men", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:3", "competition_name": "Wimbledon Women Doubles", "parent_id": "sr:competition:1", "type": "doubles", "gender": "women", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:4", "competition_name": "US Open", "parent_id": None, "type": "doubles", "gender": "mixed", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:5", "competition_name": "US Open Doubles Championship", "parent_id": "sr:competition:4", "type": "doubles", "gender": "men", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:6", "competition_name": "Roland Garros", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:7", "competition_name": "French Open Men Doubles", "parent_id": "sr:competition:6", "type": "doubles", "gender": "men", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:8", "competition_name": "Australian Open", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:1"},
        {"competition_id": "sr:competition:9", "competition_name": "ATP Masters 1000 Indian Wells", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:2"},
        {"competition_id": "sr:competition:10", "competition_name": "ATP Finals Turin", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:2"},
        {"competition_id": "sr:competition:11", "competition_name": "ITF M25 Madrid", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:4"},
        {"competition_id": "sr:competition:12", "competition_name": "ITF W35 Nonthaburi", "parent_id": None, "type": "doubles", "gender": "women", "category_id": "sr:category:5"},
        {"competition_id": "sr:competition:13", "competition_name": "Miami Open Doubles", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:2"},
        {"competition_id": "sr:competition:14", "competition_name": "Monte Carlo Masters Doubles", "parent_id": None, "type": "doubles", "gender": "men", "category_id": "sr:category:2"},
        {"competition_id": "sr:competition:15", "competition_name": "WTA Rome Doubles", "parent_id": None, "type": "doubles", "gender": "women", "category_id": "sr:category:3"}
    ],
    "complexes": [
        {"complex_id": "sr:complex:1", "complex_name": "All England Lawn Tennis and Croquet Club"},
        {"complex_id": "sr:complex:2", "complex_name": "USTA Billie Jean King National Tennis Center"},
        {"complex_id": "sr:complex:3", "complex_name": "Stade Roland Garros"},
        {"complex_id": "sr:complex:4", "complex_name": "Melbourne Park"},
        {"complex_id": "sr:complex:5", "complex_name": "Indian Wells Tennis Garden"}
    ],
    "venues": [
        {"venue_id": "sr:venue:1", "venue_name": "Centre Court", "city_name": "London", "country_name": "United Kingdom", "country_code": "GBR", "timezone": "Europe/London", "complex_id": "sr:complex:1"},
        {"venue_id": "sr:venue:2", "venue_name": "No. 1 Court", "city_name": "London", "country_name": "United Kingdom", "country_code": "GBR", "timezone": "Europe/London", "complex_id": "sr:complex:1"},
        {"venue_id": "sr:venue:3", "venue_name": "Arthur Ashe Stadium", "city_name": "New York", "country_name": "United States", "country_code": "USA", "timezone": "America/New_York", "complex_id": "sr:complex:2"},
        {"venue_id": "sr:venue:4", "venue_name": "Louis Armstrong Stadium", "city_name": "New York", "country_name": "United States", "country_code": "USA", "timezone": "America/New_York", "complex_id": "sr:complex:2"},
        {"venue_id": "sr:venue:5", "venue_name": "Court Philippe Chatrier", "city_name": "Paris", "country_name": "France", "country_code": "FRA", "timezone": "Europe/Paris", "complex_id": "sr:complex:3"},
        {"venue_id": "sr:venue:6", "venue_name": "Court Suzanne Lenglen", "city_name": "Paris", "country_name": "France", "country_code": "FRA", "timezone": "Europe/Paris", "complex_id": "sr:complex:3"},
        {"venue_id": "sr:venue:7", "venue_name": "Rod Laver Arena", "city_name": "Melbourne", "country_name": "Australia", "country_code": "AUS", "timezone": "Australia/Melbourne", "complex_id": "sr:complex:4"},
        {"venue_id": "sr:venue:8", "venue_name": "Margaret Court Arena", "city_name": "Melbourne", "country_name": "Australia", "country_code": "AUS", "timezone": "Australia/Melbourne", "complex_id": "sr:complex:4"},
        {"venue_id": "sr:venue:9", "venue_name": "Stadium 1", "city_name": "Indian Wells", "country_name": "United States", "country_code": "USA", "timezone": "America/Los_Angeles", "complex_id": "sr:complex:5"}
    ],
    "competitors": [
        {"competitor_id": "sr:competitor:101", "name": "Mektic, Nikola / Pavic, Mate", "country": "Croatia", "country_code": "CRO", "abbreviation": "MEK/PAV"},
        {"competitor_id": "sr:competitor:102", "name": "Ram, Rajeev / Salisbury, Joe", "country": "United States", "country_code": "USA", "abbreviation": "RAM/SAL"},
        {"competitor_id": "sr:competitor:103", "name": "Koolhof, Wesley / Skupski, Neal", "country": "Netherlands", "country_code": "NED", "abbreviation": "KOO/SKU"},
        {"competitor_id": "sr:competitor:104", "name": "Arevalo, Marcelo / Rojer, Jean-Julien", "country": "El Salvador", "country_code": "ESA", "abbreviation": "ARE/ROJ"},
        {"competitor_id": "sr:competitor:105", "name": "Glasspool, Lloyd / Heliovaara, Harri", "country": "United Kingdom", "country_code": "GBR", "abbreviation": "GLA/HEL"},
        {"competitor_id": "sr:competitor:106", "name": "Dodig, Ivan / Krajicek, Austin", "country": "Croatia", "country_code": "CRO", "abbreviation": "DOD/KRA"},
        {"competitor_id": "sr:competitor:107", "name": "Granollers, Marcel / Zeballos, Horacio", "country": "Spain", "country_code": "ESP", "abbreviation": "GRA/ZEB"},
        {"competitor_id": "sr:competitor:108", "name": "Bopanna, Rohan / Ebden, Matthew", "country": "India", "country_code": "IND", "abbreviation": "BOP/EBD"},
        {"competitor_id": "sr:competitor:109", "name": "Puetz, Tim / Krawietz, Kevin", "country": "Germany", "country_code": "GER", "abbreviation": "PUE/KRA"},
        {"competitor_id": "sr:competitor:110", "name": "Gonzalez, Maximo / Molteni, Andres", "country": "Argentina", "country_code": "ARG", "abbreviation": "GON/MOL"},
        {"competitor_id": "sr:competitor:111", "name": "Gille, Sander / Vliegen, Joran", "country": "Belgium", "country_code": "BEL", "abbreviation": "GIL/VLI"},
        {"competitor_id": "sr:competitor:112", "name": "Herbert, Pierre-Hugues / Mahut, Nicolas", "country": "France", "country_code": "FRA", "abbreviation": "HER/MAH"},
        {"competitor_id": "sr:competitor:113", "name": "Murray, Jamie / Venus, Michael", "country": "United Kingdom", "country_code": "GBR", "abbreviation": "MUR/VEN"},
        {"competitor_id": "sr:competitor:114", "name": "Lammons, Nathaniel / Withrow, Jackson", "country": "United States", "country_code": "USA", "abbreviation": "LAM/WIT"},
        {"competitor_id": "sr:competitor:115", "name": "Nys, Hugo / Zielinski, Jan", "country": "Monaco", "country_code": "MON", "abbreviation": "NYS/ZIE"},
        {"competitor_id": "sr:competitor:116", "name": "Cacic, Nikola / Brkic, Tomislav", "country": "Serbia", "country_code": "SRB", "abbreviation": "CAC/BRK"},
        {"competitor_id": "sr:competitor:117", "name": "Hidalgo, Diego / Rodriguez, Cristian", "country": "Ecuador", "country_code": "ECU", "abbreviation": "HID/ROD"},
        {"competitor_id": "sr:competitor:118", "name": "Barrientos, Nicolas / Behar, Ariel", "country": "Colombia", "country_code": "COL", "abbreviation": "BAR/BEH"},
        {"competitor_id": "sr:competitor:119", "name": "Matos, Rafael / Vega Hernandez, David", "country": "Brazil", "country_code": "BRA", "abbreviation": "MAT/VEG"},
        {"competitor_id": "sr:competitor:120", "name": "Venus, Michael / Puetz, Tim", "country": "New Zealand", "country_code": "NZL", "abbreviation": "VEN/PUE"}
    ],
    "rankings": [
        {"rank": 1, "movement": 0, "points": 8150, "competitions_played": 22, "competitor_id": "sr:competitor:101"},
        {"rank": 2, "movement": 1, "points": 7420, "competitions_played": 19, "competitor_id": "sr:competitor:102"},
        {"rank": 3, "movement": -1, "points": 7200, "competitions_played": 21, "competitor_id": "sr:competitor:103"},
        {"rank": 4, "movement": 0, "points": 6480, "competitions_played": 23, "competitor_id": "sr:competitor:104"},
        {"rank": 5, "movement": 2, "points": 5910, "competitions_played": 24, "competitor_id": "sr:competitor:105"},
        {"rank": 6, "movement": -1, "points": 5640, "competitions_played": 20, "competitor_id": "sr:competitor:106"},
        {"rank": 7, "movement": 0, "points": 5300, "competitions_played": 18, "competitor_id": "sr:competitor:107"},
        {"rank": 8, "movement": 3, "points": 4980, "competitions_played": 22, "competitor_id": "sr:competitor:108"},
        {"rank": 9, "movement": -2, "points": 4650, "competitions_played": 20, "competitor_id": "sr:competitor:109"},
        {"rank": 10, "movement": 1, "points": 4320, "competitions_played": 25, "competitor_id": "sr:competitor:110"},
        {"rank": 11, "movement": 0, "points": 3950, "competitions_played": 23, "competitor_id": "sr:competitor:111"},
        {"rank": 12, "movement": -2, "points": 3810, "competitions_played": 16, "competitor_id": "sr:competitor:112"},
        {"rank": 13, "movement": 1, "points": 3600, "competitions_played": 24, "competitor_id": "sr:competitor:113"},
        {"rank": 14, "movement": 4, "points": 3420, "competitions_played": 26, "competitor_id": "sr:competitor:114"},
        {"rank": 15, "movement": 0, "points": 3210, "competitions_played": 22, "competitor_id": "sr:competitor:115"},
        {"rank": 16, "movement": -1, "points": 2980, "competitions_played": 19, "competitor_id": "sr:competitor:116"},
        {"rank": 17, "movement": 2, "points": 2850, "competitions_played": 21, "competitor_id": "sr:competitor:117"},
        {"rank": 18, "movement": -3, "points": 2700, "competitions_played": 20, "competitor_id": "sr:competitor:118"},
        {"rank": 19, "movement": 1, "points": 2540, "competitions_played": 24, "competitor_id": "sr:competitor:119"},
        {"rank": 20, "movement": 0, "points": 2410, "competitions_played": 18, "competitor_id": "sr:competitor:120"}
    ]
}


def load_sample_dataset() -> Dict[str, Any]:
    """
    Populates database with official SportRadar-shaped sample data.
    Clearly marks dataset as Sample/Demo mode.
    """
    init_database()
    _SYNC_METADATA["logs"].clear()
    log_sync_message("Loading structured SportRadar-formatted sample dataset...")

    n_cats = upsert_categories(SAMPLE_DATA_PAYLOAD["categories"])
    n_comps = upsert_competitions(SAMPLE_DATA_PAYLOAD["competitions"])
    n_cplx = upsert_complexes(SAMPLE_DATA_PAYLOAD["complexes"])
    n_ven = upsert_venues(SAMPLE_DATA_PAYLOAD["venues"])
    n_cmpr = upsert_competitors(SAMPLE_DATA_PAYLOAD["competitors"])
    n_rank = upsert_rankings(SAMPLE_DATA_PAYLOAD["rankings"])

    _SYNC_METADATA["last_sync_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    _SYNC_METADATA["status"] = "Loaded Sample Data"
    _SYNC_METADATA["is_sample_data"] = True
    _SYNC_METADATA["stats"] = {
        "categories": n_cats,
        "competitions": n_comps,
        "complexes": n_cplx,
        "venues": n_ven,
        "competitors": n_cmpr,
        "rankings": n_rank
    }
    log_sync_message(f"Sample data loaded: {n_comps} competitions, {n_ven} venues, {n_rank} rankings.")
    return {"success": True, "stats": _SYNC_METADATA["stats"]}

