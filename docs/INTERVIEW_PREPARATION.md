# Interview Preparation — Data Analyst & Business Analyst

## How to introduce the portfolio
"I built an India-focused analytics portfolio with four analytical case studies and a separate BI dashboard layer. The work covers retail analytics, public road-safety statistics, consolidated state-government finances, and a simulated marketing experiment. I used Python and SQL for analysis, validated official-source extracts against published totals, and created an interactive Streamlit dashboard plus Power BI/Tableau-ready assets. I clearly separate official statistics from synthetic case-study data."

## Project 01 — E-commerce analytics (synthetic case study)
**Data:** 18,000 generated illustrative order rows. Do not call these real Indian marketplace transactions.
**Questions:** Which states/categories contribute most to the demo revenue? How do delivery status and review scores vary? What data-quality issues should be checked?
**Explain:** order-level grain, unique order ID, revenue definition, delivered-only KPI filters, handling of cancelled/returned orders, missing review scores, and why synthetic results cannot be generalized to actual retailers.
**Data Analyst angle:** Pandas cleaning, groupby, SQL joins/aggregations, time series, KPI calculations.
**Business Analyst angle:** define revenue/fulfilment KPIs, interpret operational trade-offs, propose hypotheses to test with real retailer data.

## Project 02 — Road safety analytics (official MoRTH)
**Data:** MoRTH *Road Accidents in India 2023*, Tables 5.1 and 5.6, 2019–2023.
**Verified 2023 totals:** 480,583 accidents and 172,890 persons killed. The 2022 totals were 461,312 and 168,491 respectively.
**Published insights:** accidents rose 4.2% and fatalities rose 2.6% in 2023 over 2022. Tamil Nadu reported 67,213 accidents; Madhya Pradesh 55,327; Kerala 48,091. Uttar Pradesh recorded 23,652 fatalities, followed by Tamil Nadu 18,347 and Maharashtra 15,366.
**Questions:** Which states have the highest counts? Which states increased/decreased year over year? Do not call absolute counts "risk" without population, vehicle or traffic exposure denominators.
**Data Analyst angle:** long-form normalization, missing-value handling, window functions, ranking, reconciliation.
**Business Analyst angle:** prioritize further investigation, define fair comparison denominators, propose road-safety resource-allocation questions without causal claims.

## Project 03 — State government finances (official RBI consolidated data)
**Data:** RBI *State Finances: A Study of Budgets 2025-26*, Chapter II, Tables II.1–II.3. Consolidated States/UTs, not state-level panel data.
**Published insights:** 2025-26 budgeted aggregate expenditure ₹63.6 lakh crore; revenue expenditure ₹52.1 lakh crore; capital expenditure ₹11.4 lakh crore; gross fiscal deficit ₹11.8 lakh crore (3.3% of GDP). These are budget estimates, not actual outturns.
**Questions:** How has capital expenditure changed? What is the mix of revenue and capital spending? How do Accounts, PA, RE and BE differ?
**Data Analyst angle:** data modeling, data dictionary, fiscal ratios, trend charts, data-quality checks.
**Business Analyst angle:** explain trade-offs between recurring and asset-creating expenditure, communicate estimate-vs-actual uncertainty.

## Project 04 — Marketing A/B testing (synthetic experiment)
**Data:** generated 20,000-user randomized example; not a real campaign.
**Current sample result:** control conversion 2.716%, treatment 3.161%; absolute lift about 0.445 percentage points; two-sided p-value about 0.0623. At a 5% significance threshold this simulated result is not statistically significant.
**Questions:** What is the null hypothesis? Why use a two-proportion z-test? What does the p-value mean? Why is "not significant" not proof of no effect?
**Data Analyst angle:** group balance, conversion-rate denominator, Wilson intervals, statistical test assumptions.
**Business Analyst angle:** avoid rollout decisions from weak evidence; ask for a pre-registered experiment, adequate sample size, guardrail metrics and segmentation plan.

## Project 05 — BI dashboard
Project 05 is the dashboard presentation layer over Project 01's synthetic data. Explain the difference between a data model, measures, dimensions, filters and visuals. Be explicit that Power BI and Tableau native workbook files are not included; this repository includes import-ready assets and build guides.

## Resume wording (truthful)
- **India Road Safety Analytics | Python, SQL, Pandas, Plotly:** Analyzed MoRTH state/UT accident and fatality statistics for 2019–2023; validated 10 annual national totals and built state rankings and trend analysis.
- **India State Finance & Data Quality Analysis | Python, SQL, Pandas:** Analyzed RBI consolidated State/UT fiscal indicators; derived capital-expenditure shares and built QA checks for missing, invalid and inconsistent fields.
- **E-commerce Analytics Case Study | Python, SQL, Streamlit:** Built an end-to-end retail analytics case study using synthetic order data; developed sales, category, regional and fulfilment KPIs and documented the data limitations.
- **Marketing A/B Testing Simulation | Python, Statsmodels, SciPy:** Evaluated a synthetic randomized conversion experiment using confidence intervals and a two-proportion test; documented the non-significant result and decision limitations.

## Questions you should be able to answer
1. What is the grain of each dataset?
2. How did you validate uniqueness and missing values?
3. Why do you separate raw, processed and output data?
4. How did you reconcile the MoRTH national totals?
5. Why can't absolute accident counts be treated as risk?
6. Why must RBI BE, RE, PA and Accounts be kept separate?
7. What is the difference between statistical significance and business significance?
8. What does a p-value of 0.062 mean in the simulated experiment?
9. How would you design an actual A/B test for a retailer?
10. How would you convert a business question into KPIs and dashboard filters?
