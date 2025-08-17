# Four Strategy Comparison V2: 9Sig, Static 1x, Eric's Strategy (w/ Gold), and QQQ Buy & Hold
# Eric's strategy modified: BTC replaced with GLD (Gold)
# Comprehensive backtest comparison with performance metrics and visualization

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

START = "2006-07-01"
END = "2025-07-01"
CAPITAL = 10_000  # start capital

# All tickers needed for all strategies
all_tickers = ["QQQ", "QLD", "TQQQ", "BIL", "SCHD", "GLD"]

# Eric's strategy allocation (V2: BTC -> GLD)
ERIC_WEIGHTS = {
    'BIL': 0.20,     # 20% T-Bills
    'QQQ': 0.30,     # 30% QQQ
    'SCHD': 0.40,    # 40% SCHD
    'QLD': 0.10,     # 10% QLD
    'GLD': 0.10      # 10% Gold (replaced BTC)
}

print("Downloading price data for all strategies...")
# ----- Download prices -----
data = yf.download(all_tickers, start=START, end=END, group_by='ticker')
if data.empty:
    raise ValueError("Failed to download data")

# Extract close prices for each ticker
prices_dict = {}
for ticker in all_tickers:
    if len(all_tickers) == 1:
        prices_dict[ticker] = data['Close']
    else:
        prices_dict[ticker] = data[ticker]['Close']

prices = pd.DataFrame(prices_dict).dropna()

print("Downloading dividend data...")
# ----- Download dividends -----
divs = {}
for ticker in all_tickers:
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

# ----- Strategy 1: 9Sig (TQQQ + BIL, quarterly 9% target) -----
def backtest_9sig(prices, divs, start_cap=CAPITAL, tqqq_w=0.60, q_growth=1.09):
    """9Sig strategy with quarterly rebalancing toward 9% growth target"""
    df = prices[["TQQQ", "BIL"]].copy()
    df["TQQQ_units"] = start_cap * tqqq_w / df.iloc[0]["TQQQ"]
    df["BIL_units"] = start_cap * (1 - tqqq_w) / df.iloc[0]["BIL"]
    df["Target"] = np.nan

    # Reinvest dividends
    reinvest_dividends("TQQQ_units", "TQQQ", divs["TQQQ"], df)
    reinvest_dividends("BIL_units", "BIL", divs["BIL"], df)

    # Initial total
    df["Total"] = df["TQQQ"] * df["TQQQ_units"] + df["BIL"] * df["BIL_units"]

    # Quarterly target path and rebalancing
    q_end_dates = df.resample("QE").first().index
    q_dates = []
    for q_end in q_end_dates:
        available_dates = df.index[df.index <= q_end]
        if len(available_dates) > 0:
            q_dates.append(available_dates[-1])
    
    for i, d in enumerate(q_dates):
        df.loc[d, "Target"] = start_cap if i == 0 else df.loc[q_dates[i-1], "Target"] * q_growth

    # Quarterly rebalance toward target * tqqq_w
    for i in range(1, len(q_dates)):
        d = q_dates[i]
        tpx, bpx = df.loc[d, ["TQQQ", "BIL"]]
        tgt = df.loc[q_dates[i-1], "Target"] * q_growth
        desired_tqqq_val = tgt * tqqq_w
        curr_tqqq_val = df.loc[d, "TQQQ_units"] * tpx
        delta = desired_tqqq_val - curr_tqqq_val
        df.loc[d:, "TQQQ_units"] += delta / tpx
        df.loc[d:, "BIL_units"] -= delta / bpx

    df["Total"] = df["TQQQ"] * df["TQQQ_units"] + df["BIL"] * df["BIL_units"]
    return df["Total"].dropna(), df

