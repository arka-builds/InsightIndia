"""Reproducible analysis of a synthetic India-oriented retail case dataset."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/raw/india_ecommerce_orders_demo.csv'
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
df=pd.read_csv(DATA,parse_dates=['order_date'])
required={'order_id','order_date','state','city','category','order_status','payment_method','quantity','unit_price_inr','order_value_inr','shipping_days','is_late_delivery','review_score','customer_id'}
missing=required-set(df.columns)
if missing: raise ValueError(f'Missing required columns: {sorted(missing)}')
quality=pd.DataFrame([
 {'check':'Rows present','failed_records':int(len(df)==0),'records_tested':1},
 {'check':'Unique order IDs','failed_records':int(df.order_id.duplicated().sum()),'records_tested':len(df)},
 {'check':'Order date populated','failed_records':int(df.order_date.isna().sum()),'records_tested':len(df)},
 {'check':'Non-negative order value','failed_records':int((pd.to_numeric(df.order_value_inr,errors='coerce')<0).sum()),'records_tested':len(df)},
 {'check':'Review score within 1-5 when present','failed_records':int((~df.review_score.dropna().between(1,5)).sum()),'records_tested':int(df.review_score.notna().sum())},
])
quality['pass_rate_pct']=(1-quality.failed_records/quality.records_tested.replace(0,1))*100
quality.to_csv(OUT/'data_quality_report.csv',index=False)
df=df.drop_duplicates('order_id').copy(); df['order_value_inr']=pd.to_numeric(df.order_value_inr,errors='coerce')
delivered=df[df.order_status.eq('Delivered')].copy()
delivered['month']=delivered.order_date.dt.to_period('M').astype(str)
monthly=delivered.groupby('month',as_index=False).agg(revenue_inr=('order_value_inr','sum'),orders=('order_id','nunique'),avg_order_value_inr=('order_value_inr','mean'))
state=delivered.groupby('state',as_index=False).agg(orders=('order_id','nunique'),revenue_inr=('order_value_inr','sum'),late_delivery_rate=('is_late_delivery','mean'),avg_review=('review_score','mean'))
category=delivered.groupby('category',as_index=False).agg(orders=('order_id','nunique'),revenue_inr=('order_value_inr','sum'),avg_order_value_inr=('order_value_inr','mean'))
review=delivered.groupby('is_late_delivery',as_index=False).agg(orders=('order_id','nunique'),avg_review=('review_score','mean'))
for name,table in [('monthly_sales',monthly),('state_performance',state),('category_performance',category),('late_delivery_review',review)]: table.to_csv(OUT/f'{name}.csv',index=False)
plt.figure(figsize=(10,5)); plt.plot(monthly.month,monthly.revenue_inr,marker='o'); plt.xticks(rotation=60,ha='right'); plt.title('Monthly delivered revenue — synthetic case data'); plt.ylabel('Revenue (INR)'); plt.tight_layout(); plt.savefig(OUT/'monthly_revenue.png',dpi=150); plt.close()
plt.figure(figsize=(9,5)); top=state.nlargest(10,'revenue_inr').sort_values('revenue_inr'); plt.barh(top.state,top.revenue_inr); plt.title('Top states by delivered revenue — synthetic case data'); plt.xlabel('Revenue (INR)'); plt.tight_layout(); plt.savefig(OUT/'top_states_revenue.png',dpi=150); plt.close()
print(f'Rows={len(df):,}; delivered={len(delivered):,}; demo revenue=₹{delivered.order_value_inr.sum():,.0f}; QA checks={len(quality)}')
