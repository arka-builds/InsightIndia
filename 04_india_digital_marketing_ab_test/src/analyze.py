"""Statistical analysis of a synthetic randomized marketing experiment."""
from pathlib import Path
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from scipy.stats import chisquare
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
df=pd.read_csv(ROOT/'data/raw/india_marketing_ab_test_synthetic.csv')
required={'user_id','experiment_group','converted','ad_spend_inr','channel','device','state'}
if required-set(df): raise ValueError(f'Missing columns: {required-set(df)}')
if df.user_id.duplicated().any(): raise ValueError('Each user must appear once in this experiment extract')
if set(df.experiment_group.unique())!={'Control','Treatment'}: raise ValueError('Expected Control and Treatment groups')
g=df.groupby('experiment_group').agg(users=('user_id','nunique'),conversions=('converted','sum'),spend_inr=('ad_spend_inr','sum')).reset_index()
g['conversion_rate']=g.conversions/g.users; g['cost_per_conversion_inr']=g.spend_inr/g.conversions.replace(0,float('nan'))
g[['ci_low','ci_high']]=g.apply(lambda r: pd.Series(proportion_confint(r.conversions,r.users,method='wilson')),axis=1)
g.to_csv(OUT/'group_performance.csv',index=False)
control=g.set_index('experiment_group').loc['Control']; treatment=g.set_index('experiment_group').loc['Treatment']
z,p=proportions_ztest([treatment.conversions,control.conversions],[treatment.users,control.users],alternative='two-sided')
lift=(treatment.conversion_rate/control.conversion_rate)-1
srm_chi2, srm_p = chisquare(g.users, f_exp=[g.users.sum()/2, g.users.sum()/2])
result=pd.DataFrame([{'control_users':int(control.users),'treatment_users':int(treatment.users),
'control_rate':control.conversion_rate,'treatment_rate':treatment.conversion_rate,
'absolute_lift_pp':(treatment.conversion_rate-control.conversion_rate)*100,
'relative_lift_pct':lift*100,'z_statistic':z,'p_value':p,
'significant_at_5pct':bool(p<.05),'sample_ratio_chi2':srm_chi2,
'sample_ratio_p_value':srm_p,'sample_ratio_mismatch_at_5pct':bool(srm_p<.05),
'interpretation':'Synthetic experiment only; no real campaign inference.'}])
result.to_csv(OUT/'experiment_result.csv',index=False)
seg=df.groupby(['channel','experiment_group']).agg(users=('user_id','nunique'),conversions=('converted','sum'),spend_inr=('ad_spend_inr','sum')).reset_index(); seg['conversion_rate']=seg.conversions/seg.users; seg['cost_per_conversion_inr']=seg.spend_inr/seg.conversions.replace(0,float('nan')); seg.to_csv(OUT/'channel_performance.csv',index=False)
plt.figure(figsize=(7,4)); plt.bar(g.experiment_group,g.conversion_rate); plt.ylabel('Conversion rate'); plt.title('Conversion rate by group — synthetic experiment'); plt.tight_layout(); plt.savefig(OUT/'conversion_rate.png',dpi=150); plt.close()
plt.figure(figsize=(7,4)); plt.bar(g.experiment_group,g.cost_per_conversion_inr); plt.ylabel('Cost per conversion (INR)'); plt.title('Cost per conversion — synthetic experiment'); plt.tight_layout(); plt.savefig(OUT/'cost_per_conversion.png',dpi=150); plt.close()
print(result.to_string(index=False))
