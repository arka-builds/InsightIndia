from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

class PortfolioDataTests(unittest.TestCase):
    def test_ecommerce_demo_is_consistent_and_disclosed(self):
        d = pd.read_csv(ROOT/'01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv')
        self.assertFalse(d.order_id.duplicated().any())
        self.assertTrue(d.review_score.dropna().between(1,5).all())
        self.assertTrue((d.order_value_inr >= 0).all())
        self.assertEqual(len(d), 18000)

    def test_morth_state_series_reconciles_to_published_national_totals(self):
        d = pd.read_csv(ROOT/'02_india_road_safety_mobility/data/raw/morth_road_accidents_state_2019_2023.csv')
        expected = {
            (2019,'accidents'):456959,(2020,'accidents'):372181,(2021,'accidents'):412432,(2022,'accidents'):461312,(2023,'accidents'):480583,
            (2019,'persons_killed'):158984,(2020,'persons_killed'):138383,(2021,'persons_killed'):153972,(2022,'persons_killed'):168491,(2023,'persons_killed'):172890
        }
        for key,total in expected.items():
            year,metric=key
            observed=int(d[(d.year==year)&(d.metric==metric)].value.sum())
            self.assertEqual(observed,total,key)

    def test_rbi_official_series_keeps_estimate_status(self):
        d=pd.read_csv(ROOT/'03_india_state_finances_data_quality/data/raw/rbi_consolidated_state_finances_2019_2026.csv')
        self.assertEqual(len(d),8)
        self.assertIn('Budget Estimate', ' '.join(d.estimate_status))
        self.assertIn('Provisional Accounts', ' '.join(d.estimate_status))
        self.assertTrue((d.aggregate_expenditure_lakh_crore.dropna()>0).all())
        self.assertTrue(pd.isna(d.loc[d.fiscal_year=='2019-20','revenue_receipts_lakh_crore']).all())

    def test_ab_test_has_two_groups_and_binary_outcome(self):
        d=pd.read_csv(ROOT/'04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv')
        self.assertEqual(set(d.experiment_group),{'Control','Treatment'})
        self.assertFalse(d.user_id.duplicated().any())
        self.assertTrue(d.converted.isin([0,1]).all())

    def test_powerbi_export_matches_source(self):
        src=pd.read_csv(ROOT/'01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv')
        out=pd.read_csv(ROOT/'05_india_ecommerce_bi_dashboard/data/processed/powerbi_table_orders.csv')
        self.assertEqual(len(src),len(out))
        self.assertIn('order_month',out.columns)

    def test_sqlite_database_builds_and_contains_expected_tables(self):
        script=ROOT/'database/build_database.py'
        subprocess.run([sys.executable,str(script)],cwd=ROOT,check=True,capture_output=True,text=True)
        db=ROOT/'database/insightindia_analytics.sqlite'
        with sqlite3.connect(db) as con:
            tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({'ecommerce_orders_demo','morth_road_safety','rbi_consolidated_fiscal','marketing_ab_test_synthetic'}.issubset(tables))
            total=con.execute("SELECT SUM(value) FROM morth_road_safety WHERE year=2023 AND metric='accidents'").fetchone()[0]
            self.assertEqual(total,480583)

if __name__=='__main__':
    unittest.main()