# ----- Strategy 2: Static 1.0x (QQQ:QLD:BIL = 4:3:3, quarterly rebalance) -----
def backtest_static_1x(prices, divs, start_cap=CAPITAL, w=(4.0, 3, 3.0)):
    """Static 1.0x leverage strategy with quarterly rebalancing"""
    df = prices[["QQQ", "QLD", "BIL"]].copy()
    weights = np.array(w, dtype=float)
    weights = weights / weights.sum()  # normalize

    # Initial units by target weights
    df["QQQ_units"] = start_cap * weights[0] / df.iloc[0]["QQQ"]
    df["QLD_units"] = start_cap * weights[1] / df.iloc[0]["QLD"]
    df["BIL_units"] = start_cap * weights[2] / df.iloc[0]["BIL"]

    # Reinvest dividends
    reinvest_dividends("QQQ_units", "QQQ", divs["QQQ"], df)
    reinvest_dividends("QLD_units", "QLD", divs["QLD"], df)
    reinvest_dividends("BIL_units", "BIL", divs["BIL"], df)

    df["Total"] = (df["QQQ"] * df["QQQ_units"] +
                   df["QLD"] * df["QLD_units"] +
                   df["BIL"] * df["BIL_units"])

    # Quarterly rebalancing
    q_end_dates = df.resample("QE").first().index
    q_dates = []
    for q_end in q_end_dates:
        available_dates = df.index[df.index <= q_end]
        if len(available_dates) > 0:
            q_dates.append(available_dates[-1])
    
    for i in range(1, len(q_dates)):
        d = q_dates[i]
        tot = df.loc[d, "Total"]
        tgt_vals = tot * weights
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

# ----- Strategy 3: Eric's Diversified Strategy V2 (annual rebalancing, with Gold) -----
def backtest_eric_strategy(prices, divs, weights, start_cap=CAPITAL):
    """Eric's diversified strategy with annual rebalancing (V2: includes Gold instead of Bitcoin)"""
    tickers = list(weights.keys())
    df = prices[tickers].copy()
    
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

# ----- Strategy 4: QQQ Buy & Hold -----
def backtest_qqq_buyhold(prices, divs, start_cap=CAPITAL):
    """QQQ buy and hold with dividend reinvestment"""
    df = prices[["QQQ"]].copy()
    df["QQQ_units"] = start_cap / df.iloc[0]["QQQ"]
    
    # Reinvest QQQ dividends
    reinvest_dividends("QQQ_units", "QQQ", divs["QQQ"], df)
    
    df["Total"] = df["QQQ"] * df["QQQ_units"]
    return df["Total"].dropna(), df

def perf_stats(v, rf=None, name="Strategy"):
    """Calculate comprehensive performance statistics"""
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

    print(f"\n{name} Performance:")
    print(f"  Period: {v.index[0].date()} → {v.index[-1].date()}")
    print(f"  Final value: ${v.iloc[-1]:,.2f}")
    print(f"  CAGR: {cagr*100:.2f}%")
    print(f"  Max drawdown: {mdd*100:.2f}%")
    print(f"  Volatility: {vol*100:.2f}%")
    print(f"  Sharpe ratio: {sharpe:.2f}")
    return {"final": v.iloc[-1], "cagr": cagr, "mdd": mdd, "vol": vol, "sharpe": sharpe}

# ----- Run all backtests -----
print("\nRunning all strategy backtests...")

val_9sig, df_9sig = backtest_9sig(prices, divs)
val_14x, df_14x = backtest_static_1x(prices, divs)
val_eric, df_eric = backtest_eric_strategy(prices, divs, ERIC_WEIGHTS)
val_qqq, df_qqq = backtest_qqq_buyhold(prices, divs)

# Calculate risk-free rate for Sharpe ratio
rf_daily = prices["BIL"].pct_change()

# Print all results
print("\n" + "="*60)
print("COMPREHENSIVE STRATEGY COMPARISON V2")
print("="*60)

res_9sig = perf_stats(val_9sig, rf_daily, "9Sig (TQQQ + BIL)")
res_14x = perf_stats(val_14x, rf_daily, "Static 1x (QQQ + QLD + BIL)")
res_eric = perf_stats(val_eric, rf_daily, "Eric's Strategy V2 (BIL/QQQ/SCHD/QLD/GLD)")
res_qqq = perf_stats(val_qqq, rf_daily, "QQQ Buy & Hold")

# Create comprehensive comparison plot
plt.figure(figsize=(16, 10))

