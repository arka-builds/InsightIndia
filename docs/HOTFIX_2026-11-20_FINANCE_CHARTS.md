# Hotfix — 20 November 2026

## State Government Finances chart error
The two fiscal trend charts previously passed `connectgaps=False` to `plotly.express.line()`. 
That keyword is not accepted by `px.line()` in the installed Plotly API and caused a runtime `TypeError`.

The charts now create the figure with `px.line()` and then apply `fig.update_traces(connectgaps=False)`.
This preserves the intended behaviour: missing observations remain gaps rather than being visually connected.

## Validation
- `app.py` parsed successfully.
- Automated test suite: 6/6 passed.
- ZIP integrity check passed after packaging.

The Streamlit app still needs to be launched locally to confirm the full interactive browser experience.
