-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- SQL Data Analysis Queries
-- File: sql_queries/analysis_queries.sql
-- =============================================================================

-- =============================================================================
-- COMPETITION ANALYSIS
-- =============================================================================

-- 1. List all competitions along with their category name.
SELECT 
    c.competition_id,
    c.competition_name,
    c.type AS competition_type,
    c.gender,
    cat.category_name
FROM competitions c
INNER JOIN categories cat ON c.category_id = cat.category_id
ORDER BY cat.category_name ASC, c.competition_name ASC;

-- 2. Count the number of competitions in each category.
SELECT 
    cat.category_id,
    cat.category_name,
    COUNT(c.competition_id) AS total_competitions
FROM categories cat
LEFT JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY total_competitions DESC;

-- 3. Find all competitions of type doubles.
SELECT 
    c.competition_id,
    c.competition_name,
    c.gender,
    cat.category_name
FROM competitions c
LEFT JOIN categories cat ON c.category_id = cat.category_id
WHERE LOWER(c.type) = 'doubles'
ORDER BY c.competition_name ASC;

-- 4. Get competitions belonging to a specific category (e.g., 'ITF Men' or 'ATP').
SELECT 
    c.competition_id,
    c.competition_name,
    c.type AS competition_type,
    c.gender,
    cat.category_name
FROM competitions c
INNER JOIN categories cat ON c.category_id = cat.category_id
WHERE cat.category_name = 'ITF Men'
ORDER BY c.competition_name ASC;

-- 5. Identify parent competitions and their sub-competitions.
SELECT 
    parent.competition_id AS parent_competition_id,
    parent.competition_name AS parent_competition_name,
    child.competition_id AS sub_competition_id,
    child.competition_name AS sub_competition_name,
    child.type AS sub_competition_type
FROM competitions child
INNER JOIN competitions parent ON child.parent_id = parent.competition_id
ORDER BY parent.competition_name ASC, child.competition_name ASC;

-- 6. Analyze the distribution of competition types by category.
SELECT 
    cat.category_name,
    COALESCE(c.type, 'Unspecified') AS competition_type,
    COUNT(c.competition_id) AS competition_count
FROM categories cat
JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_name, COALESCE(c.type, 'Unspecified')
ORDER BY cat.category_name ASC, competition_count DESC;

-- 7. List all competitions with no parent (top-level competitions).
SELECT 
    c.competition_id,
    c.competition_name,
    c.type AS competition_type,
    c.gender,
    cat.category_name
FROM competitions c
LEFT JOIN categories cat ON c.category_id = cat.category_id
WHERE c.parent_id IS NULL OR c.parent_id = ''
ORDER BY c.competition_name ASC;


-- =============================================================================
-- VENUE AND COMPLEX ANALYSIS
-- =============================================================================

-- 1. List all venues along with their associated complex name.
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_name
FROM venues v
INNER JOIN complexes c ON v.complex_id = c.complex_id
ORDER BY c.complex_name ASC, v.venue_name ASC;

-- 2. Count the number of venues in each complex.
SELECT 
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS venue_count
FROM complexes c
LEFT JOIN venues v ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
ORDER BY venue_count DESC, c.complex_name ASC;

-- 3. Get venue details for a specific country (e.g., 'United States' or 'France').
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_name
FROM venues v
LEFT JOIN complexes c ON v.complex_id = c.complex_id
WHERE LOWER(v.country_name) = 'united states' OR LOWER(v.country_code) = 'usa'
ORDER BY v.city_name ASC, v.venue_name ASC;

-- 4. Identify all venues and their timezones.
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    COALESCE(v.timezone, 'Unknown') AS timezone
FROM venues v
ORDER BY timezone ASC, v.venue_name ASC;

-- 5. Find complexes that have more than one venue.
SELECT 
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS total_venues
FROM complexes c
INNER JOIN venues v ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY total_venues DESC, c.complex_name ASC;

-- 6. List venues grouped by country.
SELECT 
    COALESCE(v.country_name, 'Unknown Country') AS country_name,
    COALESCE(v.country_code, 'N/A') AS country_code,
    COUNT(v.venue_id) AS total_venues
FROM venues v
GROUP BY v.country_name, v.country_code
ORDER BY total_venues DESC, country_name ASC;

-- 7. Find all venues for a specific complex.
SELECT 
    c.complex_name,
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.timezone
FROM venues v
INNER JOIN complexes c ON v.complex_id = c.complex_id
WHERE c.complex_name LIKE '%Roland Garros%' OR c.complex_id = 'sr:complex:1'
ORDER BY v.venue_name ASC;


-- =============================================================================
-- COMPETITOR RANKING ANALYSIS
-- =============================================================================

-- 1. Get all competitors with their rank and points.
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    c.country_code,
    r.points,
    r.movement,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
ORDER BY r.rank ASC;

-- 2. Find competitors ranked in the top 5.
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    r.points,
    r.movement,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.rank <= 5
ORDER BY r.rank ASC;

-- 3. List competitors with no rank movement (stable rank).
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    r.points,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.movement = 0
ORDER BY r.rank ASC;

-- 4. Get total points of competitors from a specific country (e.g., 'Croatia').
SELECT 
    c.country,
    COUNT(c.competitor_id) AS total_players,
    SUM(r.points) AS total_points,
    ROUND(AVG(r.points), 2) AS average_points
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE LOWER(c.country) = 'croatia'
GROUP BY c.country;

-- 5. Count the number of competitors per country.
SELECT 
    COALESCE(c.country, 'Unknown') AS country,
    COALESCE(c.country_code, 'N/A') AS country_code,
    COUNT(c.competitor_id) AS competitor_count,
    SUM(r.points) AS total_points,
    ROUND(AVG(r.points), 2) AS avg_points
FROM competitors c
LEFT JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
GROUP BY c.country, c.country_code
ORDER BY competitor_count DESC, total_points DESC;

-- 6. Find competitors with the highest points in the current ranking dataset.
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    r.points,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
ORDER BY r.points DESC
LIMIT 10;

