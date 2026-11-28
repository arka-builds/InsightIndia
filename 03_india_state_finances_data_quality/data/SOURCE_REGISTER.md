# Data provenance — RBI state-government finances

## Primary source
Reserve Bank of India, *State Finances: A Study of Budgets 2025-26*, released 23 January 2026.
Official publication landing page: https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=State+Finances+%3A+A+Study+of+Budgets
Chapter II, Tables II.1–II.3:
- Table II.1: Major Deficit Indicators — All States and UTs with Legislature.
- Table II.2: Aggregate Receipts of State Governments and UTs.
- Table II.3: Expenditure Pattern of State Governments and UTs.

The included series is consolidated across states/UTs, not a state-level panel. Values are in ₹ lakh crore. Accounts/actual, Provisional Accounts (PA), Revised Estimates (RE), and Budget Estimates (BE) remain explicitly labelled. Revenue receipts and expenditure fields for 2019-20 are left blank because Table II.2/II.3 begins in 2020-21; no missing values are imputed.

## QA fixture
`rbi_finance_qa_injected_defects.csv` is a deliberately corrupted test copy created from the official-source series. It contains a missing numeric value, a negative deficit test value, and whitespace in a year label. It is not official data and must not be used for fiscal conclusions.

## Interpretation caveats
- Consolidated values cannot support state-by-state rankings.
- BE and RE are estimates, not final actual outcomes.
- Amounts are nominal, not adjusted for inflation or population.
- Fiscal deficit is shown as a positive magnitude in this extract, following RBI's presentation.
