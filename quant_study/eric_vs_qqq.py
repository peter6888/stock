# Eric's Strategy vs QQQ Comparison
# Strategy: 20% BIL, 30% QQQ, 40% SCHD, 10% QLD, 10% BTC-USD
# Annual rebalancing with dividend reinvestment

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

START = "2015-07-01"
END = "2025-07-01"
CAPITAL = 10_000  # start capital

# Strategy allocation
WEIGHTS = {
    'BIL': 0.20,   # 20% T-Bills
    'QQQ': 0.30,   # 30% QQQ
    'SCHD': 0.40,  # 40% SCHD
    'QLD': 0.10,   # 10% QLD
    'BTC-USD': 0.10  # 10% Bitcoin
}

tickers = list(WEIGHTS.keys())

# ----- Download prices -----
print("Downloading price data...")
data = yf.download(tickers, start=START, end=END, group_by='ticker')
if data.empty:
    raise ValueError("Failed to download data")

# Extract close prices for each ticker
prices_dict = {}
for ticker in tickers:
    if len(tickers) == 1:
        prices_dict[ticker] = data['Close']
    else:
        prices_dict[ticker] = data[ticker]['Close']

prices = pd.DataFrame(prices_dict).dropna()

# ----- Download dividends -----
print("Downloading dividend data...")
divs = {}
for ticker in tickers:
    try:
        div_data = yf.Ticker(ticker).dividends
        divs[ticker] = div_data if div_data is not None and len(div_data) > 0 else pd.Series(dtype=float)
    except:
        divs[ticker] = pd.Series(dtype=float)

def reinvest_dividends(units_col, price_col, div_series, df):
    """Reinvest dividends by adding units"""
    for dt, amt in div_series.items():
        if dt in df.index:
            add_units = (amt * df.loc[dt, units_col]) / df.loc[dt, price_col]
            df.loc[dt:, units_col] += add_units

def backtest_eric_strategy(prices, divs, weights, start_cap=CAPITAL):
    """Backtest Eric's diversified strategy with annual rebalancing"""
    df = prices.copy()
    
    # Initialize units based on target weights
    for ticker in tickers:
        weight = weights[ticker]
        df[f"{ticker}_units"] = start_cap * weight / df.iloc[0][ticker]
    
    # Reinvest dividends
    for ticker in tickers:
        reinvest_dividends(f"{ticker}_units", ticker, divs[ticker], df)
    
    # Calculate total value
    def calc_total(row):
        return sum(row[ticker] * row[f"{ticker}_units"] for ticker in tickers)
    
    df["Total"] = df.apply(calc_total, axis=1)
    
    # Annual rebalancing
    annual_dates = df.resample("YE").first().index
    rebalance_dates = []
    for year_end in annual_dates:
        # Find the last available trading day in that year
        available_dates = df.index[df.index <= year_end]
        if len(available_dates) > 0:
            rebalance_dates.append(available_dates[-1])
    
    for i in range(1, len(rebalance_dates)):
        d = rebalance_dates[i]
        total_val = df.loc[d, "Total"]
        
        # Rebalance to target weights
        for ticker in tickers:
            target_val = total_val * weights[ticker]
            current_val = df.loc[d, f"{ticker}_units"] * df.loc[d, ticker]
            delta = target_val - current_val
            df.loc[d:, f"{ticker}_units"] += delta / df.loc[d, ticker]
    
    # Recalculate total after rebalancing
    df["Total"] = df.apply(calc_total, axis=1)
    return df["Total"].dropna(), df

def backtest_qqq_buyhold(prices, divs, start_cap=CAPITAL):
    """Backtest QQQ buy and hold with dividend reinvestment"""
    df = prices[["QQQ"]].copy()
    df["QQQ_units"] = start_cap / df.iloc[0]["QQQ"]
    
    # Reinvest QQQ dividends
    reinvest_dividends("QQQ_units", "QQQ", divs["QQQ"], df)
    
    df["Total"] = df["QQQ"] * df["QQQ_units"]
    return df["Total"].dropna(), df

def perf_stats(v, rf=None, name="Strategy"):
    """Calculate performance statistics"""
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
    print(f"  Sharpe ratio: {sharpe:.2f}")
    return {"final": v.iloc[-1], "cagr": cagr, "mdd": mdd, "vol": vol, "sharpe": sharpe}

# ----- Run backtests -----
print("\nRunning backtests...")
val_eric, df_eric = backtest_eric_strategy(prices, divs, WEIGHTS)
val_qqq, df_qqq = backtest_qqq_buyhold(prices, divs)

# Calculate risk-free rate for Sharpe ratio
rf_daily = prices["BIL"].pct_change()

# Print results
res_eric = perf_stats(val_eric, rf_daily, "Eric's Strategy")
res_qqq = perf_stats(val_qqq, rf_daily, "QQQ Buy & Hold")

# Plot comparison
plt.figure(figsize=(14, 8))
plt.plot(val_eric.index, val_eric, label="Eric's Strategy (BIL/QQQ/SCHD/QLD/BTC)", linewidth=2)
plt.plot(val_qqq.index, val_qqq, label="QQQ Buy & Hold", linewidth=2)
plt.title("Eric's Diversified Strategy vs QQQ Buy & Hold", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Portfolio Value ($)", fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# Print allocation summary
print(f"\n--- Strategy Allocation ---")
for ticker, weight in WEIGHTS.items():
    print(f"  {ticker}: {weight*100:.0f}%")

print(f"\n--- Performance Comparison ---")
print(f"Eric's Strategy: ${res_eric['final']:,.2f} ({res_eric['cagr']*100:.2f}% CAGR)")
print(f"QQQ Buy & Hold: ${res_qqq['final']:,.2f} ({res_qqq['cagr']*100:.2f}% CAGR)")
outperformance = (res_eric['final'] / res_qqq['final'] - 1) * 100
print(f"Outperformance: {outperformance:+.1f}%")
