# India Digital Marketing A/B Testing — Simulation

**Business question:** In a randomized example, does the treatment group's conversion rate differ from the control group's, and is the observed difference strong enough to support a rollout decision?

## Data
20,000 synthetic user rows generated for this portfolio. This is not a real Indian campaign or platform export. See `data/SOURCE_REGISTER.md`.

## Methods
- Validate one row per user and binary conversion outcome.
- Check group allocation with a sample-ratio mismatch chi-square test.
- Calculate conversion rate and cost per conversion.
- Calculate Wilson confidence intervals for group conversion rates.
- Run a two-sided two-proportion z-test.
- Compare channel-level outcomes as exploratory segmentation only.

## Run
`python 04_india_digital_marketing_ab_test/src/analyze.py`

## Interpretation
The generated example has a positive point estimate for treatment but p > 0.05. Do not interpret it as proof of an actual campaign effect. A real experiment requires a pre-specified hypothesis, power calculation, randomization checks, guardrails and first-party event logs.
