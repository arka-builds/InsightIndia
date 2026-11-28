-- InsightIndia 2.1 | Reusable views and materialized views
SET search_path TO insightindia;

-- Delivered orders only: the revenue-recognised population used across the project.
CREATE OR REPLACE VIEW v_delivered_orders AS
SELECT * FROM ecommerce_orders WHERE order_status = 'Delivered';

-- One row per customer with lifetime delivered metrics.
CREATE OR REPLACE VIEW v_customer_summary AS
SELECT customer_id,
       COUNT(*)                         AS delivered_orders,
       SUM(order_value_inr)             AS lifetime_revenue_inr,
       MIN(order_date)                  AS first_order_date,
       MAX(order_date)                  AS last_order_date
FROM v_delivered_orders
GROUP BY customer_id;

-- Pre-aggregated monthly sales (refresh with: REFRESH MATERIALIZED VIEW insightindia.mv_monthly_sales;)
DROP MATERIALIZED VIEW IF EXISTS mv_monthly_sales;
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT date_trunc('month', order_date)::date AS month,
       COUNT(*)                              AS delivered_orders,
       SUM(order_value_inr)                  AS revenue_inr,
       AVG(order_value_inr)                  AS avg_order_value_inr
FROM v_delivered_orders
GROUP BY 1;
CREATE UNIQUE INDEX idx_mv_monthly_sales ON mv_monthly_sales (month);
