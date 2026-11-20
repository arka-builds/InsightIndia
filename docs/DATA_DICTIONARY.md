# Data dictionary

## Project 01 — Synthetic e-commerce orders (`india_ecommerce_orders_demo.csv`)
- `order_id`: synthetic unique order key
- `order_date`: order date
- `state`, `city`: illustrative Indian geography labels
- `category`, `order_status`, `payment_method`: categorical descriptors
- `quantity`, `unit_price_inr`, `order_value_inr`: order measures in INR
- `shipping_days`, `is_late_delivery`: simulated fulfilment measures
- `review_score`: simulated 1–5 rating
- `customer_id`: synthetic customer key
- **Provenance:** generated synthetic case data, not marketplace records.

## Project 02 — MoRTH road safety (`morth_road_accidents_state_2019_2023.csv`)
- `year`: calendar year 2019–2023
- `state_ut`: state or union territory label as published
- `metric`: `accidents` or `persons_killed`
- `value`: official reported count; blank when not reported in the source table
- `source`: report title and table reference
- `data_status`: `official_reported` or `not_reported`

## Project 03 — RBI consolidated fiscal data (`rbi_consolidated_state_finances_2019_2026.csv`)
- `fiscal_year`: fiscal period label
- `*_lakh_crore`: consolidated amount in ₹ lakh crore
- `estimate_status`: Accounts/actual, Provisional Accounts, Revised Estimate, or Budget Estimate
- `source`: RBI publication and tables
- **Scope:** consolidated State/UT series; not a state-level panel.

## Project 04 — Synthetic marketing experiment (`india_marketing_ab_test_synthetic.csv`)
- `user_id`: synthetic randomized user key
- `experiment_group`: Control or Treatment
- `converted`: binary conversion outcome (0/1)
- `ad_spend_inr`: simulated advertising cost allocated to the row
- `channel`, `device`, `state`, `city_tier`: simulated segment descriptors

## Project 03 QA fixture (`rbi_finance_qa_injected_defects.csv`)
A deliberately modified copy of the RBI series with injected missing, negative and whitespace defects. It is only a test fixture.
