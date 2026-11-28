-- PostgreSQL | India E-commerce Analytics
CREATE TABLE IF NOT EXISTS dashboard_orders (order_id TEXT PRIMARY KEY, order_date DATE, state TEXT, city TEXT, category TEXT, order_status TEXT, payment_method TEXT, quantity INT, unit_price_inr NUMERIC(12,2), order_value_inr NUMERIC(14,2), shipping_days INT, is_late_delivery INT, review_score NUMERIC(2,1), customer_id TEXT, order_month TEXT, delivered_flag INT, late_delivery_flag INT);
-- Load CSV with psql after creating the table:
-- \copy dashboard_orders FROM '05_india_ecommerce_bi_dashboard/data/processed/powerbi_table_orders.csv' WITH (FORMAT csv, HEADER true);
-- 1. Monthly delivered revenue
SELECT date_trunc('month', order_date)::date AS month, COUNT(*) AS orders, SUM(order_value_inr) AS revenue_inr FROM dashboard_orders WHERE order_status='Delivered' GROUP BY 1 ORDER BY 1;
-- 2. State performance
SELECT state, COUNT(*) AS orders, SUM(order_value_inr) AS revenue_inr, AVG(is_late_delivery::numeric) AS late_delivery_rate, AVG(review_score) AS avg_review FROM dashboard_orders WHERE order_status='Delivered' GROUP BY state ORDER BY revenue_inr DESC;
-- 3. Delivery experience vs review
SELECT CASE WHEN is_late_delivery=1 THEN 'Late' ELSE 'On time' END AS delivery_group, COUNT(*) AS orders, AVG(review_score) AS avg_review FROM dashboard_orders WHERE order_status='Delivered' GROUP BY 1;
-- 4. Category contribution
SELECT category, SUM(order_value_inr) AS revenue_inr, COUNT(*) AS orders FROM dashboard_orders WHERE order_status='Delivered' GROUP BY category ORDER BY revenue_inr DESC;
