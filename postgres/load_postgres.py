"""Create the InsightIndia PostgreSQL schema and bulk-load all CSV extracts with COPY.

Usage:
    export DATABASE_URL=postgresql://insight:insight@localhost:5432/insightindia
    python postgres/load_postgres.py

Safe to re-run: tables are truncated and reloaded inside one transaction.
"""
import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SCHEMA = "insightindia"

# table -> (csv path, columns in CSV order that exist in the table)
TABLES = {
    "ecommerce_orders": ROOT / "01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv",
    "morth_road_safety": ROOT / "02_india_road_safety_mobility/data/raw/morth_road_accidents_state_2019_2023.csv",
    "rbi_consolidated_fiscal": ROOT / "03_india_state_finances_data_quality/data/raw/rbi_consolidated_state_finances_2019_2026.csv",
    "marketing_experiment": ROOT / "04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv",
}


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Set DATABASE_URL, e.g. postgresql://insight:insight@localhost:5432/insightindia", file=sys.stderr)
        return 2
    with psycopg.connect(url) as con:
        with con.cursor() as cur:
            for script in ("01_schema.sql",):
                cur.execute((HERE / script).read_text(encoding="utf-8"))
            cur.execute(f"SET search_path TO {SCHEMA}")
            cur.execute("TRUNCATE " + ", ".join(TABLES))
            for table, path in TABLES.items():
                header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
                cols = ", ".join(header)
                with cur.copy(f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER true)") as copy:
                    with path.open("rb") as fh:
                        while chunk := fh.read(1 << 16):
                            copy.write(chunk)
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table}: {cur.fetchone()[0]:,} rows loaded")
            cur.execute((HERE / "02_views.sql").read_text(encoding="utf-8"))
        con.commit()
    print("PostgreSQL load complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
