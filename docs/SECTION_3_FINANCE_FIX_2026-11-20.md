# Section 3 — State Government Finances fix (20 November 2026)

## What was wrong
- The previous line-chart approach was visually confusing because the RBI series contains actuals, revised estimates (RE), provisional accounts (PA), and budget estimates (BE), including two different observations for 2024-25.
- A previous runtime issue passed `connectgaps` to `plotly.express.line`; the option belongs on traces, not the `px.line()` call.

## Changes made
- Replaced both line charts with grouped bar comparisons. This avoids drawing continuous trends through unlike reporting statuses.
- Fiscal-period labels now use concise suffixes: Actual, RE, PA, and BE. Full status wording remains available in hover details and the source table.
- Kept missing values missing; the charts omit unavailable observations rather than interpolating them.
- Clarified the fiscal interpretation so a negative revenue balance is explicitly described as a revenue deficit, while a positive balance is described as a surplus.
- Shortened the QA chart labels and added passed, failed, and tested record counts to hover details.
- Kept the RBI source values and source CSV unchanged.

## Validation
- `app.py` Python compilation passed.
- Both grouped fiscal charts and the QA chart were constructed successfully from the packaged data using Plotly.
- All six automated tests passed.
- `python run_all.py` completed all five project pipelines.
- Streamlit browser rendering still requires a local run; this environment does not provide a full interactive browser validation.
