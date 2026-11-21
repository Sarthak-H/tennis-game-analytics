"""
Configuration module for Tennis Game Analytics.
Loads environment variables and defines application constants, API endpoints,
and database connection strings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env from project directory
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# ==============================================================================
# SportRadar API Configuration
# ==============================================================================
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()
SPORTRADAR_ACCESS_LEVEL = os.getenv("SPORTRADAR_ACCESS_LEVEL", "trial").strip()
SPORTRADAR_VERSION = os.getenv("SPORTRADAR_VERSION", "v3").strip()
SPORTRADAR_LANGUAGE = os.getenv("SPORTRADAR_LANGUAGE", "en").strip()
SPORTRADAR_FORMAT = "json"

# Official Base URL format: https://api.sportradar.com/tennis/{access_level}/{version}/{language}
SPORTRADAR_BASE_URL = os.getenv(
    "SPORTRADAR_BASE_URL",
    f"https://api.sportradar.com/tennis/{SPORTRADAR_ACCESS_LEVEL}/{SPORTRADAR_VERSION}/{SPORTRADAR_LANGUAGE}"
).rstrip("/")

# Specific API Endpoints
# 1. Competitions: GET /tennis/{access_level}/{version}/{language}/competitions.{format}
ENDPOINT_COMPETITIONS = f"/competitions.{SPORTRADAR_FORMAT}"

# 2. Complexes & Venues: GET /tennis/{access_level}/{version}/{language}/complexes.{format}
ENDPOINT_COMPLEXES = f"/complexes.{SPORTRADAR_FORMAT}"

# 3. Doubles Competitor Rankings: GET /tennis/{access_level}/{version}/{language}/double_competitor_rankings.{format}
ENDPOINT_DOUBLES_RANKINGS = f"/double_competitor_rankings.{SPORTRADAR_FORMAT}"
ENDPOINT_DOUBLES_RANKINGS_ALT = f"/doubles_competitor_rankings.{SPORTRADAR_FORMAT}"

# Rate Limiting & Timeouts (Trial Tier: 1 call per second limit)
API_REQUEST_DELAY = float(os.getenv("API_REQUEST_DELAY", "1.2"))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))

# ==============================================================================
# Database Configuration (MySQL 8.x with SQLite Fallback)
# ==============================================================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "tennis_analytics")

# Primary MySQL SQLAlchemy Connection URI
MYSQL_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Fallback SQLite DB path (for tests, demonstration without active MySQL instance)
SQLITE_DB_PATH = BASE_DIR / "tennis_analytics.db"
SQLITE_DATABASE_URI = f"sqlite:///{SQLITE_DB_PATH}"

# Force fallback if set in environment
FORCE_SQLITE = os.getenv("FORCE_SQLITE", "false").lower() in ("true", "1", "yes")

# App settings
APP_TITLE = "Game Analytics: Unlocking Tennis Data"
APP_SUBTITLE = "SportRadar API • MySQL Relational Engine • Streamlit Visuals"
APP_VERSION = "1.0.0"