# Main comparison plot
plt.subplot(2, 2, 1)
plt.plot(val_9sig.index, val_9sig, label="9Sig", linewidth=2, color='red')
plt.plot(val_14x.index, val_14x, label="Static 1x", linewidth=2, color='blue')
plt.plot(val_eric.index, val_eric, label="Eric's Strategy V2 (w/ Gold)", linewidth=2, color='green')
plt.plot(val_qqq.index, val_qqq, label="QQQ Buy & Hold", linewidth=2, color='orange')
plt.title("Four Strategy Comparison V2 - Portfolio Value", fontsize=14, fontweight='bold')
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.yscale('log')  # Log scale to better show all strategies

# Performance metrics comparison
plt.subplot(2, 2, 2)
strategies = ['9Sig', 'Static 1x', "Eric's V2", 'QQQ B&H']
cagrs = [res_9sig['cagr']*100, res_14x['cagr']*100, res_eric['cagr']*100, res_qqq['cagr']*100]
colors = ['red', 'blue', 'green', 'orange']
bars = plt.bar(strategies, cagrs, color=colors, alpha=0.7)
plt.title("CAGR Comparison", fontsize=14, fontweight='bold')
plt.ylabel("CAGR (%)")
plt.grid(True, alpha=0.3)
for bar, cagr in zip(bars, cagrs):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{cagr:.1f}%', ha='center', va='bottom', fontweight='bold')

# Max Drawdown comparison
plt.subplot(2, 2, 3)
mdds = [res_9sig['mdd']*100, res_14x['mdd']*100, res_eric['mdd']*100, res_qqq['mdd']*100]
bars = plt.bar(strategies, mdds, color=colors, alpha=0.7)
plt.title("Max Drawdown Comparison", fontsize=14, fontweight='bold')
plt.ylabel("Max Drawdown (%)")
plt.grid(True, alpha=0.3)
for bar, mdd in zip(bars, mdds):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 2, 
             f'{mdd:.1f}%', ha='center', va='top', fontweight='bold')

# Sharpe Ratio comparison
plt.subplot(2, 2, 4)
sharpes = [res_9sig['sharpe'], res_14x['sharpe'], res_eric['sharpe'], res_qqq['sharpe']]
bars = plt.bar(strategies, sharpes, color=colors, alpha=0.7)
plt.title("Sharpe Ratio Comparison", fontsize=14, fontweight='bold')
plt.ylabel("Sharpe Ratio")
plt.grid(True, alpha=0.3)
for bar, sharpe in zip(bars, sharpes):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
             f'{sharpe:.2f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()

# Summary table
print("\n" + "="*80)
print("FINAL PERFORMANCE SUMMARY V2")
print("="*80)
print(f"{'Strategy':<25} {'Final Value':<15} {'CAGR':<8} {'Max DD':<8} {'Volatility':<12} {'Sharpe':<8}")
print("-" * 80)
print(f"{'9Sig':<25} ${res_9sig['final']:>12,.0f} {res_9sig['cagr']*100:>6.1f}% {res_9sig['mdd']*100:>6.1f}% {res_9sig['vol']*100:>10.1f}% {res_9sig['sharpe']:>6.2f}")
print(f"{'Static 1x':<25} ${res_14x['final']:>12,.0f} {res_14x['cagr']*100:>6.1f}% {res_14x['mdd']*100:>6.1f}% {res_14x['vol']*100:>10.1f}% {res_14x['sharpe']:>6.2f}")
eric_name = "Eric's Strategy V2"
print(f"{eric_name:<25} ${res_eric['final']:>12,.0f} {res_eric['cagr']*100:>6.1f}% {res_eric['mdd']*100:>6.1f}% {res_eric['vol']*100:>10.1f}% {res_eric['sharpe']:>6.2f}")
print(f"{'QQQ Buy & Hold':<25} ${res_qqq['final']:>12,.0f} {res_qqq['cagr']*100:>6.1f}% {res_qqq['mdd']*100:>6.1f}% {res_qqq['vol']*100:>10.1f}% {res_qqq['sharpe']:>6.2f}")

# Eric's strategy allocation summary
print(f"\n--- Eric's Strategy V2 Allocation ---")
for ticker, weight in ERIC_WEIGHTS.items():
    print(f"  {ticker}: {weight*100:.0f}%")

print(f"\nBacktest V2 completed successfully!")
print(f"Key Change: Bitcoin (BTC) replaced with Gold (GLD) in Eric's strategy")
