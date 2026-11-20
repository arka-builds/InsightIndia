# Release notes and verified boundaries

## Implemented in this release
- Five project folders with project READMEs, source registers, data dictionaries, Python scripts and SQL.
- MoRTH 2019–2023 state/UT road accident and fatality tables transcribed from the official 2023 report. All 10 annual measure totals reconcile to the published national totals.
- RBI consolidated state-government fiscal indicators from the 2025-26 report, with Accounts/PA/RE/BE labels preserved and unavailable fields left blank.
- Synthetic e-commerce case data and synthetic A/B experiment, both clearly disclosed.
- Injected-defect finance QA fixture, separate from official data.
- Streamlit dashboard source, static Plotly gallery, Power BI CSV/DAX assets, Tableau build guide.
- SQLite database builder, SQLite query pack, PostgreSQL query packs.
- Automated tests for data integrity, national-total reconciliation, source status labels and SQLite database creation.

## Not claimed as delivered
- Native Power BI `.pbix` workbook: not generated or validated in Power BI Desktop.
- Native Tableau `.twb/.twbx` workbook: not generated or validated in Tableau Desktop.
- Real Indian marketplace transaction data: e-commerce sample is synthetic.
- Real campaign experiment data: A/B sample is synthetic.
- State-level RBI fiscal rankings: finance series is consolidated across States/UTs and cannot support state-level comparisons.

## Local validation
Run:
```bash
python run_all.py
python -m unittest discover -s tests -v
python database/build_database.py
```
Then run `streamlit run app.py` and inspect each of the five pages in a browser. The local dashboard/browser check remains a user-side validation step.

## Dashboard refinement pass (November 2026)
- Fixed the State Government Finances dashboard crash by defining a safe ₹ lakh-crore formatter and handling unavailable fiscal fields.
- Added fiscal-year estimate-status context, clearer chart labels, derived fiscal interpretation, and the QA fixture disclosure.
- Added user-friendly labels, KPI definitions, sample-size context and business interpretation to E-commerce Analytics.
- Added year-over-year change and measure-specific labels to Road Safety Analytics.
- Added absolute conversion lift, confidence-interval visualization and a decision-focused interpretation to the synthetic A/B test.
- Rebuilt the fifth Streamlit page as a separate BI-style executive, customer/product and operations view. It reuses the Project 01 synthetic source data and is explicitly labelled as such; it is not claimed as an independent dataset.
- Python syntax validation, all five analysis pipelines and all six unit tests pass after the dashboard source changes.
- Streamlit is not installed in the build environment, so a live browser launch and interactive visual check remain pending on the user's machine after dependency installation.
