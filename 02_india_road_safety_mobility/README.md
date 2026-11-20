# India Road Safety Analytics (2019–2023)

**Business question:** Which states/UTs account for the largest reported accident and fatality counts, and how did these counts change from 2019 to 2023?

## Data
Official MoRTH *Road Accidents in India 2023*, Tables 5.1 and 5.6. The cleaned long-form CSV is `data/raw/morth_road_accidents_state_2019_2023.csv` (37 state/UT labels × 5 years × 2 measures). See `data/SOURCE_REGISTER.md` for exact provenance and limitations.

## Methods
- Validate unique `(year, state_ut, metric)` keys and non-negative reported values.
- Reconcile every annual accident and fatality total to the official national totals.
- Rank states/UTs in 2023 and calculate annual trends and year-on-year changes.
- Export CSV summaries and charts.

## Run
From the repository root: `python 02_india_road_safety_mobility/src/analyze.py`

## SQL
`sql/analysis.sql` is PostgreSQL syntax. Import the CSV into `morth_road_safety` and run the queries. Note: `QUALIFY` is not supported by PostgreSQL; use the alternative `ROW_NUMBER()` CTE below if your PostgreSQL version rejects it.
