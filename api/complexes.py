"""
API Module B: Complexes and Venues
Handles retrieval of sports complexes and associated tennis venues.
Reference: https://developer.sportradar.com/tennis/reference/complexes
"""

import logging
from typing import Dict, Any, Optional
from config import ENDPOINT_COMPLEXES
from api.sportradar_client import SportRadarClient

logger = logging.getLogger(__name__)


def fetch_complexes_raw(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Fetches raw tennis complexes and venue data from the SportRadar API.
    """
    if client is None:
        client = SportRadarClient()

    logger.info("Fetching tennis complexes and venues from SportRadar API...")
    data = client.request(ENDPOINT_COMPLEXES)
    return data

