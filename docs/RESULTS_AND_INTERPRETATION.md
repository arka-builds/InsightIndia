# Results and interpretation guide

## Official public-data projects

### Road safety (MoRTH, 2019–2023)
MoRTH's *Road Accidents in India 2023* reports 480,583 accidents and 172,890 persons killed in 2023, compared with 461,312 accidents and 168,491 persons killed in 2022. The 2023 state accident leaders were Tamil Nadu (67,213), Madhya Pradesh (55,327), Kerala (48,091), Uttar Pradesh (44,534) and Karnataka (43,440). The highest fatality counts were Uttar Pradesh (23,652), Tamil Nadu (18,347) and Maharashtra (15,366). The dataset includes the full state/UT table for 2019–2023 and reconciles to the national totals. Absolute counts are not exposure-adjusted risk.

### State government finances (RBI State Finances 2025-26)
The RBI report gives 2025-26 budget estimates of ₹63.6 lakh crore aggregate expenditure, ₹52.1 lakh crore revenue expenditure, ₹11.4 lakh crore capital expenditure and ₹11.8 lakh crore gross fiscal deficit (3.3% of GDP). The same report shows capital expenditure at ₹4.6 lakh crore in 2020-21 and ₹11.4 lakh crore in 2025-26 (BE). These are consolidated State/UT amounts; estimate labels matter. 2024-25 PA, RE and BE are not interchangeable.

## Synthetic case-study projects

### E-commerce
The 18,000-row synthetic dataset contains 16,330 delivered orders. Generated delivered-order value is approximately ₹4.85 crore. These are simulation outputs only and do not represent an Indian retailer or marketplace.

### Marketing A/B experiment
Control conversion is approximately 2.72%; treatment conversion is approximately 3.16%. Relative lift is approximately 16.4%, but the two-sided two-proportion test p-value is approximately 0.0623, so the difference is not statistically significant at alpha = 0.05. This is an educational synthetic example, not a real campaign result.

## Data quality fixture
The finance QA sample deliberately contains missing, negative and whitespace issues. Its scorecard demonstrates validation logic; it does not assess RBI source-data quality.
