"""Advanced statistics for InsightIndia 2.1.

Part A (synthetic e-commerce): non-parametric tests, association tests with effect sizes,
                               regression with robust standard errors, bootstrap CIs.
Part B (synthetic A/B test):   effect-size CI, permutation test, Bayesian beta-binomial,
                               power / minimum detectable effect, multiple-testing correction.
All randomness is seeded, so results are reproducible. Data are SYNTHETIC: results illustrate
methods and must not be read as findings about real Indian markets or campaigns.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_confint, proportion_effectsize, proportions_ztest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
SEED = 2026
rng = np.random.default_rng(SEED)

orders = pd.read_csv(REPO / "01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv", parse_dates=["order_date"])
ab = pd.read_csv(REPO / "04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv")
delivered = orders[orders.order_status.eq("Delivered")].copy()


def cramers_v(table: pd.DataFrame) -> float:
    chi2 = stats.chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    return float(np.sqrt(chi2 / (n * (min(table.shape) - 1))))


def bootstrap_ci(values_a, values_b, stat=np.median, n_boot=2000):
    a, b = np.asarray(values_a), np.asarray(values_b)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = stat(rng.choice(a, a.size)) - stat(rng.choice(b, b.size))
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


# ---------------------------------------------------------------- Part A: e-commerce
rows = []
rev = delivered.dropna(subset=["review_score"])
late, ontime = rev[rev.is_late_delivery == 1].review_score, rev[rev.is_late_delivery == 0].review_score

u, p = stats.mannwhitneyu(late, ontime, alternative="two-sided")
cliffs_delta = 2 * u / (late.size * ontime.size) - 1  # P(late>ontime) - P(late<ontime)
rows.append(dict(test="Mann-Whitney U: review score, late vs on-time", statistic=u, p_value=p,
                 effect_size=cliffs_delta, effect_measure="Cliff's delta (late vs on-time)",
                 n=int(late.size + ontime.size),
                 note="Ordinal 1-5 scores, so a rank test is used instead of a t-test."))

rho, p = stats.spearmanr(rev.shipping_days, rev.review_score)
rows.append(dict(test="Spearman: shipping days vs review score", statistic=rho, p_value=p,
                 effect_size=rho, effect_measure="Spearman rho", n=len(rev), note="Monotonic association."))

for col in ["payment_method", "category", "state"]:
    table = pd.crosstab(delivered[col], delivered.is_late_delivery)
    chi2, p, dof, _ = stats.chi2_contingency(table)
    rows.append(dict(test=f"Chi-square: late delivery vs {col}", statistic=chi2, p_value=p,
                     effect_size=cramers_v(table), effect_measure="Cramer's V", n=int(table.to_numpy().sum()),
                     note=f"dof={dof}"))

groups = [g.order_value_inr.to_numpy() for _, g in delivered.groupby("category")]
h, p = stats.kruskal(*groups)
eps2 = (h - len(groups) + 1) / (len(delivered) - len(groups))
rows.append(dict(test="Kruskal-Wallis: order value across categories", statistic=h, p_value=p,
                 effect_size=eps2, effect_measure="epsilon-squared", n=len(delivered),
                 note="Order value is right-skewed, so medians/ranks are compared."))

ontime_slice = delivered[delivered.is_late_delivery == 0]
rows.append(dict(test="Levene (Brown-Forsythe): order-value variance, late vs on-time",
                 statistic=(lv := stats.levene(delivered[delivered.is_late_delivery == 1].order_value_inr,
                                               ontime_slice.order_value_inr, center="median")).statistic,
                 p_value=lv.pvalue, effect_size=np.nan, effect_measure="", n=len(delivered), note=""))
tests = pd.DataFrame(rows)
tests["significant_at_5pct"] = tests.p_value < 0.05
tests.to_csv(OUT / "ecommerce_hypothesis_tests.csv", index=False)

# OLS with heteroskedasticity-robust (HC3) errors; reference level = on-time, Cash on Delivery-like first level
model_df = rev.copy()
model_df["late"] = model_df.is_late_delivery
ols = smf.ols("review_score ~ late + shipping_days + C(category) + C(payment_method) + np.log(order_value_inr)",
              data=model_df).fit(cov_type="HC3")
coef = pd.DataFrame({"coef": ols.params, "std_err": ols.bse, "p_value": ols.pvalues,
                     "ci_low": ols.conf_int()[0], "ci_high": ols.conf_int()[1]}).reset_index(names="term")
coef.to_csv(OUT / "review_ols_robust.csv", index=False)

# Logistic regression: probability of a low review (<=2)
model_df["low_review"] = (model_df.review_score <= 2).astype(int)
logit = smf.logit("low_review ~ late + shipping_days + C(category)", data=model_df).fit(disp=0)
odds = pd.DataFrame({"odds_ratio": np.exp(logit.params), "ci_low": np.exp(logit.conf_int()[0]),
                     "ci_high": np.exp(logit.conf_int()[1]), "p_value": logit.pvalues}).reset_index(names="term")
odds.to_csv(OUT / "low_review_logit_odds_ratios.csv", index=False)

# Bootstrap CI for the mean review gap
bs_low, bs_high = bootstrap_ci(ontime, late, stat=np.mean)  # medians of 1-5 scores are too discrete for a useful CI
pd.DataFrame([dict(metric="mean review: on-time minus late", point_estimate=float(ontime.mean() - late.mean()),
                   ci95_low=bs_low, ci95_high=bs_high, n_boot=2000, seed=SEED)]).to_csv(OUT / "bootstrap_review_gap.csv", index=False)

# ---------------------------------------------------------------- Part B: A/B test
c = ab[ab.experiment_group == "Control"]
t = ab[ab.experiment_group == "Treatment"]
n_c, n_t, x_c, x_t = len(c), len(t), int(c.converted.sum()), int(t.converted.sum())
p_c, p_t = x_c / n_c, x_t / n_t
z, p_z = proportions_ztest([x_t, x_c], [n_t, n_c])

# Newcombe-Wilson (hybrid score) CI for the difference of proportions
l1, u1 = proportion_confint(x_t, n_t, method="wilson")
l2, u2 = proportion_confint(x_c, n_c, method="wilson")
d = p_t - p_c
nw_low = d - np.sqrt((p_t - l1) ** 2 + (u2 - p_c) ** 2)
nw_high = d + np.sqrt((u1 - p_t) ** 2 + (p_c - l2) ** 2)

# Permutation test on the difference in conversion rate
y = ab.converted.to_numpy()
is_t = (ab.experiment_group == "Treatment").to_numpy()
perm_stats = np.empty(10000)
for i in range(perm_stats.size):
    perm = rng.permutation(is_t)
    perm_stats[i] = y[perm].mean() - y[~perm].mean()
p_perm = float((np.abs(perm_stats) >= abs(d)).mean())

# Bayesian beta-binomial (uniform prior)
a_t, b_t, a_c, b_c = 1 + x_t, 1 + n_t - x_t, 1 + x_c, 1 + n_c - x_c
draws_t, draws_c = rng.beta(a_t, b_t, 200000), rng.beta(a_c, b_c, 200000)
prob_t_better = float((draws_t > draws_c).mean())
rel_lift_draws = draws_t / draws_c - 1
cred = np.percentile(rel_lift_draws, [2.5, 97.5])

# Power: sensitivity of THIS sample size and sample needed for a target lift
power_engine = NormalIndPower()
mde_es = power_engine.solve_power(nobs1=n_c, ratio=n_t / n_c, alpha=0.05, power=0.8)
# convert Cohen's h to an absolute lift at the control baseline
mde_rate = float(np.sin((2 * np.arcsin(np.sqrt(p_c)) + mde_es) / 2) ** 2)
observed_power = float(power_engine.power(proportion_effectsize(p_t, p_c), nobs1=n_c, ratio=n_t / n_c, alpha=0.05))
target_rel = 0.20
es_target = proportion_effectsize(p_c * (1 + target_rel), p_c)
n_needed = float(power_engine.solve_power(effect_size=es_target, alpha=0.05, power=0.8))

pd.DataFrame([dict(
    control_users=n_c, treatment_users=n_t, control_rate=p_c, treatment_rate=p_t,
    abs_lift_pp=100 * d, newcombe_ci95_low_pp=100 * nw_low, newcombe_ci95_high_pp=100 * nw_high,
    z_test_p_value=p_z, permutation_p_value=p_perm,
    bayes_prob_treatment_better=prob_t_better, bayes_rel_lift_ci95_low_pct=100 * cred[0], bayes_rel_lift_ci95_high_pct=100 * cred[1],
    observed_power=observed_power, mde_abs_pp_at_80pct_power=100 * (mde_rate - p_c),
    users_per_group_for_20pct_rel_lift=int(np.ceil(n_needed)), seed=SEED,
)]).to_csv(OUT / "ab_advanced_results.csv", index=False)

# Segment tests with multiple-testing correction (4 channels = 4 simultaneous tests)
seg_rows = []
for ch, g in ab.groupby("channel"):
    gc, gt = g[g.experiment_group == "Control"], g[g.experiment_group == "Treatment"]
    zc, pc = proportions_ztest([gt.converted.sum(), gc.converted.sum()], [len(gt), len(gc)])
    seg_rows.append(dict(channel=ch, control_users=len(gc), treatment_users=len(gt),
                         control_rate=gc.converted.mean(), treatment_rate=gt.converted.mean(),
                         abs_lift_pp=100 * (gt.converted.mean() - gc.converted.mean()), z=zc, p_raw=pc))
seg = pd.DataFrame(seg_rows)
for method, name in [("bonferroni", "p_bonferroni"), ("holm", "p_holm"), ("fdr_bh", "p_fdr_bh")]:
    seg[name] = multipletests(seg.p_raw, method=method)[1]
seg["significant_raw_5pct"] = seg.p_raw < 0.05
seg["significant_after_holm_5pct"] = seg.p_holm < 0.05
seg.to_csv(OUT / "ab_channel_multiple_testing.csv", index=False)

# ---------------------------------------------------------------- Figures
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(perm_stats * 100, bins=60, color="#9aa5b1")
ax.axvline(d * 100, color="crimson", lw=2, label=f"Observed lift = {d*100:.3f} pp")
ax.axvline(-d * 100, color="crimson", lw=2, ls="--")
ax.set(title="Permutation null distribution of conversion lift (synthetic)", xlabel="Difference in conversion rate (pp)", ylabel="Permutations")
ax.legend(); fig.tight_layout(); fig.savefig(OUT / "permutation_null.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(rel_lift_draws * 100, bins=80, color="#4c78a8")
ax.axvline(0, color="black", lw=1)
ax.set(title=f"Posterior of relative lift (P(treatment better) = {prob_t_better:.1%}) - synthetic",
       xlabel="Relative lift (%)", ylabel="Posterior draws")
fig.tight_layout(); fig.savefig(OUT / "bayesian_relative_lift.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(seg)); w = 0.38
ax.bar(x - w / 2, -np.log10(seg.p_raw), w, label="raw p", color="#9aa5b1")
ax.bar(x + w / 2, -np.log10(seg.p_holm), w, label="Holm-adjusted p", color="#4c78a8")
ax.axhline(-np.log10(0.05), color="crimson", ls="--", label="p = 0.05")
ax.set_xticks(x, seg.channel); ax.set(ylabel="-log10(p)", title="Channel-level lift tests before/after multiple-testing correction")
ax.legend(); fig.tight_layout(); fig.savefig(OUT / "multiple_testing.png", dpi=150); plt.close(fig)

def fmt_p(v):
    return 'p < 0.001' if v < 0.001 else f'p = {v:.3f}'


# ---------------------------------------------------------------- Report
report = f"""# Advanced statistics report (synthetic data)

