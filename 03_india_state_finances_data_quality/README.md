# India State Government Finances & Data Quality

**Business question:** How have consolidated state-government receipts, expenditure composition and deficit indicators evolved, and can a simple data-quality control suite detect common reporting defects?

## Data
RBI *State Finances: A Study of Budgets 2025-26*, Chapter II, Tables II.1–II.3. The extract covers consolidated State/UT totals; it is not a state-level comparison. Amounts are ₹ lakh crore. Accounts, PA, RE and BE labels are preserved. See `data/SOURCE_REGISTER.md`.

## Analysis
- Revenue receipts and revenue/capital expenditure trends.
- Capital expenditure share of aggregate expenditure.
- Revenue balance and fiscal-deficit indicators.
- QA fixture tests for missing numeric values, negative values and inconsistent labels.

## Run
`python 03_india_state_finances_data_quality/src/analyze.py`

## Important
The QA fixture contains intentionally injected defects. It is only for demonstrating data-quality validation and is never used as source data for fiscal findings.
