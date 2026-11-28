"""InsightIndia 2.1 tests: PostgreSQL schema/queries and the advanced-statistics project."""
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "06_india_advanced_statistics/outputs"

TABLE_CSV = {
    "ecommerce_orders": "01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv",
    "morth_road_safety": "02_india_road_safety_mobility/data/raw/morth_road_accidents_state_2019_2023.csv",
    "rbi_consolidated_fiscal": "03_india_state_finances_data_quality/data/raw/rbi_consolidated_state_finances_2019_2026.csv",
    "marketing_experiment": "04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv",
}


class PostgresStaticTests(unittest.TestCase):
    def test_postgres_schema_columns_match_csv_headers(self):
        sql = (ROOT / "postgres/01_schema.sql").read_text()
        for table, csv_path in TABLE_CSV.items():
            body = re.search(r"CREATE TABLE IF NOT EXISTS %s \((.*?)\n\);" % table, sql, re.S).group(1)
            cols = [ln.strip().split()[0] for ln in body.splitlines()
                    if ln.strip() and not ln.strip().upper().startswith(("PRIMARY KEY", "CHECK", "--"))]
            header = list(pd.read_csv(ROOT / csv_path, nrows=0).columns)
            self.assertEqual(cols, header, table)

    def test_advanced_query_pack_has_twelve_queries(self):
        text = (ROOT / "postgres/03_advanced_queries.sql").read_text()
        self.assertEqual(len(re.findall(r"^-- Q\d+\.", text, re.M)), 12)


@unittest.skipUnless(os.environ.get("DATABASE_URL"), "set DATABASE_URL to run PostgreSQL integration tests")
class PostgresIntegrationTests(unittest.TestCase):
    def test_load_and_run_all_advanced_queries(self):
        subprocess.run([sys.executable, str(ROOT / "postgres/load_postgres.py")], check=True, capture_output=True)
        import psycopg
        with psycopg.connect(os.environ["DATABASE_URL"]) as con:
            cur = con.cursor()
            cur.execute("SET search_path TO insightindia")
            cur.execute("SELECT COUNT(*) FROM ecommerce_orders")
            self.assertEqual(cur.fetchone()[0], 18000)
            cur.execute("SELECT SUM(value) FROM morth_road_safety WHERE year=2023 AND metric='accidents'")
            self.assertEqual(int(cur.fetchone()[0]), 480583)
            text = (ROOT / "postgres/03_advanced_queries.sql").read_text()
            statements = [s for s in re.split(r";\s*\n", text) if re.search(r"\bSELECT\b", s)]
            self.assertGreaterEqual(len(statements), 12)
            for stmt in statements:
                cur.execute(stmt)
                cur.fetchall()
            # SQL z-test must agree with the Python result
            cur.execute(statements[-1])
            row = [r for r in cur.fetchall() if r[0] == "ALL CHANNELS"][0]
            res = pd.read_csv(ROOT / "04_india_digital_marketing_ab_test/outputs/experiment_result.csv").iloc[0]
            self.assertAlmostEqual(float(row[6]), res.z_statistic, places=2)


class AdvancedStatisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "06_india_advanced_statistics/src/analyze.py")],
                       check=True, capture_output=True)

    def test_ab_results_are_consistent_with_project_04(self):
        adv = pd.read_csv(STATS / "ab_advanced_results.csv").iloc[0]
        base = pd.read_csv(ROOT / "04_india_digital_marketing_ab_test/outputs/experiment_result.csv").iloc[0]
        self.assertAlmostEqual(adv.z_test_p_value, base.p_value, places=6)
        self.assertAlmostEqual(adv.abs_lift_pp, base.absolute_lift_pp, places=6)
        self.assertLess(adv.newcombe_ci95_low_pp, adv.abs_lift_pp)
        self.assertGreater(adv.newcombe_ci95_high_pp, adv.abs_lift_pp)
        self.assertAlmostEqual(adv.permutation_p_value, adv.z_test_p_value, delta=0.01)
        self.assertTrue(0 <= adv.bayes_prob_treatment_better <= 1)

    def test_multiple_testing_adjustments_never_decrease_p_values(self):
        seg = pd.read_csv(STATS / "ab_channel_multiple_testing.csv")
        self.assertEqual(len(seg), 4)
        self.assertTrue((seg.p_bonferroni >= seg.p_holm - 1e-12).all())
        self.assertTrue((seg.p_holm >= seg.p_raw - 1e-12).all())
        self.assertTrue((seg.p_fdr_bh >= seg.p_raw - 1e-12).all())
        self.assertTrue(seg[["p_raw", "p_bonferroni", "p_holm", "p_fdr_bh"]].le(1).all().all())

    def test_ecommerce_tests_have_effect_sizes_and_valid_p_values(self):
        t = pd.read_csv(STATS / "ecommerce_hypothesis_tests.csv")
        self.assertTrue(t.p_value.between(0, 1).all())
        self.assertGreaterEqual(t.effect_size.notna().sum(), 6)
        mw = t[t.test.str.startswith("Mann-Whitney")].iloc[0]
        self.assertLess(mw.effect_size, 0)  # late deliveries rate lower

    def test_statistics_are_reproducible(self):
        before = (STATS / "ab_advanced_results.csv").read_text()
        subprocess.run([sys.executable, str(ROOT / "06_india_advanced_statistics/src/analyze.py")],
                       check=True, capture_output=True)
        self.assertEqual(before, (STATS / "ab_advanced_results.csv").read_text())


if __name__ == "__main__":
    unittest.main()
