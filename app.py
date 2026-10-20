"""Optional interactive research dashboard: streamlit run app.py."""
from pathlib import Path
import tempfile
import streamlit as st
from quantlab.core import load_bars, signals, backtest

st.set_page_config(page_title="Quant Research Lab", layout="wide")
st.title("Quant Research Lab")
st.caption("Daily-bar strategy research • Next-open execution • Explicit trading costs")
st.warning("Bundled data is synthetic. Demo performance is not evidence of a profitable strategy.")
file = st.sidebar.file_uploader("Upload OHLCV CSV", type="csv")
window = st.sidebar.slider("Lookback bars", 5, 100, 20)
threshold = st.sidebar.slider("VWAP entry discount", 0.005, 0.10, 0.02, 0.005)
fee = st.sidebar.number_input("Commission (bps per side)", 0.0, 100.0, 5.0)
slip = st.sidebar.number_input("Slippage (bps per side)", 0.0, 100.0, 5.0)
try:
    if file:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"input.csv"
            path.write_bytes(file.getvalue())
            bars = load_bars(path)
    else:
        bars = load_bars("data/synthetic_daily.csv")
    curves, metrics = {}, []
    for name in ("breakout", "vwap", "buy_hold"):
        result = backtest(bars, signals(bars,name,window,threshold),fee_bps=fee,slippage_bps=slip)
        curves[name] = [r["equity"] for r in result["equity"]]
        metrics.append(dict(strategy=name, **result["metrics"]))
    st.subheader("Portfolio equity · starting capital $10,000")
    # An indexed dictionary preserves actual ISO dates on the chart.
    import pandas as pd
    st.line_chart(pd.DataFrame(curves,index=pd.to_datetime([b["date"] for b in bars])))
    st.dataframe(metrics, use_container_width=True)
    st.caption("Sharpe assumes 252 daily observations/year and zero risk-free rate. Returns are fractions. Final positions remain open.")
    st.download_button("Download metrics", __import__("json").dumps(metrics,indent=2), "metrics.json")
except (ValueError, KeyError, UnicodeError) as error:
    st.error(str(error))
