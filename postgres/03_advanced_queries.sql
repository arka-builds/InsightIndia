-- InsightIndia 2.1 | Advanced SQL query pack (PostgreSQL 14+)
-- Run:  psql "$DATABASE_URL" -f postgres/03_advanced_queries.sql
-- Techniques: window functions, CTEs, cohorts, NTILE/RFM, percentile_cont, FILTER, LAG/LEAD,
--             cumulative distribution, and a two-proportion z-test written in pure SQL.
-- E-commerce and A/B data are SYNTHETIC; MoRTH and RBI data are OFFICIAL reported figures.
SET search_path TO insightindia;

-- ---------------------------------------------------------------------------
-- Q1. Monthly delivered revenue: MoM %, YoY %, 3-month moving average, running total
-- ---------------------------------------------------------------------------
WITH monthly AS (
    SELECT month, revenue_inr, delivered_orders FROM mv_monthly_sales
)
SELECT month,
       ROUND(revenue_inr, 0)                                                        AS revenue_inr,
       ROUND(100.0 * (revenue_inr / NULLIF(LAG(revenue_inr, 1)  OVER w, 0) - 1), 1) AS mom_pct,
       ROUND(100.0 * (revenue_inr / NULLIF(LAG(revenue_inr, 12) OVER w, 0) - 1), 1) AS yoy_pct,
       ROUND(AVG(revenue_inr) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0) AS moving_avg_3m,
       ROUND(SUM(revenue_inr) OVER (ORDER BY month), 0)                             AS running_total
FROM monthly
WINDOW w AS (ORDER BY month)
ORDER BY month;

-- ---------------------------------------------------------------------------
-- Q2. Top-3 categories per year by revenue, with share of the year (DENSE_RANK + window total)
-- ---------------------------------------------------------------------------
WITH cat_year AS (
    SELECT EXTRACT(YEAR FROM order_date)::int AS yr, category, SUM(order_value_inr) AS revenue
    FROM v_delivered_orders
    GROUP BY 1, 2
), ranked AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY yr ORDER BY revenue DESC) AS rnk,
              100.0 * revenue / SUM(revenue) OVER (PARTITION BY yr)      AS share_pct
    FROM cat_year
)
SELECT yr, rnk, category, ROUND(revenue, 0) AS revenue_inr, ROUND(share_pct, 1) AS share_pct
FROM ranked WHERE rnk <= 3 ORDER BY yr, rnk;

-- ---------------------------------------------------------------------------
-- Q3. Customer cohort retention: share of each first-order-month cohort that orders again
--     N months later (cohort analysis with CTEs and conditional aggregation)
-- ---------------------------------------------------------------------------
WITH first_order AS (
    SELECT customer_id, date_trunc('month', MIN(order_date))::date AS cohort_month
    FROM v_delivered_orders GROUP BY customer_id
), activity AS (
    SELECT DISTINCT o.customer_id, f.cohort_month,
           (EXTRACT(YEAR FROM age(date_trunc('month', o.order_date), f.cohort_month)) * 12
          + EXTRACT(MONTH FROM age(date_trunc('month', o.order_date), f.cohort_month)))::int AS months_since
    FROM v_delivered_orders o JOIN first_order f USING (customer_id)
), cohort_size AS (
    SELECT cohort_month, COUNT(*) AS customers FROM first_order GROUP BY 1
)
SELECT a.cohort_month, s.customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE a.months_since = 1)  / s.customers, 1) AS m1_retention_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE a.months_since = 3)  / s.customers, 1) AS m3_retention_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE a.months_since = 6)  / s.customers, 1) AS m6_retention_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE a.months_since = 12) / s.customers, 1) AS m12_retention_pct
FROM activity a JOIN cohort_size s USING (cohort_month)
GROUP BY a.cohort_month, s.customers
ORDER BY a.cohort_month;

-- ---------------------------------------------------------------------------
-- Q4. RFM segmentation with NTILE(5); "today" is the day after the last order in the data
-- ---------------------------------------------------------------------------
WITH snapshot AS (SELECT MAX(order_date) + 1 AS as_of FROM v_delivered_orders),
rfm AS (
    SELECT c.customer_id,
           (s.as_of - c.last_order_date)  AS recency_days,
           c.delivered_orders             AS frequency,
           c.lifetime_revenue_inr         AS monetary
    FROM v_customer_summary c CROSS JOIN snapshot s
), scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency_days DESC)              AS r_score,  -- 5 = most recent
           NTILE(5) OVER (ORDER BY frequency, monetary)            AS f_score,
           NTILE(5) OVER (ORDER BY monetary)                       AS m_score
    FROM rfm
)
SELECT CASE WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New / promising'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lapsed'
            ELSE 'Needs attention' END AS segment,
       COUNT(*)                         AS customers,
       ROUND(AVG(monetary), 0)          AS avg_lifetime_revenue_inr,
       ROUND(AVG(recency_days), 0)      AS avg_recency_days
