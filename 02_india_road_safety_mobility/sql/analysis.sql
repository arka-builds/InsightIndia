-- PostgreSQL | MoRTH Road Accidents in India, 2019–2023
CREATE TABLE IF NOT EXISTS morth_road_safety (
    year SMALLINT NOT NULL,
    state_ut TEXT NOT NULL,
    metric TEXT NOT NULL CHECK (metric IN ('accidents','persons_killed')),
    value NUMERIC(12,0),  -- CSV stores counts as e.g. 21992.0, which BIGINT rejects on \copy
    source TEXT NOT NULL,
    data_status TEXT NOT NULL,
    PRIMARY KEY (year, state_ut, metric),
    CHECK (value IS NULL OR value >= 0)
);
-- Import:
-- \copy morth_road_safety FROM '02_india_road_safety_mobility/data/raw/morth_road_accidents_state_2019_2023.csv' CSV HEADER;

-- National totals (sum of state/UT records; check against the MoRTH table totals).
SELECT year, metric, SUM(value) AS india_total
FROM morth_road_safety
GROUP BY year, metric
ORDER BY year, metric;

-- Top 10 states/UTs in 2023.
WITH ranked AS (
  SELECT state_ut, metric, value,
         ROW_NUMBER() OVER (PARTITION BY metric ORDER BY value DESC) AS national_rank
  FROM morth_road_safety
  WHERE year = 2023
)
SELECT state_ut, metric, value, national_rank
FROM ranked
WHERE national_rank <= 10
ORDER BY metric, national_rank;

-- Year-on-year change by state/UT.
WITH yearly AS (
  SELECT state_ut, metric, year, value,
         LAG(value) OVER (PARTITION BY state_ut, metric ORDER BY year) AS prior_year
  FROM morth_road_safety
)
SELECT state_ut, metric, year, value, prior_year,
       ROUND(100.0 * (value - prior_year) / NULLIF(prior_year, 0), 2) AS yoy_change_pct
FROM yearly
WHERE year = 2023
ORDER BY metric, yoy_change_pct DESC NULLS LAST;
