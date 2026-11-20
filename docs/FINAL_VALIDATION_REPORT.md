# Final validation report

Release validation performed in the build environment:

| Check | Result |
|---|---|
| `python run_all.py` | Passed — all five analysis/export scripts completed |
| `python -m unittest discover -s tests -v` | Passed — 6 tests |
| Python syntax compilation | Passed — 9 Python files checked |
| SQLite database build | Passed — four tables created |
| SQLite query pack | Passed — all six query statements executed |
| MoRTH national-total reconciliation | Passed — 10/10 annual measure totals match the source report |
| RBI fiscal series integrity | Passed — estimate labels retained; unavailable 2019-20 fields remain null |

## Checks not performed in this environment
- Streamlit was not installed in the build environment, so the app source was syntax-checked but not launched in a browser.
- PostgreSQL server execution was not available; PostgreSQL scripts are supplied but should be run in a local PostgreSQL instance.
- Power BI Desktop and Tableau Desktop were not available. Native `.pbix` and `.twbx` files are therefore not included or validated.
- The Streamlit dashboard and native BI desktop dashboards require final user-side visual review.

This report distinguishes automated code/data checks from application-level visual QA.
