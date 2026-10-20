"""Validated data, causal strategies, execution accounting, and metrics."""
import csv
import math
from datetime import date
from statistics import mean, stdev


def load_bars(path):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    bars = []
    previous = None
    for row in rows:
        day = date.fromisoformat(row["date"])
        if previous is not None and day <= previous:
            raise ValueError("Dates must be unique and strictly increasing")
        bar = {key: float(row[key]) for key in ("open", "high", "low", "close", "volume")}
        if not all(math.isfinite(value) for value in bar.values()):
            raise ValueError("Non-finite OHLCV value")
        if min(bar[k] for k in ("open", "high", "low", "close")) <= 0 or bar["volume"] <= 0:
            raise ValueError("Prices and volume must be positive")
        if not bar["low"] <= min(bar["open"], bar["close"]) <= max(bar["open"], bar["close"]) <= bar["high"]:
            raise ValueError("Inconsistent OHLC prices")
        bars.append(dict(date=day.isoformat(), **bar))
        previous = day
    if len(bars) < 2:
        raise ValueError("At least two bars required")
    return bars


def signals(bars, strategy="breakout", window=20, threshold=0.02):
    """Targets known after each close; execution occurs at the NEXT open.

    Breakout: enter above prior window high, exit below prior window low.
    VWAP: enter below rolling volume-weighted typical price by threshold,
    exit when close recovers to that rolling price. This is daily rolling
    VWAP, not intraday session VWAP.
    """
    if strategy not in ("breakout", "vwap", "buy_hold"):
        raise ValueError("Unknown strategy")
    if window < 2 or not 0 < threshold < 1:
        raise ValueError("Invalid window or threshold")
    targets, position = [], 0
    for i, bar in enumerate(bars):
        if strategy == "buy_hold":
            position = 1
        elif i >= window:
            history = bars[i-window:i]
            if strategy == "breakout":
                if bar["close"] > max(b["high"] for b in history):
                    position = 1
                elif bar["close"] < min(b["low"] for b in history):
                    position = 0
            else:
                history = bars[i-window+1:i+1]
                vwap = sum((b["high"]+b["low"]+b["close"])/3*b["volume"] for b in history)/sum(b["volume"] for b in history)
                if bar["close"] < vwap*(1-threshold):
                    position = 1
                elif bar["close"] >= vwap:
                    position = 0
        targets.append(position)
    return targets


def backtest(bars, targets, initial_cash=10000.0, fee_bps=5.0, slippage_bps=5.0):
    """All-in fractional shares, no leverage, cash earns zero interest.

    At open i, execute target i-1. Mark equity at close i. Open positions
    remain marked to market at the end; no artificial terminal liquidation.
    """
    if len(bars) != len(targets) or not bars:
        raise ValueError("Bars and targets must have matching nonzero lengths")
    if not math.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError("Initial cash must be positive and finite")
    if any(t not in (0, 1) for t in targets):
        raise ValueError("Targets must be zero or one")
    if not all(math.isfinite(x) and 0 <= x < 10000 for x in (fee_bps, slippage_bps)):
        raise ValueError("Costs must be finite and in [0, 10000) bps")
    fee, slip = fee_bps/10000, slippage_bps/10000
    cash, shares, equity, fills = initial_cash, 0.0, [], []
    for i, bar in enumerate(bars):
        target = targets[i-1] if i else 0
        side = "BUY" if target and shares == 0 else "SELL" if not target and shares > 0 else None
        if side:
            price = bar["open"]*(1+slip if side == "BUY" else 1-slip)
            quantity = cash/(price*(1+fee)) if side == "BUY" else shares
            commission = quantity*price*fee
            cash += (-quantity*price-commission) if side == "BUY" else quantity*price-commission
            shares = quantity if side == "BUY" else 0.0
            fills.append(dict(date=bar["date"], side=side, price=price, shares=quantity, fee=commission))
        equity.append(dict(date=bar["date"], equity=cash+shares*bar["close"], shares=shares))
    returns = [equity[i]["equity"]/equity[i-1]["equity"]-1 for i in range(1, len(equity))]
    peak, drawdown = initial_cash, 0.0
    for row in equity:
        peak = max(peak, row["equity"])
        drawdown = min(drawdown, row["equity"]/peak-1)
    volatility = stdev(returns) if len(returns)>1 else 0
    metrics = dict(total_return=equity[-1]["equity"]/initial_cash-1,
                   annualized_return=(equity[-1]["equity"]/initial_cash)**(252/max(1,len(returns)))-1,
                   annualized_volatility=volatility*math.sqrt(252),
                   sharpe=mean(returns)/volatility*math.sqrt(252) if volatility else None,
                   max_drawdown=drawdown, fills=len(fills),
                   exposure=sum(row["shares"]>0 for row in equity)/len(equity))
    return dict(metrics=metrics, equity=equity, fills=fills)
