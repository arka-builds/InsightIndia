-- PostgreSQL | Marketing A/B Test
CREATE TABLE IF NOT EXISTS marketing_experiment (user_id TEXT, state TEXT, city_tier TEXT, channel TEXT, device TEXT, experiment_group TEXT, converted INT, ad_spend_inr NUMERIC(12,2), PRIMARY KEY (user_id), CHECK (converted IN (0,1)), CHECK (ad_spend_inr >= 0));
-- \copy marketing_experiment FROM '04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv' WITH (FORMAT csv, HEADER true);
SELECT experiment_group, COUNT(*) users, SUM(converted) conversions, AVG(converted::numeric) conversion_rate, SUM(ad_spend_inr) spend_inr, SUM(ad_spend_inr)/NULLIF(SUM(converted),0) cost_per_conversion FROM marketing_experiment GROUP BY experiment_group;
SELECT channel, experiment_group, COUNT(*) users, AVG(converted::numeric) conversion_rate FROM marketing_experiment GROUP BY channel, experiment_group ORDER BY channel, experiment_group;
SELECT city_tier, experiment_group, COUNT(*) users, AVG(converted::numeric) conversion_rate FROM marketing_experiment GROUP BY city_tier, experiment_group ORDER BY city_tier, experiment_group;
