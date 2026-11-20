-- SQLite query pack for the InsightIndia
-- Open database/insightindia_analytics.sqlite in DB Browser for SQLite or sqlite3.

-- 1. Synthetic e-commerce: monthly delivered revenue
SELECT substr(order_date, 1, 7) AS order_month,
       ROUND(SUM(order_value_inr), 2) AS delivered_revenue_inr,
       COUNT(DISTINCT order_id) AS delivered_orders
FROM ecommerce_orders_demo
WHERE order_status = 'Delivered'
GROUP BY substr(order_date, 1, 7)
ORDER BY order_month;

-- 2. Synthetic e-commerce: state profitability/revenue comparison
SELECT state, COUNT(DISTINCT order_id) AS delivered_orders,
       ROUND(SUM(order_value_inr), 2) AS delivered_revenue_inr,
       ROUND(AVG(review_score), 2) AS avg_review
FROM ecommerce_orders_demo
WHERE order_status = 'Delivered'
GROUP BY state
ORDER BY delivered_revenue_inr DESC;

-- 3. Official MoRTH: state/UT ranking by 2023 accidents
SELECT state_ut, value AS accidents,
       RANK() OVER (ORDER BY value DESC) AS national_rank
FROM morth_road_safety
WHERE year = 2023 AND metric = 'accidents' AND value IS NOT NULL
ORDER BY national_rank;

-- 4. Official MoRTH: 2019–2023 India total reconciliation
SELECT year, metric, SUM(value) AS reported_total
FROM morth_road_safety
GROUP BY year, metric
ORDER BY year, metric;

-- 5. Official RBI: capital expenditure share of aggregate expenditure
SELECT fiscal_year, estimate_status,
       ROUND(100.0 * capital_expenditure_lakh_crore /
             NULLIF(aggregate_expenditure_lakh_crore, 0), 2) AS capex_share_pct
FROM rbi_consolidated_fiscal
ORDER BY fiscal_year;

-- 6. Synthetic A/B case: conversion rate by experiment group
SELECT experiment_group, COUNT(*) AS users,
       SUM(converted) AS conversions,
       ROUND(100.0 * SUM(converted) / COUNT(*), 3) AS conversion_rate_pct
FROM marketing_ab_test_synthetic
GROUP BY experiment_group;
