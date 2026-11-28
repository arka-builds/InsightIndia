# 06 · Advanced Statistics (InsightIndia 2.1)

Statistical-inference layer on top of the existing synthetic datasets. **All results here describe synthetic data**: they demonstrate methods, not real Indian market or campaign behaviour.

Run: `python 06_india_advanced_statistics/src/analyze.py` (seeded, reproducible; ~10 s).

| Area | Methods | Output |
|---|---|---|
| Review vs late delivery | Mann-Whitney U + Cliff's delta, Spearman, bootstrap CI | `ecommerce_hypothesis_tests.csv`, `bootstrap_review_gap.csv` |
| Association | Chi-square + Cramér's V (payment, category, state), Kruskal-Wallis + ε², Brown-Forsythe | `ecommerce_hypothesis_tests.csv` |
| Regression | OLS with HC3 robust errors; logistic regression (odds ratios) | `review_ols_robust.csv`, `low_review_logit_odds_ratios.csv` |
| A/B inference | Newcombe-Wilson CI, permutation test, Bayesian beta-binomial | `ab_advanced_results.csv`, `permutation_null.png`, `bayesian_relative_lift.png` |
| Power planning | Observed power, minimum detectable effect, sample size for a 20% lift | `ab_advanced_results.csv` |
| Multiple testing | Bonferroni, Holm, Benjamini-Hochberg across 4 channels | `ab_channel_multiple_testing.csv`, `multiple_testing.png` |

A plain-language summary is written to `outputs/STATISTICS_REPORT.md`. The pure-SQL version of the A/B z-test (Q12 in `postgres/03_advanced_queries.sql`) reproduces the z-statistic computed here.

## Interview talking points
- Why a rank test for 1-5 review scores, and why report an effect size next to every p-value.
- p = 0.06 does not mean "no effect": the CI and the power analysis show the test was under-powered for a lift this small.
- Why channel-level wins need multiple-testing correction before anyone acts on them.