FROM scored GROUP BY 1 ORDER BY customers DESC;

-- ---------------------------------------------------------------------------
-- Q5. Pareto: what share of delivered revenue comes from the top 20% of customers?
-- ---------------------------------------------------------------------------
WITH ranked AS (
    SELECT customer_id, lifetime_revenue_inr,
           SUM(lifetime_revenue_inr) OVER (ORDER BY lifetime_revenue_inr DESC, customer_id) AS cum_revenue,
           SUM(lifetime_revenue_inr) OVER ()                                                 AS total_revenue,
           ROW_NUMBER() OVER (ORDER BY lifetime_revenue_inr DESC, customer_id)               AS rn,
           COUNT(*) OVER ()                                                                  AS n
    FROM v_customer_summary
)
SELECT ROUND(100.0 * MAX(cum_revenue) FILTER (WHERE rn <= CEIL(0.2 * n)) / MAX(total_revenue), 1) AS top20pct_customers_revenue_share_pct,
       MAX(n) AS customers
FROM ranked;

-- ---------------------------------------------------------------------------
-- Q6. Order-value distribution by category: percentiles via ordered-set aggregates
-- ---------------------------------------------------------------------------
SELECT category,
       COUNT(*)                                                         AS orders,
       ROUND(AVG(order_value_inr), 0)                                   AS mean_inr,
       ROUND(percentile_cont(0.50) WITHIN GROUP (ORDER BY order_value_inr)::numeric, 0) AS median_inr,
       ROUND(percentile_cont(0.90) WITHIN GROUP (ORDER BY order_value_inr)::numeric, 0) AS p90_inr,
       ROUND(percentile_cont(0.99) WITHIN GROUP (ORDER BY order_value_inr)::numeric, 0) AS p99_inr
FROM v_delivered_orders
GROUP BY category ORDER BY median_inr DESC;

-- ---------------------------------------------------------------------------
-- Q7. State late-delivery rate vs national rate (min 30 orders), with rank and gap in pp
-- ---------------------------------------------------------------------------
WITH s AS (
    SELECT state, COUNT(*) AS orders, AVG(is_late_delivery::numeric) AS late_rate
    FROM v_delivered_orders GROUP BY state HAVING COUNT(*) >= 30
), nat AS (SELECT AVG(is_late_delivery::numeric) AS national_rate FROM v_delivered_orders)
SELECT RANK() OVER (ORDER BY late_rate DESC)             AS rank_worst,
       state, orders,
       ROUND(100 * late_rate, 1)                         AS late_pct,
       ROUND(100 * (late_rate - national_rate), 1)       AS gap_vs_national_pp
FROM s CROSS JOIN nat
ORDER BY rank_worst LIMIT 10;

-- ---------------------------------------------------------------------------
-- Q8. Review penalty of late delivery per category (FILTER aggregates)
-- ---------------------------------------------------------------------------
SELECT category,
       COUNT(*) FILTER (WHERE is_late_delivery = 1)                    AS late_orders,
       ROUND(AVG(review_score) FILTER (WHERE is_late_delivery = 0), 2) AS avg_review_on_time,
       ROUND(AVG(review_score) FILTER (WHERE is_late_delivery = 1), 2) AS avg_review_late,
       ROUND(AVG(review_score) FILTER (WHERE is_late_delivery = 0)
           - AVG(review_score) FILTER (WHERE is_late_delivery = 1), 2) AS review_gap
FROM v_delivered_orders
GROUP BY category ORDER BY review_gap DESC;

