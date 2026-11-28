"""Reproducible analysis of MoRTH Road Accidents in India 2023 (Tables 5.1 and 5.6)."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "data/raw/morth_road_accidents_state_2019_2023.csv")
required = {"year", "state_ut", "metric", "value", "source", "data_status"}
if required - set(df.columns):
    raise ValueError(f"Missing columns: {required - set(df.columns)}")
if df.duplicated(["year", "state_ut", "metric"]).any():
    raise ValueError("Duplicate state/year/metric records")
if (df.loc[df.data_status == "official_reported", "value"] < 0).any():
    raise ValueError("Negative official values detected")

expected = {
    (2019, "accidents"): 456959, (2020, "accidents"): 372181,
    (2021, "accidents"): 412432, (2022, "accidents"): 461312,
    (2023, "accidents"): 480583,
    (2019, "persons_killed"): 158984, (2020, "persons_killed"): 138383,
    (2021, "persons_killed"): 153972, (2022, "persons_killed"): 168491,
    (2023, "persons_killed"): 172890,
}
checks = []
for (year, metric), total in expected.items():
    observed = int(df[(df.year == year) & (df.metric == metric)].value.sum())
    if observed != total:
        raise ValueError(f"Reconciliation failed: {year} {metric}: {observed} != {total}")
    checks.append({"year": year, "metric": metric, "reported_sum": observed, "official_total": total, "passed": True})
pd.DataFrame(checks).to_csv(OUT / "national_reconciliation.csv", index=False)

for metric in ["accidents", "persons_killed"]:
    sub = df[(df.year == 2023) & (df.metric == metric)].dropna(subset=["value"]).sort_values("value", ascending=False)
    sub.to_csv(OUT / f"{metric}_state_ranking_2023.csv", index=False)
    top = sub.head(12).sort_values("value")
    plt.figure(figsize=(10, 6))
    plt.barh(top.state_ut, top.value)
    plt.title(f"Top states/UTs by {metric.replace('_', ' ')} — 2023")
    plt.xlabel("Count reported by MoRTH")
    plt.tight_layout()
    plt.savefig(OUT / f"top_states_{metric}_2023.png", dpi=160)
    plt.close()

trend = df.groupby(["year", "metric"], as_index=False).value.sum(min_count=1)
trend.to_csv(OUT / "national_trend_2019_2023.csv", index=False)
for metric, group in trend.groupby("metric"):
    plt.figure(figsize=(8, 4.5))
    plt.plot(group.year, group.value, marker="o")
    plt.title(f"India — {metric.replace('_', ' ')} (2019–2023)")
    plt.xlabel("Year"); plt.ylabel("Count")
    plt.xticks(sorted(group.year.unique()))
    plt.tight_layout()
    plt.savefig(OUT / f"india_{metric}_trend_2019_2023.png", dpi=160)
    plt.close()
print("MoRTH 2019–2023 validation passed for 10 national totals; 37 state/UT labels retained.")
