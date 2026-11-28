from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

BASE = Path(__file__).resolve().parent
st.set_page_config(page_title='InsightIndia', page_icon='📊', layout='wide')

PAGES = [
    '01 · E-commerce Analytics',
    '02 · Road Safety Analytics',
    '03 · State Government Finances',
    '04 · Marketing A/B Experiment',
    '05 · E-commerce BI Dashboard',
    '06 · Advanced Statistics',
]

# Consistent presentation helpers ------------------------------------------------
def kpi(items):
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def inr(value, decimals=0):
    if pd.isna(value):
        return 'Not available'
    return f'₹{value:,.{decimals}f}'


def lakh_crore(value):
    if pd.isna(value):
        return 'Not available'
    return f'₹{value:,.1f} lakh crore'


def add_business_note(title, body):
    st.subheader(title)
    st.info(body)


def style_axes(fig, x_title=None, y_title=None):
    fig.update_layout(
        margin=dict(l=15, r=15, t=65, b=20),
        legend_title_text='',
        title_font_size=18,
        hoverlabel=dict(namelength=-1),
    )
    if x_title:
        fig.update_xaxes(title=x_title)
    if y_title:
        fig.update_yaxes(title=y_title)
    return fig


def load_ecommerce():
    path = BASE / '01_india_ecommerce_analytics/data/raw/india_ecommerce_orders_demo.csv'
    return pd.read_csv(path, parse_dates=['order_date'])


def ecommerce_filters(df, key_prefix):
    c1, c2, c3 = st.columns(3)
    states = ['All'] + sorted(df.state.dropna().unique().tolist())
    categories = ['All'] + sorted(df.category.dropna().unique().tolist())
    statuses = ['All'] + sorted(df.order_status.dropna().unique().tolist())
    state = c1.selectbox('State', states, key=f'{key_prefix}_state')
    category = c2.selectbox('Product category', categories, key=f'{key_prefix}_category')
    status = c3.selectbox('Order status', statuses, key=f'{key_prefix}_status')
    filtered = df.copy()
    if state != 'All':
        filtered = filtered[filtered.state == state]
    if category != 'All':
        filtered = filtered[filtered.category == category]
    if status != 'All':
        filtered = filtered[filtered.order_status == status]
    return filtered


st.title('InsightIndia')
st.caption('Six reproducible analytics workstreams | Source labels distinguish official statistics from synthetic case-study data')
page = st.sidebar.radio('Project dashboard', PAGES)
st.sidebar.markdown('---')
st.sidebar.caption('Data provenance is displayed on every page. Synthetic examples must not be presented as official statistics.')

# 01 · E-commerce Analytics ------------------------------------------------------
if page == PAGES[0]:
    st.header('E-commerce Analytics')
    st.warning('SYNTHETIC CASE DATA · Indian state/city labels are illustrative. These are not actual Indian e-commerce transactions.')
    df = load_ecommerce()
    d = ecommerce_filters(df, 'analysis')
    delivered = d[d.order_status.eq('Delivered')].copy()
    total_revenue = delivered.order_value_inr.sum()
    delivered_orders = delivered.order_id.nunique()
    aov = delivered.order_value_inr.mean() if delivered_orders else float('nan')
    late_rate = delivered.is_late_delivery.mean() if delivered_orders else float('nan')
    kpi([
        ('Delivered revenue', f'₹{total_revenue/1e7:.2f} Cr', 'Sum of order value for delivered orders in the selected filters.'),
        ('Delivered orders', f'{delivered_orders:,}', 'Distinct delivered order IDs.'),
        ('Average order value', inr(aov), 'Delivered revenue divided by delivered orders.'),
        ('Late delivery rate', f'{late_rate:.1%}' if pd.notna(late_rate) else 'N/A', 'Share of delivered orders marked as late.'),
    ])
    if delivered.empty:
        st.warning('No delivered orders match the selected filters. Change the filters to view revenue analysis.')
    else:
        delivered['month'] = delivered.order_date.dt.to_period('M').astype(str)
        monthly = delivered.groupby('month', as_index=False).order_value_inr.sum()
        category = delivered.groupby('category', as_index=False).agg(revenue_inr=('order_value_inr', 'sum'), orders=('order_id', 'nunique')).sort_values('revenue_inr', ascending=False)
        a, b = st.columns(2)
        fig = px.line(monthly, x='month', y='order_value_inr', markers=True, title='Delivered revenue by month')
        a.plotly_chart(style_axes(fig, 'Month', 'Delivered revenue (₹)'), width='stretch')
        fig = px.bar(category, x='category', y='revenue_inr', title='Delivered revenue by product category', text_auto='.2s')
        b.plotly_chart(style_axes(fig, 'Product category', 'Delivered revenue (₹)'), width='stretch')

        regional = delivered.groupby('state', as_index=False).agg(
            revenue_inr=('order_value_inr', 'sum'),
            orders=('order_id', 'nunique'),
            late_rate=('is_late_delivery', 'mean'),
        ).sort_values('revenue_inr', ascending=False)
        fig = px.bar(regional.head(15).sort_values('revenue_inr'), x='revenue_inr', y='state', orientation='h', title='Top 15 states by delivered revenue', text_auto='.2s')
        st.plotly_chart(style_axes(fig, 'Delivered revenue (₹)', 'State'), width='stretch')

        reviews = delivered.groupby('is_late_delivery', as_index=False).agg(
            average_review=('review_score', 'mean'), orders=('order_id', 'nunique')
        )
        reviews['Delivery timing'] = reviews.is_late_delivery.map({0: 'On time', 1: 'Late'})
        fig = px.bar(reviews, x='Delivery timing', y='average_review', text='orders', title='Average customer review by delivery timing', hover_data={'orders': True, 'average_review': ':.2f'})
        fig.update_traces(texttemplate='n=%{text}', textposition='outside')
        st.plotly_chart(style_axes(fig, 'Delivery timing', 'Average review score (1–5)'), width='stretch')

        best_category = category.iloc[0]
        eligible = regional[regional.orders >= 30]
        worst_late = (eligible if not eligible.empty else regional).sort_values('late_rate', ascending=False).iloc[0]
        late_reviews = reviews.set_index('Delivery timing').average_review.to_dict()
        review_gap = late_reviews.get('On time', float('nan')) - late_reviews.get('Late', float('nan'))
        add_business_note(
            'Business interpretation',
            f"Within the selected synthetic sample, {best_category.category} contributes the most delivered revenue ({inr(best_category.revenue_inr)}). "
            f"{worst_late.state} has the highest late-delivery share ({worst_late.late_rate:.1%}) among states with at least 30 delivered orders. "
            f"The average review-score gap between on-time and late deliveries is {review_gap:.2f} points. "
            'Treat these as practice-case signals, not evidence about the real Indian e-commerce market.'
        )
        st.subheader('State-level operating summary')
        regional_display = regional.rename(columns={'state': 'State', 'revenue_inr': 'Delivered revenue (₹)', 'orders': 'Delivered orders', 'late_rate': 'Late delivery rate'})
        regional_display['Late delivery rate'] = regional_display['Late delivery rate'].map(lambda x: f'{x:.1%}')
        st.dataframe(regional_display, width='stretch', hide_index=True)
    st.download_button('Download filtered order records', d.to_csv(index=False).encode('utf-8'), file_name='filtered_india_ecommerce_demo.csv', mime='text/csv')