-- ---------------------------------------------------------------------------
-- Q9. MoRTH: state share of national total, 2019-2023 CAGR and fatalities per 100 accidents
--     (official reported counts; NULL = not reported, so CAGR is only computed when both ends exist)
-- ---------------------------------------------------------------------------
WITH wide AS (
    SELECT state_ut,
           MAX(value) FILTER (WHERE metric='accidents'      AND year=2019) AS acc_2019,
           MAX(value) FILTER (WHERE metric='accidents'      AND year=2023) AS acc_2023,
           MAX(value) FILTER (WHERE metric='persons_killed' AND year=2023) AS killed_2023
    FROM morth_road_safety GROUP BY state_ut
)
SELECT state_ut, acc_2023,
       ROUND(100.0 * acc_2023 / SUM(acc_2023) OVER (), 2)                         AS share_of_national_pct,
       ROUND(100 * (POWER(acc_2023 / NULLIF(acc_2019, 0), 1.0/4) - 1), 2)        AS accidents_cagr_2019_23_pct,
       ROUND(100.0 * killed_2023 / NULLIF(acc_2023, 0), 1)                        AS killed_per_100_accidents
FROM wide
WHERE acc_2023 IS NOT NULL
ORDER BY acc_2023 DESC LIMIT 10;

-- ---------------------------------------------------------------------------
-- Q10. MoRTH: the 8 largest 2023 year-over-year accident declines, vs the mean state change (LAG + window AVG)
-- ---------------------------------------------------------------------------
WITH yoy AS (
    SELECT state_ut, year, value,
           LAG(value) OVER (PARTITION BY state_ut ORDER BY year) AS prior
    FROM morth_road_safety WHERE metric = 'accidents'
), chg AS (
    SELECT state_ut, 100.0 * (value - prior) / NULLIF(prior, 0) AS pct
    FROM yoy WHERE year = 2023 AND prior IS NOT NULL AND value IS NOT NULL
)
SELECT state_ut, ROUND(pct, 1) AS yoy_pct,
       ROUND(AVG(pct) OVER (), 1) AS mean_state_yoy_pct,
       CASE WHEN pct < 0 THEN 'declined' ELSE 'rose' END AS direction
FROM chg ORDER BY pct LIMIT 8;

-- ---------------------------------------------------------------------------
-- Q11. RBI: capital-expenditure share and revenue balance, keeping estimate status visible
-- ---------------------------------------------------------------------------
SELECT fiscal_year, estimate_status,
       ROUND(100 * capital_expenditure_lakh_crore / NULLIF(aggregate_expenditure_lakh_crore, 0), 1) AS capex_share_pct,
       ROUND(revenue_receipts_lakh_crore - revenue_expenditure_lakh_crore, 1)                        AS revenue_balance_lakh_crore,
       ROUND(100 * interest_payments_lakh_crore / NULLIF(revenue_receipts_lakh_crore, 0), 1)         AS interest_to_receipts_pct
FROM rbi_consolidated_fiscal
ORDER BY fiscal_year;

-- ---------------------------------------------------------------------------
-- Q12. A/B test in SQL: two-proportion z-test and 95% CI of the difference, overall and per channel
--      (synthetic experiment; compare with 06_india_advanced_statistics outputs)
-- ---------------------------------------------------------------------------
WITH g AS (
    SELECT channel,
           SUM((experiment_group='Control')::int)                         AS n_c,
           SUM((experiment_group='Treatment')::int)                       AS n_t,
           SUM(converted) FILTER (WHERE experiment_group='Control')       AS x_c,
           SUM(converted) FILTER (WHERE experiment_group='Treatment')     AS x_t
    FROM marketing_experiment GROUP BY ROLLUP (channel)
), r AS (
    SELECT COALESCE(channel, 'ALL CHANNELS') AS channel, n_c, n_t, x_c, x_t,
           x_c::numeric / n_c AS p_c, x_t::numeric / n_t AS p_t,
           (x_c + x_t)::numeric / (n_c + n_t) AS p_pool
    FROM g
)
SELECT channel, n_c, n_t,
       ROUND(100 * p_c, 3) AS control_pct, ROUND(100 * p_t, 3) AS treatment_pct,
       ROUND(100 * (p_t - p_c), 3) AS diff_pp,
       ROUND(((p_t - p_c) / SQRT(p_pool * (1 - p_pool) * (1.0/n_c + 1.0/n_t)))::numeric, 3) AS z,
       ROUND(100 * (p_t - p_c - 1.96 * SQRT(p_c*(1-p_c)/n_c + p_t*(1-p_t)/n_t)), 3) AS ci95_low_pp,
       ROUND(100 * (p_t - p_c + 1.96 * SQRT(p_c*(1-p_c)/n_c + p_t*(1-p_t)/n_t)), 3) AS ci95_high_pp
FROM r ORDER BY (channel = 'ALL CHANNELS') DESC, channel;
