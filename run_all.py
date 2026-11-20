from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parent
SCRIPTS=[
'01_india_ecommerce_analytics/src/analyze.py',
'02_india_road_safety_mobility/src/analyze.py',
'03_india_state_finances_data_quality/src/analyze.py',
'04_india_digital_marketing_ab_test/src/analyze.py',
'05_india_ecommerce_bi_dashboard/src/export_dashboard_data.py']
for script in SCRIPTS:
    print(f"\n=== Running {script} ===",flush=True)
    subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
print('\nAll five project pipelines completed successfully.')
