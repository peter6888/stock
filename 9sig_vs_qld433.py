# 9Sig (TQQQ+BIL) vs Static ~1.4x (QQQ+QLD+BIL)
# pip install yfinance pandas numpy matplotlib

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

START = "2015-07-01"
END   = "2025-07-01"
CAPITAL = 10_000  # start capital

tickers = ["QQQ", "QLD", "TQQQ", "BIL"]

# ----- Download prices -----
# Download all tickers at once to get proper DataFrame structure
data = yf.download(tickers, start=START, end=END, group_by='ticker')
if data.empty:
    raise ValueError("Failed to download data")

# Extract close prices for each ticker
prices_dict = {}
for ticker in tickers:
    if len(tickers) == 1:
        # Single ticker case - no multi-level columns
        prices_dict[ticker] = data['Close']
    else:
        # Multiple tickers case - multi-level columns
        prices_dict[ticker] = data[ticker]['Close']

prices = pd.DataFrame(prices_dict).dropna()


# ----- Dividends -----
divs = {t: yf.Ticker(t).dividends for t in tickers}
for t in tickers:
    if divs[t] is None or len(divs[t]) == 0:
        divs[t] = pd.Series(dtype=float)

def reinvest(units_col, price_col, div_series, frame):
    """DRIP: add units on each dividend date = cash dividend / price."""
    for dt, amt in div_series.items():
        if dt in frame.index:
            # Ensure we have price data for the dividend date
            if dt in frame.index:
                add_units = (amt * frame.loc[dt, units_col]) / frame.loc[dt, price_col]
                frame.loc[dt:, units_col] += add_units


# ----- Strategy A: 9Sig (TQQQ + BIL, quarterly 9% target, TQQQ target weight = 60%) -----
def backtest_9sig(prices, divs, start_cap=CAPITAL, tqqq_w=0.60, q_growth=1.09):
    # Columns are now simply ticker symbols
    df = prices[["TQQQ", "BIL"]].copy()
    df["TQQQ_units"] = start_cap * tqqq_w / df.iloc[0]["TQQQ"]
    df["BIL_units"]  = start_cap * (1 - tqqq_w) / df.iloc[0]["BIL"]
    df["Target"] = np.nan

    # Reinvest dividends
    reinvest("TQQQ_units", "TQQQ", divs["TQQQ"], df)
    reinvest("BIL_units", "BIL", divs["BIL"], df)

    # Initial total
    df["Total"] = df["TQQQ"] * df["TQQQ_units"] + df["BIL"] * df["BIL_units"]

    # Quarterly target path
    # Fix: Use 'QE' for Quarterly End frequency and align to actual trading days
    q_end_dates = df.resample("QE").first().index
    q_dates = []
    for q_end in q_end_dates:
        # Find the last available trading day in that quarter
        available_dates = df.index[df.index <= q_end]
        if len(available_dates) > 0:
            q_dates.append(available_dates[-1])
    
    for i, d in enumerate(q_dates):
        df.loc[d, "Target"] = start_cap if i == 0 else df.loc[q_dates[i-1], "Target"] * q_growth


    # Quarterly rebalance toward target * tqqq_w
    for i in range(1, len(q_dates)):
        d = q_dates[i]
        tpx, bpx = df.loc[d, ["TQQQ", "BIL"]]
        tgt = df.loc[q_dates[i-1], "Target"] * q_growth # Use previous quarter's target for calculation
        desired_tqqq_val = tgt * tqqq_w
        curr_tqqq_val = df.loc[d, "TQQQ_units"] * tpx
        delta = desired_tqqq_val - curr_tqqq_val
        df.loc[d:, "TQQQ_units"] += delta / tpx
        df.loc[d:, "BIL_units"]  -= delta / bpx


    df["Total"] = df["TQQQ"] * df["TQQQ_units"] + df["BIL"] * df["BIL_units"]
    return df["Total"].dropna(), df