# 02 · Road Safety Analytics -----------------------------------------------------
elif page == PAGES[1]:
    st.header('Road Safety Analytics')
    df = pd.read_csv(BASE / '02_india_road_safety_mobility/data/raw/morth_road_accidents_state_2019_2023.csv')
    st.info('OFFICIAL SOURCE · MoRTH Road Accidents in India 2023, Tables 5.1 and 5.6. Covers 2019–2023 state/UT accidents and fatalities. These are reported counts, not exposure-adjusted risk.')
    metric = st.selectbox('Measure', ['accidents', 'persons_killed'], format_func=lambda x: 'Road accidents' if x == 'accidents' else 'Persons killed')
    years = sorted(df.year.unique().tolist())
    year = st.select_slider('Year', options=years, value=2023)
    label = 'Road accidents' if metric == 'accidents' else 'Persons killed'
    d = df[(df.metric == metric) & (df.year == year)].dropna(subset=['value']).copy()
    total = int(d.value.sum())
    annual = df[df.metric == metric].groupby('year', as_index=False).value.sum(min_count=1).sort_values('year')
    current = annual.loc[annual.year == year, 'value']
    prior = annual.loc[annual.year == year - 1, 'value']
    yoy = ((float(current.iloc[0]) / float(prior.iloc[0])) - 1) * 100 if len(current) and len(prior) and float(prior.iloc[0]) else None
    kpi([
        ('India total', f'{total:,.0f}', f'Total reported {label.lower()} for {year}.'),
        ('Selected year', str(year), 'Choose a year from 2019 to 2023.'),
        ('State/UT records', f'{len(d):,}', 'Rows with a reported value for this measure and year.'),
        ('Change vs previous year', f'{yoy:+.1f}%' if yoy is not None else 'N/A', 'Year-over-year change in the all-India total.'),
    ])
    ranked = d.sort_values('value', ascending=False)
    a, b = st.columns(2)
    fig = px.bar(ranked.head(12).sort_values('value'), x='value', y='state_ut', orientation='h', title=f'Top 12 States/UTs by {label.lower()}')
    a.plotly_chart(style_axes(fig, f'{label} (count)', 'State/UT'), width='stretch')
    fig = px.line(annual, x='year', y='value', markers=True, title=f'All-India {label.lower()} trend, 2019–2023')
    b.plotly_chart(style_axes(fig, 'Year', f'{label} (count)'), width='stretch')
    if yoy is not None:
        direction = 'increased' if yoy > 0 else 'decreased'
        add_business_note('What the trend says', f'In {year}, reported {label.lower()} {direction} by {abs(yoy):.1f}% compared with {year-1}. This is a change in reported counts; it does not by itself measure individual road-user risk or account for traffic exposure.')
    st.caption('State/UT values reconcile to the all-India totals published by MoRTH. Missing source values remain blank and are excluded from the sum.')
    display = ranked.rename(columns={'year': 'Year', 'state_ut': 'State/UT', 'metric': 'Measure', 'value': 'Reported count', 'source': 'Source', 'data_status': 'Data status'})
    st.dataframe(display, width='stretch', hide_index=True)
    st.download_button('Download filtered source table', d.to_csv(index=False).encode('utf-8'), file_name=f'morth_{metric}_{year}.csv', mime='text/csv')

