"""
Refactored Eric's Strategy vs QQQ comparison using shared modules.
Shows how the new architecture dramatically reduces code duplication.
"""

from backtest_utils import (
    download_price_data, 
    download_dividend_data, 
    calculate_performance_stats
)
from strategies import (
    backtest_eric_strategy,
    backtest_buy_and_hold,
    ERIC_STRATEGY_BTC
)
import matplotlib.pyplot as plt

# Configuration
START = "2015-07-01"
END = "2025-07-01"
CAPITAL = 10_000

def main():
    """Run Eric's Strategy vs QQQ comparison."""
    
    # Download data
    tickers = list(ERIC_STRATEGY_BTC.keys())
    prices = download_price_data(tickers, START, END)
    dividends = download_dividend_data(tickers)
    
    # Run backtests
    print("\nRunning backtests...")
    val_eric, _ = backtest_eric_strategy(prices, dividends, ERIC_STRATEGY_BTC, CAPITAL)
    val_qqq, _ = backtest_buy_and_hold(prices, dividends, "QQQ", CAPITAL)
    
    # Calculate performance
    rf_daily = prices["BIL"].pct_change()
    res_eric = calculate_performance_stats(val_eric, rf_daily, "Eric's Strategy")
    res_qqq = calculate_performance_stats(val_qqq, rf_daily, "QQQ Buy & Hold")
    
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
    
    # Print allocation and performance summary
    print(f"\n--- Strategy Allocation ---")
    for ticker, weight in ERIC_STRATEGY_BTC.items():
        print(f"  {ticker}: {weight*100:.0f}%")
    
    print(f"\n--- Performance Comparison ---")
    print(f"Eric's Strategy: ${res_eric['final']:,.2f} ({res_eric['cagr']*100:.2f}% CAGR)")
    print(f"QQQ Buy & Hold: ${res_qqq['final']:,.2f} ({res_qqq['cagr']*100:.2f}% CAGR)")
    outperformance = (res_eric['final'] / res_qqq['final'] - 1) * 100
    print(f"Outperformance: {outperformance:+.1f}%")

if __name__ == "__main__":
    main()
