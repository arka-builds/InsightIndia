"""Analyze RBI's consolidated state-government fiscal indicators and QA fixture."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"; OUT.mkdir(exist_ok=True)
PROC = ROOT / "data/processed"; PROC.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "data/raw/rbi_consolidated_state_finances_2019_2026.csv")
required = {"fiscal_year", "revenue_receipts_lakh_crore", "aggregate_expenditure_lakh_crore",
            "revenue_expenditure_lakh_crore", "capital_expenditure_lakh_crore",
            "gross_fiscal_deficit_lakh_crore", "estimate_status"}
if required - set(df.columns):
    raise ValueError(f"Missing fields: {required - set(df.columns)}")
if df.fiscal_year.duplicated().any():
    raise ValueError("Fiscal year should be unique")
if df.fiscal_year.astype(str).str.strip().ne(df.fiscal_year.astype(str)).any():
    raise ValueError("Fiscal year labels contain leading/trailing whitespace")
# All values are consolidated across states/UTs; no state-level ranking is inferred.
df.to_csv(PROC / "rbi_consolidated_fiscal_trends_clean.csv", index=False)

qa = pd.read_csv(ROOT / "data/raw/rbi_finance_qa_injected_defects.csv")
checks = []
for field in ["revenue_expenditure_lakh_crore", "gross_fiscal_deficit_lakh_crore", "capital_expenditure_lakh_crore"]:
    numeric = pd.to_numeric(qa[field], errors="coerce")
    checks.append({"rule": f"{field}: non-null numeric", "failed_records": int(numeric.isna().sum()), "records_tested": len(qa)})
    checks.append({"rule": f"{field}: non-negative", "failed_records": int((numeric < 0).sum()), "records_tested": int(numeric.notna().sum())})
checks.append({"rule": "fiscal_year normalized", "failed_records": int(qa.fiscal_year.astype(str).str.strip().ne(qa.fiscal_year.astype(str)).sum()), "records_tested": len(qa)})
score = pd.DataFrame(checks)
score["passed_records"] = score.records_tested - score.failed_records
score["pass_rate_pct"] = score.passed_records / score.records_tested.replace(0, 1) * 100
score.to_csv(OUT / "data_quality_scorecard.csv", index=False)

# Derived fiscal indicators with explicit estimate labels.
df["capital_expenditure_share_pct"] = 100 * df.capital_expenditure_lakh_crore / df.aggregate_expenditure_lakh_crore
df["revenue_balance_lakh_crore"] = df.revenue_receipts_lakh_crore - df.revenue_expenditure_lakh_crore
df.to_csv(OUT / "fiscal_indicators_derived.csv", index=False)

plot = df.dropna(subset=["revenue_expenditure_lakh_crore", "capital_expenditure_lakh_crore"])
plt.figure(figsize=(10, 5.5))
plt.plot(plot.fiscal_year, plot.revenue_expenditure_lakh_crore, marker="o", label="Revenue expenditure")
plt.plot(plot.fiscal_year, plot.capital_expenditure_lakh_crore, marker="o", label="Capital expenditure")
plt.xticks(rotation=25); plt.ylabel("₹ lakh crore")
plt.title("Consolidated state-government expenditure — RBI")
plt.legend(); plt.tight_layout(); plt.savefig(OUT / "expenditure_trend.png", dpi=160); plt.close()

plt.figure(figsize=(10, 5.5))
plt.barh(score.rule, score.pass_rate_pct)
plt.xlim(0, 100); plt.xlabel("Pass rate (%)")
plt.title("Data-quality QA fixture — injected defects")
plt.tight_layout(); plt.savefig(OUT / "data_quality_scorecard.png", dpi=160); plt.close()
print(f"RBI series rows={len(df)}; official series values preserved; QA checks={len(score)}.")