# 03 · State Government Finances -----------------------------------------------
elif page == PAGES[2]:
    st.header('State Government Finances & Data Quality')
    df = pd.read_csv(BASE / '03_india_state_finances_data_quality/data/raw/rbi_consolidated_state_finances_2019_2026.csv')
    st.info('OFFICIAL SOURCE · RBI State Finances: A Study of Budgets 2025-26, consolidated state-government fiscal position. Amounts are ₹ lakh crore. Accounts/actual, RE, PA and BE statuses are labelled separately. These are aggregate values, not state-by-state figures.')
    fy = st.selectbox('Fiscal year', df.fiscal_year.tolist(), index=len(df)-1)
    row = df[df.fiscal_year == fy].iloc[0]
    kpi([
        ('Total expenditure', lakh_crore(row.aggregate_expenditure_lakh_crore), 'Aggregate expenditure for the selected fiscal year.'),
        ('Revenue expenditure', lakh_crore(row.revenue_expenditure_lakh_crore), 'Recurring expenditure recorded in the RBI series.'),
        ('Capital expenditure', lakh_crore(row.capital_expenditure_lakh_crore), 'Capital expenditure recorded in the RBI series.'),
        ('Gross fiscal deficit', lakh_crore(row.gross_fiscal_deficit_lakh_crore), 'Gross fiscal deficit in ₹ lakh crore.'),
    ])
    st.caption(f"Estimate status for {fy}: **{row.estimate_status}**. Values shown are not all final actuals; compare years with their status in mind.")
    # Use grouped bars rather than connecting unlike reporting statuses as a time series.
    # 2024-25 RE and PA are separate observations; 2025-26 is a BE, not an actual.
    st.subheader('Receipts vs expenditure')
    st.caption('Grouped comparisons in ₹ lakh crore. Fiscal-year labels preserve Accounts/actual, RE, PA and BE status; missing observations are omitted, not estimated.')
    flow_fields = {
        'Revenue receipts': 'revenue_receipts_lakh_crore',
        'Revenue expenditure': 'revenue_expenditure_lakh_crore',
        'Total expenditure': 'aggregate_expenditure_lakh_crore',
    }
    flow = df.melt(id_vars=['fiscal_year', 'estimate_status'], value_vars=list(flow_fields.values()), var_name='indicator', value_name='amount_lakh_crore')
    flow['indicator'] = flow.indicator.map({v: k for k, v in flow_fields.items()})
    flow = flow.dropna(subset=['amount_lakh_crore'])
    def fiscal_period_label(row):
        year = str(row['fiscal_year']).replace(' (RE)', '').replace(' (PA)', '').replace(' (BE)', '')
        status = {'Accounts/actual': 'Actual', 'Revised Estimate': 'RE', 'Provisional Accounts': 'PA', 'Budget Estimate': 'BE'}.get(row['estimate_status'], row['estimate_status'])
        return f'{year} · {status}'

    flow['period_label'] = flow.apply(fiscal_period_label, axis=1)
    period_order = flow[['fiscal_year', 'period_label']].drop_duplicates().sort_values('fiscal_year', key=lambda x: x.map({v: i for i, v in enumerate(df.fiscal_year)}))['period_label'].tolist()
    fig = px.bar(
        flow, x='period_label', y='amount_lakh_crore', color='indicator', barmode='group',
        category_orders={'period_label': period_order, 'indicator': list(flow_fields)},
        custom_data=['fiscal_year', 'estimate_status'],
        title='Receipts and expenditure by reporting period',
    )
    fig.update_traces(hovertemplate='%{fullData.name}<br>Period: %{customdata[0]}<br>Status: %{customdata[1]}<br>Amount: ₹%{y:.1f} lakh crore<extra></extra>')
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0.0), bargap=0.22, xaxis_tickangle=-25)
    st.plotly_chart(style_axes(fig, 'Fiscal year and reporting status', '₹ lakh crore'), width='stretch')

    st.subheader('Fiscal deficit indicators')
    st.caption('Gross fiscal deficit, revenue deficit and primary deficit are shown as grouped comparisons. These are reported amounts, not deficit ratios.')
    deficit_fields = {
        'Gross fiscal deficit': 'gross_fiscal_deficit_lakh_crore',
        'Revenue deficit': 'revenue_deficit_lakh_crore',
        'Primary deficit': 'primary_deficit_lakh_crore',
    }
    deficits = df.melt(id_vars=['fiscal_year', 'estimate_status'], value_vars=list(deficit_fields.values()), var_name='indicator', value_name='amount_lakh_crore')
    deficits['indicator'] = deficits.indicator.map({v: k for k, v in deficit_fields.items()})
    deficits = deficits.dropna(subset=['amount_lakh_crore'])
    deficits['period_label'] = deficits.apply(fiscal_period_label, axis=1)
    deficit_order = deficits[['fiscal_year', 'period_label']].drop_duplicates().sort_values('fiscal_year', key=lambda x: x.map({v: i for i, v in enumerate(df.fiscal_year)}))['period_label'].tolist()
    fig = px.bar(
        deficits, x='period_label', y='amount_lakh_crore', color='indicator', barmode='group',
        category_orders={'period_label': deficit_order, 'indicator': list(deficit_fields)},
        custom_data=['fiscal_year', 'estimate_status'],
        title='Fiscal deficit measures by reporting period',
    )
    fig.update_traces(hovertemplate='%{fullData.name}<br>Period: %{customdata[0]}<br>Status: %{customdata[1]}<br>Amount: ₹%{y:.1f} lakh crore<extra></extra>')
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0.0), bargap=0.22, xaxis_tickangle=-25)
    st.plotly_chart(style_axes(fig, 'Fiscal year and reporting status', '₹ lakh crore'), width='stretch')

    derived = pd.read_csv(BASE / '03_india_state_finances_data_quality/outputs/fiscal_indicators_derived.csv')
    selected = derived[derived.fiscal_year == fy].iloc[0]
    cap_share = selected.capital_expenditure_share_pct
    rev_balance = selected.revenue_balance_lakh_crore
    if pd.notna(rev_balance):
        balance_text = (
            f"Revenue receipts exceed revenue expenditure by {lakh_crore(rev_balance)} (revenue surplus)."
            if rev_balance > 0 else
            f"Revenue expenditure exceeds revenue receipts by {lakh_crore(abs(rev_balance))} (revenue deficit)."
            if rev_balance < 0 else
            'Revenue receipts equal revenue expenditure (revenue balance).'
        )
    else:
        balance_text = 'Revenue balance is unavailable because one or both components are not reported for this period.'
    add_business_note(
        'Fiscal interpretation',
        (f"For {fy}, capital expenditure represents {cap_share:.1f}% of total expenditure where both values are reported. " if pd.notna(cap_share) else f"Capital expenditure share is unavailable for {fy}. ")
        + balance_text
        + ' Compare actuals, provisional accounts, revised estimates and budget estimates with their status in mind; estimates are not final audited outcomes.'
    )
    qa = pd.read_csv(BASE / '03_india_state_finances_data_quality/outputs/data_quality_scorecard.csv')
    st.subheader('Data-quality validation exercise')
    st.caption('The QA sample is a deliberately corrupted test copy of the official series. It is not the RBI source table. Pass rates describe this test fixture only.')
    qa = qa.copy()
    label_map = {
        'revenue_expenditure_lakh_crore: non-null numeric': 'Revenue expenditure · numeric present',
        'revenue_expenditure_lakh_crore: non-negative': 'Revenue expenditure · non-negative',
        'gross_fiscal_deficit_lakh_crore: non-null numeric': 'Gross fiscal deficit · numeric present',
        'gross_fiscal_deficit_lakh_crore: non-negative': 'Gross fiscal deficit · non-negative',
        'capital_expenditure_lakh_crore: non-null numeric': 'Capital expenditure · numeric present',
        'capital_expenditure_lakh_crore: non-negative': 'Capital expenditure · non-negative',
        'fiscal_year normalized': 'Fiscal-year label · normalized',
    }
    qa['rule_label'] = qa['rule'].map(label_map).fillna(qa['rule'])
    qa = qa.sort_values('pass_rate_pct', ascending=True)
    fig = px.bar(qa, x='pass_rate_pct', y='rule_label', orientation='h', range_x=[0, 112],
                 title='Validation pass rate on the injected-issue test sample', text='pass_rate_pct',
                 custom_data=['failed_records', 'records_tested', 'passed_records'])
    fig.update_traces(
        texttemplate='%{x:.0f}%', textposition='outside', cliponaxis=False,
        hovertemplate='%{y}<br>Pass rate: %{x:.1f}%<br>Passed: %{customdata[2]}<br>Failed: %{customdata[0]}<br>Records tested: %{customdata[1]}<extra></extra>',
    )
    st.plotly_chart(style_axes(fig, 'Records passing (%)', 'Validation rule'), width='stretch')

    table = df.rename(columns={
        'fiscal_year': 'Fiscal year', 'revenue_receipts_lakh_crore': 'Revenue receipts (₹ lakh crore)',
        'aggregate_expenditure_lakh_crore': 'Total expenditure (₹ lakh crore)',
        'revenue_expenditure_lakh_crore': 'Revenue expenditure (₹ lakh crore)',
        'capital_expenditure_lakh_crore': 'Capital expenditure (₹ lakh crore)',
        'interest_payments_lakh_crore': 'Interest payments (₹ lakh crore)',
        'gross_fiscal_deficit_lakh_crore': 'Gross fiscal deficit (₹ lakh crore)',
        'revenue_deficit_lakh_crore': 'Revenue deficit (₹ lakh crore)',
        'primary_deficit_lakh_crore': 'Primary deficit (₹ lakh crore)',
        'estimate_status': 'Estimate status', 'source': 'Source',
    })
    st.subheader('RBI source series')
    st.dataframe(table, width='stretch', hide_index=True)  # missing values show as blank; avoids mixed float/str columns
    st.download_button('Download RBI fiscal series', df.to_csv(index=False).encode('utf-8'), file_name='rbi_consolidated_state_finances.csv', mime='text/csv')

