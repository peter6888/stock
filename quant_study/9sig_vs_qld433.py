"""
Refactored 9Sig vs Static 1.4x comparison using shared modules.
Demonstrates the power of the refactored codebase with minimal code.
"""

from backtest_utils import (
    download_price_data, 
    download_dividend_data, 
    calculate_performance_stats
)
from strategies import (
    backtest_9sig_strategy,
    backtest_static_leverage_strategy,
    TICKERS_STATIC_14X
)
import matplotlib.pyplot as plt

# Configuration
START = "2015-07-01"
END = "2025-07-01"
CAPITAL = 10_000
TICKERS = ["QQQ", "QLD", "TQQQ", "BIL"]

def main():
    """Run 9Sig vs Static 1.4x comparison."""
    
    # Download data (much cleaner than before!)
    prices = download_price_data(TICKERS, START, END)
    dividends = download_dividend_data(TICKERS)
    
    # Run backtests (simplified function calls)
    val_9sig, _ = backtest_9sig_strategy(prices, dividends, CAPITAL)
    val_14x, _ = backtest_static_leverage_strategy(
        prices, dividends, TICKERS_STATIC_14X, (4.0, 9.67, 3.0), CAPITAL
    )
    
    # Calculate performance (standardized across all scripts)
    rf_daily = prices["BIL"].pct_change()
    res_9sig = calculate_performance_stats(val_9sig, rf_daily, "9Sig (TQQQ + BIL)")
    res_14x = calculate_performance_stats(val_14x, rf_daily, "Static 1.4× (QQQ + QLD + BIL)")
    
    # Simple plot (could also use create_comparison_plot for more comprehensive view)
    plt.figure(figsize=(12, 6))
    plt.plot(val_9sig.index, val_9sig, label="9Sig (TQQQ + BIL)", linewidth=2)
    plt.plot(val_14x.index, val_14x, label="Static 1.4× (QQQ + QLD + BIL)", linewidth=2)
    plt.title("9Sig vs Static 1.4× — Total Value")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
