"""
Unit tests for data processing modules:
1. competition_processor.py
2. venue_processor.py
3. ranking_processor.py
"""

try:
    import pytest
except ImportError:
    pass

import pandas as pd
from data_processing.competition_processor import process_competitions_data
from data_processing.venue_processor import process_complexes_data
from data_processing.ranking_processor import process_rankings_data


def test_process_competitions_valid():
    sample_json = {
        "competitions": [
            {
                "id": "sr:competition:1",
                "name": "Wimbledon",
                "parent_id": None,
                "type": "doubles",
                "gender": "men",
                "category": {
                    "id": "sr:category:1",
                    "name": "Grand Slam"
                }
            },
            {
                "id": "sr:competition:2",
                "name": "Wimbledon Men Doubles",
                "parent_id": "sr:competition:1",
                "type": "doubles",
                "gender": "men",
                "category": {
                    "id": "sr:category:1",
                    "name": "Grand Slam"
                }
            }
        ]
    }

    cats_df, comps_df = process_competitions_data(sample_json)

    assert not cats_df.empty
    assert len(cats_df) == 1
    assert cats_df.iloc[0]["category_id"] == "sr:category:1"
    assert cats_df.iloc[0]["category_name"] == "Grand Slam"

    assert not comps_df.empty
    assert len(comps_df) == 2
    assert "Wimbledon" in comps_df["competition_name"].values
    assert comps_df.loc[comps_df["competition_id"] == "sr:competition:2", "parent_id"].values[0] == "sr:competition:1"


def test_process_competitions_empty_and_corrupt():
    cats_df, comps_df = process_competitions_data({})
    assert cats_df.empty
    assert comps_df.empty

    cats_df, comps_df = process_competitions_data({"competitions": [{"invalid": 123}]})
    assert comps_df.empty


def test_process_complexes_valid():
    sample_json = {
        "complexes": [
            {
                "id": "sr:complex:1",
                "name": "Roland Garros",
                "venues": [
                    {
                        "id": "sr:venue:1",
                        "name": "Court Philippe Chatrier",
                        "city_name": "Paris",
                        "country_name": "France",
                        "country_code": "FRA",
                        "timezone": "Europe/Paris"
                    },
                    {
                        "id": "sr:venue:2",
                        "name": "Court Suzanne Lenglen",
                        "city": {"name": "Paris"},
                        "country": {"name": "France", "code": "FRA"},
                        "timezone": "Europe/Paris"
                    }
                ]
            }
        ]
    }

    cplx_df, ven_df = process_complexes_data(sample_json)

    assert not cplx_df.empty
    assert len(cplx_df) == 1
    assert cplx_df.iloc[0]["complex_name"] == "Roland Garros"

    assert not ven_df.empty
    assert len(ven_df) == 2
    assert ven_df.iloc[0]["complex_id"] == "sr:complex:1"
    assert ven_df.iloc[1]["city_name"] == "Paris"
    assert ven_df.iloc[1]["country_code"] == "FRA"


def test_process_rankings_valid():
    sample_json = {
        "rankings": [
            {
                "name": "ATP Doubles",
                "competitor_rankings": [
                    {
                        "rank": 1,
                        "movement": 0,
                        "points": 8000,
                        "competitions_played": 20,
                        "competitor": {
                            "id": "sr:competitor:101",
                            "name": "Mektic, Nikola / Pavic, Mate",
                            "country": "Croatia",
                            "country_code": "CRO",
                            "abbreviation": "MEK/PAV"
                        }
                    },
                    {
                        "rank": 2,
                        "movement": 1,
                        "points": 7500,
                        "competitions_played": 18,
                        "competitor": {
                            "id": "sr:competitor:102",
                            "name": "Ram, Rajeev / Salisbury, Joe",
                            "country": "United States",
                            "country_code": "USA",
                            "abbreviation": "RAM/SAL"
                        }
                    }
                ]
            }
        ]
    }

    cmpr_df, rank_df = process_rankings_data(sample_json)

    assert not cmpr_df.empty
    assert len(cmpr_df) == 2
    assert "Croatia" in cmpr_df["country"].values

    assert not rank_df.empty
    assert len(rank_df) == 2
    assert rank_df.iloc[0]["rank"] == 1
    assert rank_df.iloc[0]["points"] == 8000
    assert rank_df.iloc[0]["movement"] == 0
