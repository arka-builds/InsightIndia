# Changelog

## 2.1.0
**New**
- `postgres/`: PostgreSQL 16 schema with constraints and indexes, views and a materialized view, Docker Compose file, `COPY`-based loader, and a 12-query advanced SQL pack (windows, cohorts, RFM, percentiles, pure-SQL z-test).
- `06_india_advanced_statistics/`: non-parametric tests with effect sizes, robust OLS, logistic regression, bootstrap, permutation and Bayesian A/B inference, power/MDE analysis, Bonferroni/Holm/BH correction, and a generated report.
- Streamlit page "06 · Advanced Statistics".
- `tests/test_v21.py`: schema-vs-CSV checks, live PostgreSQL integration test (when `DATABASE_URL` is set), statistics consistency and reproducibility tests.

**Fixed (from 2.0 review)**
- Project 05 SQL table definition now matches the 17-column CSV; Project 02 SQL `value` column accepts `21992.0`-style values.
- Streamlit: replaced removed `use_container_width` with `width='stretch'`; removed Arrow serialization error on the finance table; made A/B text and state late-delivery callouts data-driven.
- Power BI `Average Review` measure now delivered-only, consistent with Python/app figures.
