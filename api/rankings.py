"""
API Module C: Doubles Competitor Rankings
Handles retrieval of doubles competitor rankings from Sportradar API.
Reference: https://developer.sportradar.com/tennis/reference/doubles-competitor-rankings
"""

import logging
from typing import Dict, Any, Optional
from config import ENDPOINT_DOUBLES_RANKINGS, ENDPOINT_DOUBLES_RANKINGS_ALT
from api.sportradar_client import SportRadarClient, SportRadarAPIError

logger = logging.getLogger(__name__)


def fetch_doubles_rankings_raw(client: Optional[SportRadarClient] = None) -> Dict[str, Any]:
    """
    Fetches raw doubles competitor rankings JSON from the SportRadar API.
    Tries primary official endpoint and handles fallback naming if necessary.
    """
    if client is None:
        client = SportRadarClient()

    logger.info("Fetching doubles competitor rankings from SportRadar API...")
    try:
        data = client.request(ENDPOINT_DOUBLES_RANKINGS)
        return data
    except SportRadarAPIError as exc:
        if exc.status_code == 404:
            logger.warning(f"Primary rankings endpoint {ENDPOINT_DOUBLES_RANKINGS} returned 404. Trying alternate {ENDPOINT_DOUBLES_RANKINGS_ALT}...")
            return client.request(ENDPOINT_DOUBLES_RANKINGS_ALT)
        raise

