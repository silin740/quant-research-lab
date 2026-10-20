"""Generate artificial weekday OHLCV bars; never represents market prices."""
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

rng = random.Random(740)
day, price, rows = date(2021, 1, 4), 100.0, []
while len(rows) < 756:
    if day.weekday() < 5:
        i = len(rows)
        drift = (0.001, -0.0007, 0.0002)[i//252]
        opening = price*math.exp(rng.gauss(0, 0.003))
        close = opening*math.exp(drift+rng.gauss(0, 0.012))
        high = max(opening, close)*(1+rng.uniform(0.001, 0.012))
        low = min(opening, close)*(1-rng.uniform(0.001, 0.012))
        rows.append(dict(date=day.isoformat(),open=round(opening,4),high=round(high,4),low=round(low,4),close=round(close,4),volume=rng.randint(100000,2000000)))
        price = close
    day += timedelta(days=1)
path = Path(__file__).resolve().parents[1]/'data/synthetic_daily.csv'
with path.open('w',newline='') as handle:
    writer=csv.DictWriter(handle,lineterminator="\n",fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
print(f'Generated {len(rows)} synthetic bars: {path}')
