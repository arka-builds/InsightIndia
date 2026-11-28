"""Prepare a clean Power BI/Tableau fact table from Project 01 demo case data."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
src=ROOT.parent/'01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv'
df=pd.read_csv(src,parse_dates=['order_date'])
df['order_month']=df.order_date.dt.to_period('M').astype(str)
df['delivered_flag']=(df.order_status=='Delivered').astype(int)
df['late_delivery_flag']=pd.to_numeric(df.is_late_delivery,errors='coerce').fillna(0).astype(int)
df['order_value_inr']=pd.to_numeric(df.order_value_inr,errors='coerce')
df['review_score']=pd.to_numeric(df.review_score,errors='coerce')
out=ROOT/'data/processed'; out.mkdir(parents=True,exist_ok=True)
df.to_csv(out/'powerbi_table_orders.csv',index=False)
# Dimensions support a simple star-schema build in BI tools.
for col,name in [('state','dim_state'),('category','dim_category'),('payment_method','dim_payment_method'),('order_status','dim_order_status')]:
    df[[col]].drop_duplicates().sort_values(col).rename(columns={col:'name'}).to_csv(out/f'{name}.csv',index=False)
print(f'Exported {len(df):,} demo orders with month and flag fields.')
