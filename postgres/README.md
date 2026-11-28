# PostgreSQL + Advanced SQL (InsightIndia 2.1)

## Quick start
```bash
docker compose -f postgres/docker-compose.yml up -d
export DATABASE_URL=postgresql://insight:insight@localhost:5432/insightindia   # PowerShell: $env:DATABASE_URL="..."
python postgres/load_postgres.py                 # schema + COPY bulk load + views
psql "$DATABASE_URL" -f postgres/03_advanced_queries.sql
```
Without Docker, point `DATABASE_URL` at any PostgreSQL 14+ database you can write to.

## Files
| File | Purpose |
|---|---|
| `01_schema.sql` | `insightindia` schema, typed tables, PK/CHECK constraints, B-tree and partial indexes (idempotent) |
| `02_views.sql` | `v_delivered_orders`, `v_customer_summary`, materialized view `mv_monthly_sales` |
| `03_advanced_queries.sql` | 12 interview-style queries |
| `load_postgres.py` | Re-runnable loader using `COPY` inside one transaction |

## Query pack
| # | Topic | Techniques |
|---|---|---|
| Q1 | Monthly revenue: MoM, YoY, moving average, running total | `LAG`, framed window `AVG`, `SUM OVER` |
| Q2 | Top-3 categories per year | `DENSE_RANK`, window share |
| Q3 | Cohort retention | CTEs, `age()`, `FILTER` |
| Q4 | RFM segmentation | `NTILE(5)`, `CASE` |
| Q5 | Pareto: revenue share of top 20% customers | cumulative window, `CEIL` |
| Q6 | Order-value percentiles by category | `percentile_cont ... WITHIN GROUP` |
| Q7 | State late-delivery rate vs national | `HAVING`, `RANK`, cross join |
| Q8 | Review penalty of late delivery | `FILTER` aggregates |
| Q9 | MoRTH state share, CAGR, severity | pivoting with `FILTER`, `POWER` |
| Q10 | Largest 2023 accident declines | `LAG`, window `AVG` |
| Q11 | RBI capex share and revenue balance with status | ratio columns, `NULLIF` |
| Q12 | Two-proportion z-test and CI in pure SQL | `ROLLUP`, `SQRT` (matches the Python result) |

## Notes
- E-commerce and A/B data are **synthetic**; MoRTH and RBI data are **official reported figures**.
- MoRTH `NULL` means "not reported", never zero; Q9 computes CAGR only when both end years exist.
- Run the integration test with `DATABASE_URL` set: `python -m pytest tests/test_v21.py`. Without it, only the static schema checks run.
