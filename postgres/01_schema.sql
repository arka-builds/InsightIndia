-- InsightIndia 2.1 | PostgreSQL schema (typed tables, constraints, indexes)
-- Idempotent: safe to run repeatedly.
CREATE SCHEMA IF NOT EXISTS insightindia;
SET search_path TO insightindia;

-- Synthetic e-commerce case data (NOT real marketplace transactions)
CREATE TABLE IF NOT EXISTS ecommerce_orders (
    order_id          TEXT PRIMARY KEY,
    order_date        DATE          NOT NULL,
    state             TEXT          NOT NULL,
    city              TEXT          NOT NULL,
    category          TEXT          NOT NULL,
    order_status      TEXT          NOT NULL CHECK (order_status IN ('Delivered','Returned','Cancelled')),
    payment_method    TEXT          NOT NULL,
    quantity          INT           NOT NULL CHECK (quantity > 0),
    unit_price_inr    NUMERIC(12,2) NOT NULL CHECK (unit_price_inr >= 0),
    order_value_inr   NUMERIC(14,2) NOT NULL CHECK (order_value_inr >= 0),
    shipping_days     INT           NOT NULL CHECK (shipping_days >= 0),
    is_late_delivery  SMALLINT      NOT NULL CHECK (is_late_delivery IN (0,1)),
    review_score      NUMERIC(2,1)  CHECK (review_score BETWEEN 1 AND 5),
    customer_id       TEXT          NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_date     ON ecommerce_orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_state    ON ecommerce_orders (state);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON ecommerce_orders (customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_orders_delivered ON ecommerce_orders (order_date) WHERE order_status = 'Delivered';

-- Official MoRTH road accident counts (reported); NULL = not reported
CREATE TABLE IF NOT EXISTS morth_road_safety (
    year        SMALLINT NOT NULL,
    state_ut    TEXT     NOT NULL,
    metric      TEXT     NOT NULL CHECK (metric IN ('accidents','persons_killed')),
    value       NUMERIC(12,0) CHECK (value IS NULL OR value >= 0),
    source      TEXT     NOT NULL,
    data_status TEXT     NOT NULL,
    PRIMARY KEY (year, state_ut, metric)
);

-- Official RBI consolidated state-government finances (Rs lakh crore)
CREATE TABLE IF NOT EXISTS rbi_consolidated_fiscal (
    fiscal_year                      TEXT PRIMARY KEY,
    revenue_receipts_lakh_crore      NUMERIC,
    aggregate_expenditure_lakh_crore NUMERIC,
    revenue_expenditure_lakh_crore   NUMERIC,
    capital_expenditure_lakh_crore   NUMERIC,
    interest_payments_lakh_crore     NUMERIC,
    gross_fiscal_deficit_lakh_crore  NUMERIC,
    revenue_deficit_lakh_crore       NUMERIC,
    primary_deficit_lakh_crore       NUMERIC,
    estimate_status                  TEXT NOT NULL,
    source                           TEXT
);

-- Synthetic randomized marketing experiment
CREATE TABLE IF NOT EXISTS marketing_experiment (
    user_id          TEXT PRIMARY KEY,
    state            TEXT NOT NULL,
    city_tier        TEXT NOT NULL,
    channel          TEXT NOT NULL,
    device           TEXT NOT NULL,
    experiment_group TEXT NOT NULL CHECK (experiment_group IN ('Control','Treatment')),
    converted        SMALLINT NOT NULL CHECK (converted IN (0,1)),
    ad_spend_inr     NUMERIC(12,2) NOT NULL CHECK (ad_spend_inr >= 0)
);
CREATE INDEX IF NOT EXISTS idx_mkt_group_channel ON marketing_experiment (experiment_group, channel);
