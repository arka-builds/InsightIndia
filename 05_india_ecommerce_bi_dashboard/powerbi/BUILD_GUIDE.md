# Power BI dashboard build guide

1. Run `python 05_india_ecommerce_bi_dashboard/src/export_dashboard_data.py` from repository root.
2. Power BI Desktop → Get Data → Text/CSV → `data/processed/powerbi_table_orders.csv`; name the table `Orders`.
3. Set data types: `order_date` Date; `order_value_inr` Decimal; `is_late_delivery` Whole Number; `review_score` Decimal; `order_month` Text.
4. Create measures from `DAX_MEASURES.dax`.
5. Page 1 Executive Overview: KPI cards for Delivered Revenue, Delivered Orders, Average Order Value, Late Delivery Rate; line chart for monthly revenue; bar chart for category revenue.
6. Page 2 Regional Performance: state revenue, order count, late-delivery rate; State slicer.
7. Page 3 Customer & Fulfilment: review score by late flag, shipping days vs review score, order-status mix, payment method.
8. Add slicers for State, Category, Payment Method, Order Date.
9. Add a visible data disclosure: `Synthetic demonstration data — not actual Indian marketplace transactions.`
10. Save as `India_Ecommerce_BI_Dashboard.pbix`.

A native `.pbix` is not bundled; create and validate it in Power BI Desktop.
