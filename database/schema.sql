-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- MySQL Relational Database Schema: tennis_analytics
-- =============================================================================

CREATE DATABASE IF NOT EXISTS tennis_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE tennis_analytics;

-- -----------------------------------------------------------------------------
-- 1. Categories Table
-- Stores high-level competition groupings (e.g., ATP, WTA, ITF Men, ITF Women)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id VARCHAR(50) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (category_id),
    INDEX idx_category_name (category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. Competitions Table
-- Stores competition details with hierarchical parent-child relationships
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competitions (
    competition_id VARCHAR(50) NOT NULL,
    competition_name VARCHAR(200) NOT NULL,
    parent_id VARCHAR(50) DEFAULT NULL,
    type VARCHAR(50) DEFAULT NULL,
    gender VARCHAR(20) DEFAULT NULL,
    category_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (competition_id),
    INDEX idx_comp_name (competition_name),
    INDEX idx_comp_type (type),
    INDEX idx_comp_gender (gender),
    INDEX idx_comp_parent (parent_id),
    INDEX idx_comp_category (category_id),
    CONSTRAINT fk_competitions_category
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_competitions_parent
        FOREIGN KEY (parent_id) REFERENCES competitions (competition_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. Complexes Table
-- Stores tennis complexes / sporting facilities
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complexes (
    complex_id VARCHAR(50) NOT NULL,
    complex_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (complex_id),
    INDEX idx_complex_name (complex_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. Venues Table
-- Stores court / stadium venues associated with a sports complex
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS venues (
    venue_id VARCHAR(50) NOT NULL,
    venue_name VARCHAR(150) NOT NULL,
    city_name VARCHAR(100) DEFAULT NULL,
    country_name VARCHAR(100) DEFAULT NULL,
    country_code VARCHAR(10) DEFAULT NULL,
    timezone VARCHAR(100) DEFAULT NULL,
    complex_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (venue_id),
    INDEX idx_venue_name (venue_name),
    INDEX idx_venue_country (country_name),
    INDEX idx_venue_country_code (country_code),
    INDEX idx_venue_complex (complex_id),
    CONSTRAINT fk_venues_complex
        FOREIGN KEY (complex_id) REFERENCES complexes (complex_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. Competitors Table
-- Stores player and doubles team identities
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competitors (
    competitor_id VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    country VARCHAR(100) DEFAULT NULL,
    country_code VARCHAR(10) DEFAULT NULL,
    abbreviation VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (competitor_id),
    INDEX idx_competitor_name (name),
    INDEX idx_competitor_country (country),
    INDEX idx_competitor_country_code (country_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. Competitor_Rankings Table
-- Stores weekly / current doubles rankings, points, and movements
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competitor_rankings (
    rank_id INT AUTO_INCREMENT NOT NULL,
    `rank` INT NOT NULL,
    movement INT NOT NULL DEFAULT 0,
    points INT NOT NULL DEFAULT 0,
    competitions_played INT NOT NULL DEFAULT 0,
    competitor_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (rank_id),
    INDEX idx_ranking_rank (`rank`),
    INDEX idx_ranking_points (points),
    INDEX idx_ranking_movement (movement),
    INDEX idx_ranking_competitor (competitor_id),
    CONSTRAINT fk_rankings_competitor
        FOREIGN KEY (competitor_id) REFERENCES competitors (competitor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

