# Data contract

`synthetic_daily.csv` is generated with Python's seeded random generator (seed 740), 756 weekday observations, and artificial price regimes. It is not exchange data and does not represent a real security. Weekdays are not an exchange calendar.

To research a real security, provide a CSV with `date,open,high,low,close,volume`, ISO dates in ascending order, positive finite values and consistent OHLC ranges. Use daily trading-session bars. Adjust **all** OHLC fields consistently for splits; document dividend treatment, vendor, retrieval date, symbol, date range and license. The loader cannot infer adjustment consistency or calendar completeness. Do not upload licensed market data without redistribution rights.
