"""
SQLAlchemy ORM models for the tennis_analytics database.
Maps the 6 normalized relational tables:
1. categories
2. competitions
3. complexes
4. venues
5. competitors
6. competitor_rankings
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Index
)
from sqlalchemy.orm import relationship
from database.connection import Base

# -----------------------------------------------------------------------------
# 1. Categories
# -----------------------------------------------------------------------------
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String(50), primary_key=True, index=True)
    category_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    competitions = relationship("Competition", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id='{self.category_id}', name='{self.category_name}')>"


# -----------------------------------------------------------------------------
# 2. Competitions
# -----------------------------------------------------------------------------
class Competition(Base):
    __tablename__ = "competitions"

    competition_id = Column(String(50), primary_key=True, index=True)
    competition_name = Column(String(200), nullable=False, index=True)
    parent_id = Column(String(50), ForeignKey("competitions.competition_id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(String(50), nullable=True, index=True)
    gender = Column(String(20), nullable=True, index=True)
    category_id = Column(String(50), ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="competitions")
    parent = relationship("Competition", remote_side=[competition_id], backref="sub_competitions")

    def __repr__(self):
        return f"<Competition(id='{self.competition_id}', name='{self.competition_name}', type='{self.type}')>"


# -----------------------------------------------------------------------------
# 3. Complexes
# -----------------------------------------------------------------------------
class Complex(Base):
    __tablename__ = "complexes"

    complex_id = Column(String(50), primary_key=True, index=True)
    complex_name = Column(String(150), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    venues = relationship("Venue", back_populates="complex", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Complex(id='{self.complex_id}', name='{self.complex_name}')>"


# -----------------------------------------------------------------------------
# 4. Venues
# -----------------------------------------------------------------------------
class Venue(Base):
    __tablename__ = "venues"

    venue_id = Column(String(50), primary_key=True, index=True)
    venue_name = Column(String(150), nullable=False, index=True)
    city_name = Column(String(100), nullable=True)
    country_name = Column(String(100), nullable=True, index=True)
    country_code = Column(String(10), nullable=True, index=True)
    timezone = Column(String(100), nullable=True)
    complex_id = Column(String(50), ForeignKey("complexes.complex_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complex = relationship("Complex", back_populates="venues")

    def __repr__(self):
        return f"<Venue(id='{self.venue_id}', name='{self.venue_name}', city='{self.city_name}')>"


# -----------------------------------------------------------------------------
# 5. Competitors
# -----------------------------------------------------------------------------
class Competitor(Base):
    __tablename__ = "competitors"

    competitor_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    country = Column(String(100), nullable=True, index=True)
    country_code = Column(String(10), nullable=True, index=True)
    abbreviation = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rankings = relationship("CompetitorRanking", back_populates="competitor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Competitor(id='{self.competitor_id}', name='{self.name}', country='{self.country}')>"


# -----------------------------------------------------------------------------
# 6. Competitor_Rankings
# -----------------------------------------------------------------------------
class CompetitorRanking(Base):
    __tablename__ = "competitor_rankings"

    rank_id = Column(Integer, primary_key=True, autoincrement=True)
    rank = Column(Integer, nullable=False, index=True)
    movement = Column(Integer, nullable=False, default=0, index=True)
    points = Column(Integer, nullable=False, default=0, index=True)
    competitions_played = Column(Integer, nullable=False, default=0)
    competitor_id = Column(String(50), ForeignKey("competitors.competitor_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="rankings")

    def __repr__(self):
        return f"<CompetitorRanking(id={self.rank_id}, rank={self.rank}, competitor_id='{self.competitor_id}', points={self.points})>"