*Generated by `06_india_advanced_statistics/src/analyze.py`, seed {SEED}. Synthetic data: methods demonstration only.*

## A/B test
- Control {p_c:.3%} (n={n_c:,}) vs treatment {p_t:.3%} (n={n_t:,}); absolute lift {100*d:+.3f} pp.
- Newcombe 95% CI for the difference: [{100*nw_low:+.3f}, {100*nw_high:+.3f}] pp. z-test p = {p_z:.4f}; permutation p = {p_perm:.4f}.
- Bayesian (uniform prior): P(treatment better) = {prob_t_better:.1%}; 95% credible interval for relative lift [{100*cred[0]:+.1f}%, {100*cred[1]:+.1f}%].
- Power: at this sample size the smallest lift detectable with 80% power is about {100*(mde_rate-p_c):.2f} pp; observed power for the observed lift is {observed_power:.0%}.
  Detecting a 20% relative lift would need about {int(np.ceil(n_needed)):,} users per group.
- Channel tests: {int(seg.significant_raw_5pct.sum())} of {len(seg)} significant before correction, {int(seg.significant_after_holm_5pct.sum())} after Holm correction.

## E-commerce
- Late deliveries carry a lower review score: Cliff's delta = {cliffs_delta:+.2f}; bootstrap 95% CI for the mean review gap (on-time minus late) [{bs_low:+.2f}, {bs_high:+.2f}] stars.
- In the robust OLS, `late` coefficient = {ols.params['late']:+.3f} stars (HC3 {fmt_p(ols.pvalues['late'])}), holding shipping days, category, payment method and order value fixed.
- Odds ratio of a low (<=2) review for late deliveries = {np.exp(logit.params['late']):.2f}.
- See `outputs/ecommerce_hypothesis_tests.csv` for all tests with effect sizes.

## Caveats
Statistical significance is not business value. Because every dataset here is simulated, the generating
assumptions drive the results; use these scripts as templates for first-party data.
"""
(OUT / "STATISTICS_REPORT.md").write_text(report, encoding="utf-8")
print(report)
