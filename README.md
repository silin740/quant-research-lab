# Quant Research Lab

A reproducible Python research project for comparing daily momentum breakout and rolling VWAP mean-reversion strategies against buy-and-hold. Includes a dependency-free backtesting engine, optional Streamlit dashboard, chronological holdout evaluation, CSV exports and automated accounting tests.

**Status:** working research prototype. Bundled results use synthetic data and make no claim about real-market profitability. This is a fresh implementation based on earlier strategy discussions; it does not contain recovered prior trading code.

## Quick start

```bash
git clone https://github.com/silin740/quant-research-lab.git
cd quant-research-lab
python3 -m venv .venv
source .venv/bin/activate
python -m quantlab.cli
python -m unittest discover -s tests -v
```

The core uses only Python's standard library. Optional dashboard:

```bash
python -m pip install --upgrade pip
pip install -e '.[dashboard]'
streamlit run app.py
```

Real data:

```bash
python -m quantlab.cli --data path/to/daily.csv --window 20 --fee-bps 5 --slippage-bps 5 --output reports/real
```

See [data contract](data/README.md) before importing market data.

## Strategies and execution

| Strategy | Entry | Exit |
|---|---|---|
| Momentum breakout | Close exceeds the preceding N bars' highest high | Close falls below preceding N bars' lowest low |
| Rolling VWAP reversion | Close falls below N-bar volume-weighted typical price by the entry discount | Close recovers to rolling VWAP |
| Buy-and-hold benchmark | First eligible next open | Remains invested |

Signals are computed after a bar closes and executed at the **following open**. Breakout reference windows exclude the current bar. VWAP includes only bars available at that close; this is **daily rolling VWAP**, not session VWAP. Positions are long-only and all-in with fractional shares. Both buys and sells pay commissions and adverse slippage. Cash earns zero interest; there is no leverage or shorting. Final holdings are marked to the last close without a forced liquidation.

## Evaluation

`reports/summary.json` contains full-period and final-30% chronological holdout metrics. Holdout starts with fresh $10,000; the preceding close is included as a baseline so its known signal can execute at the first holdout open. Parameters are fixed in advance; the code does not tune them on the holdout. The split alone does not establish out-of-sample performance after repeated human experimentation.

Metrics: total return, geometric annualized return, annualized sample volatility, zero-risk-free Sharpe, peak-to-trough maximum drawdown, executed fills and bar exposure. Annualization assumes 252 sessions/year. Fills are individual transactions, not completed round trips. Each strategy exports a dated equity curve and fill ledger.

## Architecture

- `quantlab/core.py`: CSV validation, causal signals, execution and risk metrics.
- `quantlab/cli.py`: reproducible experiments and chronological evaluation.
- `app.py`: CSV upload, cost controls and equity comparison.
- `tests/`: hand-calculated accounting, timing, causality and input validation tests.
- `.github/workflows/tests.yml`: Python 3.9/3.12 test and CLI checks.

## Limitations and next research steps

Fixed bps costs do not model spread variation, market impact, liquidity limits or partial fills. Daily bars hide intraday paths. A single security cannot establish cross-asset robustness; a selected universe can introduce survivorship bias. No corporate-action ingestion, live brokerage integration, parameter optimization or ML model is implemented. Before reporting investment results, use documented real data, preserve an untouched test period and evaluate across multiple securities and cost scenarios.

## Resume description

Quantitative Trading Research Platform | Python, Streamlit, GitHub Actions

- Implemented a daily-bar backtesting engine with next-open execution, fractional-share accounting, commissions and slippage.
- Developed momentum breakout and rolling VWAP strategies with benchmark comparisons and chronological holdout evaluation.
- Added automated tests for execution timing, future-data independence, portfolio accounting and invalid market data.

Use these claims only after you can explain the implementation. Do not describe synthetic returns as real trading performance. See [development notes](DEVELOPMENT.md) for reproduction and attribution.
