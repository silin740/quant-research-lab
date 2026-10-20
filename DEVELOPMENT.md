# Development and attribution

Initial implementation prepared with OpenAI Codex assistance at the owner's request. Review and understand the code before presenting it in an interview. No earlier project source was available in the working directory.

## Reproduce

Run `python scripts/generate_demo.py`, then `python -m quantlab.cli` and `python -m unittest discover -s tests -v`. The generator has a fixed seed. The checked-in report is an engineering demo, not a financial finding.

## Interview walkthrough

Explain why a close-derived signal must trade at a later timestamp, calculate a buy and sell including bps costs, describe how full-period metrics differ from holdout metrics, and explain why synthetic data cannot establish strategy efficacy.

## Validation record

The 11 core unit/integration tests and CLI run passed on Python 3.9.6. Dashboard source was syntax-checked; interactive execution could not be verified locally because package-index network access was unavailable. GitHub Actions provides the additional Python-version checks when enabled.
