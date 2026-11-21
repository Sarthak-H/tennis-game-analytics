"""
Database connection and session management module.
Provides SQLAlchemy engine creation with automatic MySQL verification and
safe fallback capability, transaction management, and schema initialization.
"""

import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import (
    MYSQL_DATABASE_URI,
    SQLITE_DATABASE_URI,
    FORCE_SQLITE,
    DB_NAME,
    DB_HOST,
    DB_PORT,
    DB_USER
)

logger = logging.getLogger(__name__)
Base = declarative_base()

# Global engine and session factory caches
_ENGINE = None
_SESSION_FACTORY = None
_ACTIVE_DIALECT = "unknown"

def get_engine():
    """
    Returns the SQLAlchemy engine.
    Attempts to connect to MySQL first. If MySQL is unreachable, falls back to
    SQLite and logs a clear operational notification.
    """
    global _ENGINE, _ACTIVE_DIALECT
    if _ENGINE is not None:
        return _ENGINE

    if FORCE_SQLITE:
        logger.info(f"Using forced SQLite database: {SQLITE_DATABASE_URI}")
        _ENGINE = create_engine(
            SQLITE_DATABASE_URI,
            connect_args={"check_same_thread": False},
            echo=False
        )
        _ACTIVE_DIALECT = "sqlite"
        return _ENGINE

    # Try connecting to MySQL
    try:
        mysql_engine = create_engine(
            MYSQL_DATABASE_URI,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Successfully connected to MySQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}.")
        _ENGINE = mysql_engine
        _ACTIVE_DIALECT = "mysql"
        return _ENGINE
    except Exception as exc:
        logger.warning(
            f"Unable to connect to MySQL at {DB_HOST}:{DB_PORT} ({exc}). "
            f"Engaging automatic local SQLite engine for continuous operation."
        )
        _ENGINE = create_engine(
            SQLITE_DATABASE_URI,
            connect_args={"check_same_thread": False},
            echo=False
        )
        _ACTIVE_DIALECT = "sqlite"
        return _ENGINE

def get_active_dialect() -> str:
    """Returns the current active database dialect ('mysql' or 'sqlite')."""
    if _ENGINE is None:
        get_engine()
    return _ACTIVE_DIALECT

def get_session_factory():
    """Returns thread-safe sessionmaker factory."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        engine = get_engine()
        _SESSION_FACTORY = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _SESSION_FACTORY

@contextmanager
def get_db_session():
    """
    Context manager providing a transactional database session.
    Commits on success, rolls back on exception, and automatically closes.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def check_database_connection():
    """
    Explicitly tests MySQL connectivity and returns status report:
    (is_mysql_connected, message, active_dialect, host_info)
    """
    try:
        test_engine = create_engine(MYSQL_DATABASE_URI, connect_args={"connect_timeout": 3})
        with test_engine.connect() as conn:
            res = conn.execute(text("SELECT VERSION()")).scalar()
        return True, f"Connected to MySQL {res} (Database: '{DB_NAME}')", "mysql", f"{DB_HOST}:{DB_PORT}"
    except Exception as exc:
        current_dialect = get_active_dialect()
        return (
            False,
            f"MySQL server offline or credentials invalid ({exc}). Active engine: {current_dialect.upper()}",
            current_dialect,
            f"{DB_HOST}:{DB_PORT}"
        )

def init_database():
    """
    Initializes all database tables using SQLAlchemy models.
    """
    engine = get_engine()
    # Import models so Base has all metadata
    import database.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

