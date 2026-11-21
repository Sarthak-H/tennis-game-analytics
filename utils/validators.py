"""
Validation utilities for tennis data processing.
Ensures data integrity, correct formats, and validates API payloads.
"""

from typing import Dict, Any, List

def validate_category_record(record: Dict[str, Any]) -> bool:
    """Validates that a category record has required non-empty fields."""
    return bool(record.get("category_id") and record.get("category_name"))

def validate_competition_record(record: Dict[str, Any]) -> bool:
    """Validates that a competition record has non-empty ID, name, and category_id."""
    return bool(record.get("competition_id") and record.get("competition_name") and record.get("category_id"))

def validate_complex_record(record: Dict[str, Any]) -> bool:
    """Validates complex record."""
    return bool(record.get("complex_id") and record.get("complex_name"))

def validate_venue_record(record: Dict[str, Any]) -> bool:
    """Validates venue record."""
    return bool(record.get("venue_id") and record.get("venue_name") and record.get("complex_id"))

def validate_competitor_record(record: Dict[str, Any]) -> bool:
    """Validates competitor record."""
    return bool(record.get("competitor_id") and record.get("name"))

def validate_ranking_record(record: Dict[str, Any]) -> bool:
    """Validates ranking record."""
    try:
        rank = int(record.get("rank", 0))
        comp_id = str(record.get("competitor_id", "")).strip()
        return rank > 0 and len(comp_id) > 0
    except (ValueError, TypeError):
        return False