# ----- Strategy B: Static ~1.4x via QQQ:QLD:BIL = 4 : 9.67 : 3 (quarterly rebalance) -----
def backtest_static_14x(prices, divs, start_cap=CAPITAL, w=(4.0, 9.67, 3.0)):
    # Columns are now simply ticker symbols
    df = prices[["QQQ", "QLD", "BIL"]].copy()
    weights = np.array(w, dtype=float)
    weights = weights / weights.sum()  # normalize

    # Initial units by target weights
    df["QQQ_units"] = start_cap * weights[0] / df.iloc[0]["QQQ"]
    df["QLD_units"] = start_cap * weights[1] / df.iloc[0]["QLD"]
    df["BIL_units"] = start_cap * weights[2] / df.iloc[0]["BIL"]

    # Reinvest dividends
    reinvest("QQQ_units", "QQQ", divs["QQQ"], df)
    reinvest("QLD_units", "QLD", divs["QLD"], df)
    reinvest("BIL_units", "BIL", divs["BIL"], df)


    df["Total"] = (df["QQQ"] * df["QQQ_units"] +
                   df["QLD"] * df["QLD_units"] +
                   df["BIL"] * df["BIL_units"])

    # Quarterly rebalance back to target weights
    # Fix: Use 'QE' for Quarterly End frequency and align to actual trading days
    q_end_dates = df.resample("QE").first().index
    q_dates = []
    for q_end in q_end_dates:
        # Find the last available trading day in that quarter
        available_dates = df.index[df.index <= q_end]
        if len(available_dates) > 0:
            q_dates.append(available_dates[-1])
    
    for i in range(1, len(q_dates)):
        d = q_dates[i]
        tot = df.loc[d, "Total"]
        tgt_vals = tot * weights  # desired dollars in [QQQ, QLD, BIL]
        deltas = tgt_vals - np.array([
            df.loc[d, "QQQ_units"] * df.loc[d, "QQQ"],
            df.loc[d, "QLD_units"] * df.loc[d, "QLD"],
            df.loc[d, "BIL_units"] * df.loc[d, "BIL"],
        ])
        df.loc[d:, "QQQ_units"] += deltas[0] / df.loc[d, "QQQ"]
        df.loc[d:, "QLD_units"] += deltas[1] / df.loc[d, "QLD"]
        df.loc[d:, "BIL_units"] += deltas[2] / df.loc[d, "BIL"]

    df["Total"] = (df["QQQ"] * df["QQQ_units"] +
                   df["QLD"] * df["QLD_units"] +
                   df["BIL"] * df["BIL_units"])
    return df["Total"].dropna(), df

def perf_stats(v, rf=None, name="Strategy"):
    v = v.dropna()
    r = v.pct_change().dropna()
    if rf is not None:
        rf = rf.reindex(r.index).fillna(0.0)
        ex = r - rf
    else:
        ex = r
    years = (v.index[-1] - v.index[0]).days / 365.25
    cagr = (v.iloc[-1] / v.iloc[0])**(1/years) - 1
    roll_max = v.cummax()
    dd = v / roll_max - 1.0
    mdd = dd.min()
    vol = ex.std() * np.sqrt(252)
    sharpe = (ex.mean() / ex.std() * np.sqrt(252)) if ex.std() > 0 else np.nan

    print(f"\n{name} results:")
    print(f"  Period: {v.index[0].date()} → {v.index[-1].date()}")
    print(f"  Final value: ${v.iloc[-1]:,.2f}")
    print(f"  APR/CAGR: {cagr*100:.2f}%")
    print(f"  Max drawdown: {mdd*100:.2f}%")
    print(f"  Ann. volatility: {vol*100:.2f}%")
    print(f"  Sharpe (excess vs BIL): {sharpe:.2f}")
    return {"final": v.iloc[-1], "cagr": cagr, "mdd": mdd, "vol": vol, "sharpe": sharpe}


# ----- Run both backtests -----
val_9sig, df_9sig   = backtest_9sig(prices, divs)
val_14x, df_14x     = backtest_static_14x(prices, divs)
rf_daily = prices["BIL"].pct_change()

# Print results
res_9 = perf_stats(val_9sig, rf_daily, "9Sig (TQQQ + BIL)")
res_14 = perf_stats(val_14x, rf_daily, "Static 1.4× (QQQ + QLD + BIL)")

# Plot curve
plt.figure(figsize=(12,6))
plt.plot(val_9sig.index, val_9sig, label="9Sig (TQQQ + BIL)")
plt.plot(val_14x.index, val_14x, label="Static 1.4× (QQQ + QLD + BIL)")
plt.title("9Sig vs Static 1.4× — Total Value")
plt.xlabel("Date"); plt.ylabel("Portfolio Value ($)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()