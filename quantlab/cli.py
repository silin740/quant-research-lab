"""Run reproducible full-period and chronological holdout experiments."""
import argparse
import csv
import json
from pathlib import Path
from .core import load_bars, signals, backtest


def run(path, output, window=20, threshold=0.02, fee_bps=5, slippage_bps=5):
    bars = load_bars(path)
    if len(bars) < max(30, window*2):
        raise ValueError("Need at least max(30, 2*window) bars for chronological evaluation")
    split = int(len(bars)*0.7)
    report = {"data":str(path), "bars":len(bars), "holdout_start":bars[split]["date"],
              "parameters":dict(window=window, threshold=threshold, fee_bps=fee_bps, slippage_bps=slippage_bps),
              "results":{}}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for strategy in ("breakout", "vwap", "buy_hold"):
        targets = signals(bars, strategy, window, threshold)
        result = backtest(bars, targets, fee_bps=fee_bps, slippage_bps=slippage_bps)
        # Carry signal history but start holdout with fresh cash. The first
        # holdout open can execute the signal from the last training close.
        holdout = backtest(bars[split-1:], targets[split-1:], fee_bps=fee_bps, slippage_bps=slippage_bps)
        report["results"][strategy] = dict(full=result["metrics"], holdout=holdout["metrics"])
        for name in ("equity", "fills"):
            rows = result[name]
            with (output/f"{strategy}_{name}.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, lineterminator="\n", fieldnames=list(rows[0]) if rows else ["date","side","price","shares","fee"])
                writer.writeheader()
                writer.writerows(rows)
    (output/"summary.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/synthetic_daily.csv")
    parser.add_argument("--output", default="reports")
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=0.02)
    parser.add_argument("--fee-bps", type=float, default=5)
    parser.add_argument("--slippage-bps", type=float, default=5)
    args = parser.parse_args()
    print(json.dumps(run(args.data,args.output,args.window,args.threshold,args.fee_bps,args.slippage_bps),indent=2))


if __name__ == "__main__":
    main()