# 04 · Marketing A/B Experiment --------------------------------------------------
elif page == PAGES[3]:
    st.header('Marketing A/B Experiment')
    df = pd.read_csv(BASE / '04_india_digital_marketing_ab_test/data/raw/india_marketing_ab_test_synthetic.csv')
    st.warning('SYNTHETIC EXPERIMENT · Generated randomized example data, not results from a real Indian advertising campaign.')
    g = df.groupby('experiment_group', as_index=False).agg(users=('user_id', 'nunique'), conversions=('converted', 'sum'), spend_inr=('ad_spend_inr', 'sum'))
    g['conversion_rate'] = g.conversions / g.users
    g['cost_per_conversion_inr'] = g.spend_inr / g.conversions.replace(0, float('nan'))
    res = pd.read_csv(BASE / '04_india_digital_marketing_ab_test/outputs/experiment_result.csv').iloc[0]
    ci = pd.read_csv(BASE / '04_india_digital_marketing_ab_test/outputs/group_performance.csv')
    control_rate = g.loc[g.experiment_group == 'Control', 'conversion_rate'].iloc[0]
    treatment_rate = g.loc[g.experiment_group == 'Treatment', 'conversion_rate'].iloc[0]
    kpi([
        ('Control conversion', f'{control_rate:.2%}', 'Share of control users who converted.'),
        ('Treatment conversion', f'{treatment_rate:.2%}', 'Share of treatment users who converted.'),
        ('Absolute lift', f'{res.absolute_lift_pp:.3f} pp', 'Treatment minus control conversion rate, in percentage points.'),
        ('P-value', f'{res.p_value:.4f}', 'Two-sided test; 5% significance threshold.'),
    ])
    a, b = st.columns(2)
    fig = px.bar(ci, x='experiment_group', y='conversion_rate', error_y=ci.conversion_rate-ci.ci_low, error_y_minus=ci.ci_high-ci.conversion_rate, title='Conversion rate with 95% Wilson confidence intervals')
    a.plotly_chart(style_axes(fig, 'Experiment group', 'Conversion rate'), width='stretch')
    fig = px.bar(g, x='experiment_group', y='cost_per_conversion_inr', title='Cost per conversion')
    b.plotly_chart(style_axes(fig, 'Experiment group', 'Cost per conversion (₹)'), width='stretch')
    sig = bool(res.significant_at_5pct)
    st.markdown('**Statistical result:** ' + ('Statistically significant at the 5% level.' if sig else 'Not statistically significant at the 5% level.'))
    treatment_cpc = g.loc[g.experiment_group == 'Treatment', 'cost_per_conversion_inr'].iloc[0]
    control_cpc = g.loc[g.experiment_group == 'Control', 'cost_per_conversion_inr'].iloc[0]
    if sig and treatment_cpc <= control_cpc:
        recommendation = 'The synthetic treatment is statistically higher-converting and no more expensive per conversion in this example. Validate with real campaign data before rollout.'
    elif sig:
        recommendation = 'The synthetic treatment conversion difference is statistically significant, but cost per conversion is higher. Assess the value of incremental conversions before rollout.'
    else:
        cost_clause = 'treatment cost per conversion is higher in this sample' if treatment_cpc > control_cpc else 'treatment cost per conversion is not higher in this sample'
        recommendation = f'Do not declare a winner from this experiment: the observed lift is not statistically significant at 5%, and {cost_clause}. Consider a pre-planned larger test with real randomized campaign data.'
    add_business_note('Business recommendation', recommendation)
    st.caption(f"Sample-ratio check p-value: {res.sample_ratio_p_value:.3f}. {'Sample-ratio mismatch IS flagged at the 5% level, so the randomization may be compromised.' if bool(res.sample_ratio_mismatch_at_5pct) else 'The synthetic sample does not show evidence of sample-ratio mismatch at the 5% level.'} Statistical significance does not establish commercial value by itself.")
    display = g.rename(columns={'experiment_group': 'Experiment group', 'users': 'Users', 'conversions': 'Conversions', 'spend_inr': 'Ad spend (₹)', 'conversion_rate': 'Conversion rate', 'cost_per_conversion_inr': 'Cost per conversion (₹)'})
    st.dataframe(display, width='stretch', hide_index=True)
    st.caption('A/B testing is synthetic by design here. Use first-party randomized campaign logs for an actual business decision.')

