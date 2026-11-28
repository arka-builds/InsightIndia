# India E-commerce Sales, Delivery & Customer Analytics

## Business problem
Analyze order value, product mix, regional sales, fulfilment performance, and customer reviews for an India-oriented e-commerce operation.

## Questions
- Which states and categories contribute the most delivered revenue?
- How do monthly orders and revenue change over time?
- What is the relationship between late delivery and customer ratings?
- Which payment methods and order outcomes are most common?

## Stack
Python, Pandas, NumPy, Matplotlib, PostgreSQL, SQL.

## Run
`python src/analyze.py` from this folder. Dataset: `data/raw/india_ecommerce_orders_demo.csv`.

## Outputs
Monthly sales, state performance, category performance, and PNG charts in `outputs/`. SQL analysis is in `sql/analysis.sql`.

## Data caveat
The bundled order-level file is synthetic demonstration data with Indian state/city labels. Do not present its values as actual Indian e-commerce market statistics. See `data/SOURCE_REGISTER.md` for verified source options.
