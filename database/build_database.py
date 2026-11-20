"""Build a local SQLite analytics database from the repository CSV extracts."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database" / "insightindia_analytics.sqlite"
SOURCES = {
    "ecommerce_orders_demo": ROOT / "01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv",
    "morth_road_safety": ROOT / "02_india_road_safety_mobility/data/raw/morth_road_accidents_state_2019_2023.csv",
    "rbi_consolidated_fiscal": ROOT / "03_india_state_finances_data_quality/data/raw/rbi_consolidated_state_finances_2019_2026.csv",
    "marketing_ab_test_synthetic": ROOT / "04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv",
}
with sqlite3.connect(DB) as con:
    for table, path in SOURCES.items():
        frame = pd.read_csv(path)
        frame.to_sql(table, con, if_exists="replace", index=False)
    con.executescript("""
    CREATE INDEX IF NOT EXISTS idx_ecom_date ON ecommerce_orders_demo(order_date);
    CREATE INDEX IF NOT EXISTS idx_ecom_state ON ecommerce_orders_demo(state);
    CREATE INDEX IF NOT EXISTS idx_road_year_metric ON morth_road_safety(year, metric);
    CREATE INDEX IF NOT EXISTS idx_road_state ON morth_road_safety(state_ut);
    CREATE INDEX IF NOT EXISTS idx_marketing_group ON marketing_ab_test_synthetic(experiment_group);
    """)
    for table in SOURCES:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count:,} rows")
print(f"SQLite database created: {DB.relative_to(ROOT)}")
