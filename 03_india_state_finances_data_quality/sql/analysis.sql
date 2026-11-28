-- PostgreSQL | RBI State Finances: A Study of Budgets 2025-26
CREATE TABLE IF NOT EXISTS rbi_consolidated_fiscal (
  fiscal_year TEXT PRIMARY KEY,
  revenue_receipts_lakh_crore NUMERIC,
  aggregate_expenditure_lakh_crore NUMERIC,
  revenue_expenditure_lakh_crore NUMERIC,
  capital_expenditure_lakh_crore NUMERIC,
  interest_payments_lakh_crore NUMERIC,
  gross_fiscal_deficit_lakh_crore NUMERIC,
  revenue_deficit_lakh_crore NUMERIC,
  primary_deficit_lakh_crore NUMERIC,
  estimate_status TEXT,
  source TEXT
);
-- Import CSV using psql:
-- \copy rbi_consolidated_fiscal FROM '03_india_state_finances_data_quality/data/raw/rbi_consolidated_state_finances_2019_2026.csv' CSV HEADER;

-- Capital expenditure share in aggregate expenditure.
SELECT fiscal_year, estimate_status,
       ROUND(100 * capital_expenditure_lakh_crore / NULLIF(aggregate_expenditure_lakh_crore, 0), 2) AS capex_share_pct
FROM rbi_consolidated_fiscal
ORDER BY fiscal_year;

-- Revenue balance: positive = surplus; negative = deficit.
SELECT fiscal_year, estimate_status,
       ROUND(revenue_receipts_lakh_crore - revenue_expenditure_lakh_crore, 2) AS revenue_balance_lakh_crore
FROM rbi_consolidated_fiscal
ORDER BY fiscal_year;

-- Keep Accounts, Provisional Accounts, Revised Estimates and Budget Estimates distinct.
SELECT estimate_status, COUNT(*) AS periods,
       AVG(gross_fiscal_deficit_lakh_crore) AS avg_gfd_lakh_crore
FROM rbi_consolidated_fiscal
GROUP BY estimate_status
ORDER BY estimate_status;
