"""
Helper utilities for UI formatting, logging, and data manipulation.
"""

import logging
from datetime import datetime
from typing import Optional

# Setup standard logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("tennis_analytics")

def format_number(val: Optional[int or float]) -> str:
    """Formats numbers with commas (e.g., 12,450)."""
    if val is None:
        return "0"
    try:
        return f"{int(val):,}"
    except (ValueError, TypeError):
        return str(val)

def format_movement(movement: int) -> str:
    """Formats ranking movement indicator with arrows."""
    if movement > 0:
        return f"▲ +{movement}"
    elif movement < 0:
        return f"▼ {movement}"
    else:
        return "— 0"

def get_current_timestamp() -> str:
    """Returns formatted UTC timestamp string."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