# 05 · E-commerce BI Dashboard ---------------------------------------------------
elif page == PAGES[4]:
    st.header('E-commerce BI Dashboard · Executive & Operations View')
    st.warning('SYNTHETIC CASE DATA · This BI-style dashboard reuses the Project 01 demo dataset. It is a separate reporting view, not an independent dataset or real marketplace result.')
    df = load_ecommerce()
    d = ecommerce_filters(df, 'bi')
    total_orders = d.order_id.nunique()
    delivered = d[d.order_status.eq('Delivered')].copy()
    delivered_count = delivered.order_id.nunique()
    revenue = delivered.order_value_inr.sum()
    customers = delivered.customer_id.nunique()
    repeat_customers = delivered.groupby('customer_id').order_id.nunique().gt(1).sum()
    repeat_rate = repeat_customers / customers if customers else float('nan')
    cancellation_rate = d.order_status.eq('Cancelled').mean() if len(d) else float('nan')
    kpi([
        ('All orders', f'{total_orders:,}', 'Distinct orders after the selected filters.'),
        ('Delivered sales', f'₹{revenue/1e7:.2f} Cr', 'Delivered order value only.'),
        ('Unique delivered customers', f'{customers:,}', 'Distinct customers with at least one delivered order.'),
        ('Repeat-customer rate', f'{repeat_rate:.1%}' if pd.notna(repeat_rate) else 'N/A', 'Share of delivered customers with more than one delivered order in this sample.'),
    ])

    overview_tab, customer_tab, operations_tab = st.tabs(['Executive overview', 'Customer & product mix', 'Operations & fulfilment'])
    with overview_tab:
        st.subheader('Sales performance')
        if delivered.empty:
            st.info('No delivered orders match the selected filters.')
        else:
            delivered['month'] = delivered.order_date.dt.to_period('M').astype(str)
            trend = delivered.groupby('month', as_index=False).agg(sales=('order_value_inr', 'sum'), orders=('order_id', 'nunique'))
            fig = px.area(trend, x='month', y='sales', title='Monthly delivered sales')
            st.plotly_chart(style_axes(fig, 'Month', 'Delivered sales (₹)'), width='stretch')
            cat = delivered.groupby('category', as_index=False).agg(sales=('order_value_inr', 'sum'), orders=('order_id', 'nunique')).sort_values('sales', ascending=False)
            fig = px.bar(cat, x='category', y='sales', color='orders', title='Category sales and order volume', text_auto='.2s')
            st.plotly_chart(style_axes(fig, 'Product category', 'Delivered sales (₹)'), width='stretch')
            top = cat.iloc[0]
            add_business_note('Executive takeaway', f"{top.category} is the largest category by delivered sales in the selected sample, contributing {top.sales/revenue:.1%} of delivered revenue. Use the filters to compare the product mix across states and order statuses.")
    with customer_tab:
        st.subheader('Customer & product mix')
        if delivered.empty:
            st.info('No delivered orders match the selected filters.')
        else:
            customer_orders = delivered.groupby('customer_id', as_index=False).agg(orders=('order_id', 'nunique'), customer_sales=('order_value_inr', 'sum'))
            # Repeat status is defined within the currently filtered delivered-order sample.
            customer_orders['customer_type'] = customer_orders.orders.map(lambda n: 'Repeat' if n > 1 else 'One-time')
            mix = customer_orders.groupby('customer_type', as_index=False).agg(
                customers=('customer_id', 'nunique'), orders=('orders', 'sum'), sales=('customer_sales', 'sum')
            )
            mix['customer_share'] = mix.customers / mix.customers.sum()
            mix['average_order_value'] = mix.sales / mix.orders.replace(0, float('nan'))
            a, b = st.columns(2)
            fig = px.pie(mix, names='customer_type', values='customers', hole=.55, title='Customer mix by purchase frequency',
                         custom_data=['customers'])
            fig.update_traces(textinfo='percent+label', hovertemplate='%{label}<br>Customers: %{customdata[0]:,}<br>Share: %{percent}<extra></extra>')
            a.plotly_chart(fig, width='stretch')
            fig = px.bar(mix, x='customer_type', y='sales', title='Delivered sales by customer type', text_auto='.2s',
                         hover_data={'customers': True, 'orders': True, 'average_order_value': ':.2f'})
            b.plotly_chart(style_axes(fig, 'Customer type', 'Delivered sales (₹)'), width='stretch')
            pay = delivered.groupby('payment_method', as_index=False).agg(orders=('order_id', 'nunique'), sales=('order_value_inr', 'sum')).sort_values('sales', ascending=False)
            fig = px.bar(pay, x='payment_method', y='sales', title='Delivered sales by payment method', text_auto='.2s',
                         hover_data={'orders': True})
            st.plotly_chart(style_axes(fig, 'Payment method', 'Delivered sales (₹)'), width='stretch')
            st.subheader('Customer segment summary')
            segment_table = mix.rename(columns={'customer_type': 'Customer type', 'customers': 'Customers', 'orders': 'Delivered orders', 'sales': 'Delivered sales (₹)', 'customer_share': 'Share of customers', 'average_order_value': 'Average order value (₹)'})
            segment_table['Share of customers'] = segment_table['Share of customers'].map(lambda x: f'{x:.1%}')
            segment_table['Average order value (₹)'] = segment_table['Average order value (₹)'].map(lambda x: f'₹{x:,.2f}')
            st.dataframe(segment_table, width='stretch', hide_index=True)
            repeat_row = mix[mix.customer_type.eq('Repeat')]
            one_row = mix[mix.customer_type.eq('One-time')]
            if not repeat_row.empty:
                repeat = repeat_row.iloc[0]
                repeat_sales_share = repeat.sales / mix.sales.sum() if mix.sales.sum() else 0
                repeat_aov = repeat.average_order_value
                one_aov = float(one_row.average_order_value.iloc[0]) if not one_row.empty else float('nan')
                aov_sentence = f"Average order value is ₹{repeat_aov:,.0f} for repeat customers versus ₹{one_aov:,.0f} for one-time customers." if pd.notna(one_aov) else f"Repeat-customer average order value is ₹{repeat_aov:,.0f}."
                add_business_note('Customer insight', f"Repeat customers account for {repeat.customer_share:.1%} of delivered customers and {repeat_sales_share:.1%} of delivered sales in the current filtered sample. {aov_sentence} Repeat status means more than one delivered order in this filtered dataset; it is not a lifetime customer classification.")
            with st.expander('View customer-level detail (sample)'):
                st.dataframe(customer_orders.head(20).rename(columns={'customer_id': 'Customer ID', 'orders': 'Delivered orders', 'customer_sales': 'Delivered sales (₹)', 'customer_type': 'Customer type'}), width='stretch', hide_index=True)
    with operations_tab:
        st.subheader('Order fulfilment')
        if d.empty:
            st.info('No orders match the selected filters.')
        else:
            status_mix = d.order_status.value_counts().rename_axis('order_status').reset_index(name='orders')
            a, b = st.columns(2)
            fig = px.pie(status_mix, names='order_status', values='orders', hole=.5, title='Order status mix (all filtered orders)')
            a.plotly_chart(fig, width='stretch')
            if not delivered.empty:
                on_time_rate = (~delivered.is_late_delivery.astype(bool)).mean()
                late_rate = delivered.is_late_delivery.astype(bool).mean()
                avg_ship = delivered.shipping_days.mean()
                op_kpis = [
                    ('On-time delivery rate', f'{on_time_rate:.1%}', 'On-time delivered orders divided by all delivered orders.'),
                    ('Late delivery rate', f'{late_rate:.1%}', 'Late delivered orders divided by all delivered orders.'),
                    ('Average shipping time', f'{avg_ship:.1f} days', 'Mean shipping days for delivered orders.'),
                    ('Cancellation rate', f'{cancellation_rate:.1%}', 'Cancelled orders divided by all orders in the current filtered population.'),
                ]
                kpi(op_kpis)
                delivery = delivered.groupby('is_late_delivery', as_index=False).agg(orders=('order_id', 'nunique'), avg_shipping_days=('shipping_days', 'mean'))
                delivery['Delivery timing'] = delivery.is_late_delivery.map({0: 'On time', 1: 'Late'})
                fig = px.bar(delivery, x='Delivery timing', y='orders', title='Delivered orders by delivery timing', text='orders')
                b.plotly_chart(style_axes(fig, 'Delivery timing', 'Delivered orders'), width='stretch')
                st.caption('Order status (Delivered, Returned, Cancelled) describes the final order outcome. Delivery timing (On time/Late) is calculated only for delivered orders.')
                st.dataframe(delivery[['Delivery timing', 'orders', 'avg_shipping_days']].rename(columns={'orders': 'Orders', 'avg_shipping_days': 'Average shipping days'}), width='stretch', hide_index=True)

                state_ops = delivered.groupby('state', as_index=False).agg(
                    delivered_orders=('order_id', 'nunique'),
                    late_rate=('is_late_delivery', 'mean'),
                    average_shipping_days=('shipping_days', 'mean'),
                )
                state_ops = state_ops[state_ops.delivered_orders >= 30].sort_values('late_rate', ascending=False)
                st.subheader('Delivery performance by state')
                st.caption('States are included only when at least 30 delivered orders are present in the current filtered sample, reducing unstable comparisons from very small groups.')
                if not state_ops.empty:
                    state_chart = state_ops.head(10).sort_values('late_rate')
                    fig = px.bar(state_chart, x='late_rate', y='state', orientation='h', text=state_chart.late_rate.map(lambda x: f'{x:.1%}'),
                                 hover_data={'delivered_orders': True, 'average_shipping_days': ':.1f'}, title='Highest late-delivery rates among eligible states')
                    fig.update_traces(textposition='outside', cliponaxis=False)
                    st.plotly_chart(style_axes(fig, 'Late delivery rate', 'State'), width='stretch')
                    state_ops_display = state_ops[['state', 'delivered_orders', 'late_rate', 'average_shipping_days']].copy()
                    state_ops_display = state_ops_display.rename(columns={
                        'state': 'State',
                        'delivered_orders': 'Delivered orders',
                        'late_rate': 'Late delivery rate',
                        'average_shipping_days': 'Average shipping days',
                    })
                    state_ops_display['Late delivery rate'] = state_ops_display['Late delivery rate'].map(lambda value: f'{value:.1%}')
                    state_ops_display['Average shipping days'] = state_ops_display['Average shipping days'].map(lambda value: f'{value:.1f}')
                    st.dataframe(state_ops_display, width='stretch', hide_index=True)
                    priority = state_ops.iloc[0]
                    ops_text = f"{priority.state} has the highest late-delivery rate ({priority.late_rate:.1%}) among states with at least 30 delivered orders in the current filtered sample. Its average shipping time is {priority.average_shipping_days:.1f} days. Review carrier capacity, dispatch delays and route-level data before assigning a cause."
                else:
                    ops_text = 'No state has at least 30 delivered orders under the current filters. Broaden the filters before comparing state-level delivery performance.'
            else:
                st.info('Delivery timing KPIs are unavailable because no delivered orders match the current filters.')
                ops_text = 'The current filters contain no delivered orders. Review the order-status mix and broaden the filters to assess fulfilment.'
            add_business_note('Operations takeaway', f"Cancellation rate is {cancellation_rate:.1%} across all orders in the current filtered population. {ops_text} This synthetic dataset is for dashboard practice, not a real logistics performance assessment.")
    st.download_button('Download BI filtered dataset', d.to_csv(index=False).encode('utf-8'), file_name='ecommerce_bi_filtered_demo.csv', mime='text/csv')

