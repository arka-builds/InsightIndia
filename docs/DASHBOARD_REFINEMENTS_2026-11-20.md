# Dashboard refinement changelog — 20 November 2026

This release refines the Streamlit presentation while retaining the existing project datasets and their provenance disclosures.

## Project 03 — State Government Finances
- Split the previously crowded fiscal chart into a receipts/expenditure chart and a fiscal-deficit-indicators chart.
- Kept Accounts/actual, RE, PA and BE status distinctions visible and left missing observations as gaps rather than connecting them.
- Reworked the data-quality scorecard into a horizontal chart with shorter, readable rule labels and failure-count hover details.
- Displayed unavailable values in the on-screen RBI table as `Not available`; the downloaded source CSV retains missing values as missing.

## Project 05 — E-commerce BI Dashboard
### Customer & product mix
- Added customer counts to the customer-mix chart hover details.
- Added delivered order counts and average order value to customer-segment comparisons.
- Replaced the always-visible customer-ID listing with an aggregate segment summary; retained a small customer-level sample inside an expander.
- Added a filter-aware customer insight describing repeat-customer share and revenue share.
- Defined repeat status as more than one delivered order within the currently filtered dataset, not lifetime customer status.

### Operations & fulfilment
- Added on-time delivery rate, late delivery rate, average shipping time and cancellation rate KPIs.
- Clarified that order status applies to all filtered orders, while delivery timing applies only to delivered orders.
- Added state-level late-delivery and average-shipping comparisons, including only states with at least 30 delivered orders in the current filtered sample.
- Added a filter-aware operational takeaway that recommends investigation rather than asserting an unproven cause.

## Validation and limitations
- All five project pipelines completed successfully.
- All six automated unit tests passed.
- `app.py` passed Python compilation.
- The interactive Streamlit app was not launched in this build environment because Streamlit is not installed here. Browser rendering, interactions, and responsiveness still require local verification after installing `requirements.txt`.
- No source datasets or official reported values were changed as part of these presentation refinements.
