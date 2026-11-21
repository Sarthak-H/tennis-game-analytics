"""
API Module A: Competitions
Handles retrieval of competitions and categories from Sportradar API.
Reference: https://developer.sportradar.com/tennis/reference/competitions
"""

import logging
from typing import Dict, Any, Optional
from config import ENDPOINT_COMPETITIONS
from api.sportradar_client import SportRadarClient

logger = logging.getLogger(__name__)


def fetch_competitions_raw(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Fetches raw competitions and categories JSON from the SportRadar API.
    """
    if client is None:
        client = SportRadarClient()

    logger.info("Fetching tennis competitions from SportRadar API...")
    data = client.request(ENDPOINT_COMPETITIONS)
    return data