# 06 · Advanced Statistics -------------------------------------------------------
elif page == PAGES[5]:
    st.header('Advanced Statistics · Inference, Power & Multiple Testing')
    st.warning('SYNTHETIC DATA · These results demonstrate statistical methods on simulated e-commerce and A/B-test data. They are not findings about real Indian markets or campaigns.')
    sdir = BASE / '06_india_advanced_statistics/outputs'
    if not (sdir / 'ab_advanced_results.csv').exists():
        st.error('Statistics outputs not found. Run `python 06_india_advanced_statistics/src/analyze.py` first.')
    else:
        ab_res = pd.read_csv(sdir / 'ab_advanced_results.csv').iloc[0]
        tab_ab, tab_ec, tab_mt = st.tabs(['A/B test inference', 'E-commerce hypothesis tests', 'Multiple testing'])
        with tab_ab:
            kpi([
                ('Absolute lift', f'{ab_res.abs_lift_pp:+.3f} pp', 'Treatment minus control conversion rate.'),
                ('95% CI (Newcombe)', f'[{ab_res.newcombe_ci95_low_pp:+.2f}, {ab_res.newcombe_ci95_high_pp:+.2f}] pp', 'Interval for the difference in proportions.'),
                ('P(treatment better)', f'{ab_res.bayes_prob_treatment_better:.1%}', 'Bayesian beta-binomial posterior with a uniform prior.'),
                ('Observed power', f'{ab_res.observed_power:.0%}', 'Power to detect the observed lift at alpha=5% with this sample.'),
            ])
            st.write(
                f"Z-test p = {ab_res.z_test_p_value:.4f}; permutation p = {ab_res.permutation_p_value:.4f}. "
                f"With this sample, lifts below about {ab_res.mde_abs_pp_at_80pct_power:.2f} pp cannot be detected reliably (80% power). "
                f"A 20% relative lift would need roughly {int(ab_res.users_per_group_for_20pct_rel_lift):,} users per group."
            )
            a, b = st.columns(2)
            a.image(str(sdir / 'permutation_null.png'), caption='Permutation null distribution')
            b.image(str(sdir / 'bayesian_relative_lift.png'), caption='Posterior of relative lift')
        with tab_ec:
            tests = pd.read_csv(sdir / 'ecommerce_hypothesis_tests.csv')
            show = tests[['test', 'statistic', 'p_value', 'effect_size', 'effect_measure', 'n', 'significant_at_5pct']].copy()
            show['p_value'] = show.p_value.map(lambda v: '< 0.001' if v < 0.001 else f'{v:.3f}')
            st.dataframe(show, width='stretch', hide_index=True)
            st.caption('Every p-value is paired with an effect size: with 16,000+ orders even trivial differences can be significant.')
            odds = pd.read_csv(sdir / 'low_review_logit_odds_ratios.csv')
            st.subheader('Odds of a low (<= 2) review')
            st.dataframe(odds, width='stretch', hide_index=True)
        with tab_mt:
            seg = pd.read_csv(sdir / 'ab_channel_multiple_testing.csv')
            st.image(str(sdir / 'multiple_testing.png'))
            st.dataframe(seg, width='stretch', hide_index=True)
            st.caption('Testing four channels at once inflates false positives; Holm and Benjamini-Hochberg adjust for that.')

st.markdown('---')
st.caption('InsightIndia · Reproducible analysis · See project README files for data provenance, methods, SQL, and limitations.')
