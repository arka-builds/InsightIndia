# InsightIndia
### Data Analytics & Business Intelligence Portfolio

**InsightIndia** is a reproducible analytics portfolio built around five project workstreams covering Indian e-commerce, road safety, public finance, digital marketing experiments, and business intelligence. It demonstrates how to turn raw data into validated analysis, useful metrics, clear visualisations, and business-facing recommendations.

> **Data integrity comes first.** This repository combines official public-source extracts with clearly labelled synthetic case-study data. E-commerce orders and the marketing A/B experiment are synthetic and must not be described as actual marketplace or campaign results. Road-safety figures are transcribed from the Ministry of Road Transport and Highways (MoRTH) report. Consolidated state-finance indicators are transcribed from the Reserve Bank of India (RBI) publication. The finance QA fixture deliberately contains injected defects and is used only to demonstrate validation controls.

## Project portfolio

| # | Project | Project type | What it demonstrates | Data provenance |
|---|---|---|---|---|
| 01 | India E-commerce Sales & Customer Analytics | Data Analytics Project | Data cleaning, EDA, sales and customer KPIs, category/state trends, delivery and review analysis | Synthetic case-study data |
| 02 | India Road Safety Analytics (2019–2023) | Public Data Analytics Project | State/UT comparisons, multi-year trends, data validation and reconciliation to national totals | Official MoRTH publication |
| 03 | State Government Finances & Data Quality | Financial Analytics Project | Receipts and expenditure analysis, fiscal deficit indicators, estimate-status handling and QA checks | Official RBI consolidated tables + separate injected-defect QA fixture |
| 04 | Digital Marketing A/B Testing | Statistical Analysis Project | Sample-ratio checks, conversion rates, confidence intervals, hypothesis testing and channel analysis | Synthetic randomized experiment |
| 05 | E-commerce BI Dashboard | Business Intelligence Project | Executive KPIs, customer/product mix, fulfilment analysis and filterable reporting views | Reuses Project 01 synthetic data |

**Scope note:** Project 05 is the BI/reporting layer built on Project 01's demo dataset. It is not a separate independent dataset or an additional independent business case. The portfolio therefore contains four analytical case studies and one dedicated BI dashboard workstream.

## Technology stack

- **Programming & analysis:** Python, Pandas, NumPy
- **Visualisation & dashboards:** Plotly, Matplotlib, Streamlit
- **Databases & querying:** SQL, SQLite, PostgreSQL-compatible query packs
- **Statistics:** SciPy, Statsmodels, confidence intervals and hypothesis testing
- **BI tools:** Power BI (import-ready CSV, DAX measures and build guide), Tableau (compatible extracts and build guide)
- **Quality & reproducibility:** Python `unittest`, schema checks, data-quality rules, source reconciliation and repeatable pipelines

## Run locally (Windows PowerShell)

1. Download or clone this repository from GitHub.
2. Open PowerShell **inside the `InsightIndia` project folder** — the folder containing `app.py` and `requirements.txt`.
3. Run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py run_all.py
py -m unittest discover -s tests -v
py database/build_database.py
py -m streamlit run app.py
```

If PowerShell blocks virtual-environment activation, use Command Prompt instead:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

**Important:** Do not run the install or Streamlit commands from the Downloads parent folder. First change into the extracted `InsightIndia` folder, for example:

```powershell
cd "$HOME\Downloads\InsightIndia"
```

If `py` is not recognised, install Python 3.10 or newer from the official Python website and enable the option to add Python to PATH, then reopen the terminal. The `py -m pip` form avoids relying on a standalone `pip` command being on PATH.

## What to open

- **Interactive dashboard:** run `py -m streamlit run app.py`
- **Static chart gallery:** open `dashboard_previews/index.html` in a browser
- **SQLite database:** `database/insightindia_analytics.sqlite` (rebuild with `py database/build_database.py`)
- **SQLite query pack:** `database/queries.sql`
- **Project-specific SQL:** `sql/analysis.sql` inside the relevant project folder
- **Power BI resources:** `05_india_ecommerce_bi_dashboard/powerbi/`
- **Tableau resources:** `05_india_ecommerce_bi_dashboard/tableau/`
- **Interview preparation:** `docs/INTERVIEW_PREPARATION.md`
- **Validation summary:** `docs/FINAL_VALIDATION_REPORT.md`
- **Data dictionary:** `docs/DATA_DICTIONARY.md`

## Power BI and Tableau deliverables

The repository includes Power BI import-ready data, DAX measures and a build guide, plus Tableau-compatible extracts and a build guide. Native `.pbix` and `.twbx` workbooks are **not included**. Create and validate those files in Power BI Desktop and Tableau Desktop before claiming that native dashboards have been delivered.

## How to position InsightIndia in interviews

- **Data Analyst roles:** focus on data cleaning, Python EDA, SQL, KPI definitions, data validation, trend analysis and dashboards.
- **Business Analyst roles:** focus on business questions, metric definitions, stakeholder-ready reporting, interpretation, recommendations and operational implications.
- **Analytics/BI roles:** explain the end-to-end workflow from source data and quality checks to analysis, visualisation and communication.

Always distinguish official-source observations from synthetic practice data. Do not present synthetic sales, delivery, customer, or A/B-test findings as real Indian market or campaign performance.

## Repository structure

```text
InsightIndia/
├── 01_india_ecommerce_analytics/
├── 02_india_road_safety_mobility/
├── 03_india_state_finances_data_quality/
├── 04_india_digital_marketing_ab_test/
├── 05_india_ecommerce_bi_dashboard/
├── database/
├── dashboard_previews/
├── docs/
├── tests/
├── app.py
├── requirements.txt
└── run_all.py
```

## License

Code is released under the MIT License. Dataset provenance, source citations, and any source-specific reuse conditions are documented in `DATA_LICENSE.md` and in each project's source register. The MIT license for code does not override third-party dataset terms.
