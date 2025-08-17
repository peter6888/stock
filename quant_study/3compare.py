"""
Three Strategy Comparison: Static 1x, Eric's Strategy (w/ Gold), and QQQ Buy & Hold
Refactored to use shared utilities and libraries.
Eric's strategy: BTC replaced with GLD (Gold)
"""

from backtest_utils import (
    download_price_data, 
    download_dividend_data, 
    calculate_performance_stats,
    create_comparison_plot,
    print_performance_summary
)
from strategies import (
    backtest_static_leverage_strategy,
    backtest_eric_strategy,
    backtest_buy_and_hold,
    ERIC_STRATEGY_GOLD,
    TICKERS_STATIC_1X
)

# Configuration
START = "2006-07-01"
END = "2025-07-01"
CAPITAL = 10_000

# All tickers needed for all strategies
ALL_TICKERS = ["QQQ", "QLD", "BIL", "SCHD", "GLD"]

def main():
    """Run the three strategy comparison."""
    
    # Download data using shared utilities
    prices = download_price_data(ALL_TICKERS, START, END)
    dividends = download_dividend_data(ALL_TICKERS)
    
    # Run all backtests using shared strategy implementations
    print("\nRunning all strategy backtests...")
    
    # Strategy 1: Static 1.0x (QQQ:QLD:BIL = 4:3:3, quarterly rebalance)
    val_static, _ = backtest_static_leverage_strategy(
        prices, dividends, TICKERS_STATIC_1X, (4.0, 3.0, 3.0), CAPITAL, "quarterly"
    )
    
    # Strategy 2: Eric's Strategy with Gold (annual rebalancing)
    val_eric, _ = backtest_eric_strategy(prices, dividends, ERIC_STRATEGY_GOLD, CAPITAL)
    
    # Strategy 3: QQQ Buy & Hold
    val_qqq, _ = backtest_buy_and_hold(prices, dividends, "QQQ", CAPITAL)
    
    # Calculate risk-free rate for Sharpe ratio
    rf_daily = prices["BIL"].pct_change()
    
    # Calculate performance statistics using shared utilities
    print("\n" + "="*60)
    print("THREE STRATEGY COMPARISON")
    print("="*60)
    
    res_static = calculate_performance_stats(val_static, rf_daily, "Static 1x (QQQ + QLD + BIL)")
    res_eric = calculate_performance_stats(val_eric, rf_daily, "Eric's Strategy (BIL/QQQ/SCHD/QLD/GLD)")
    res_qqq = calculate_performance_stats(val_qqq, rf_daily, "QQQ Buy & Hold")
    
    # Prepare results for visualization
    strategy_results = {
        "Static 1x": (val_static, res_static),
        "Eric's Strategy (w/ Gold)": (val_eric, res_eric),
        "QQQ Buy & Hold": (val_qqq, res_qqq)
    }
    
    # Create comprehensive comparison plot using shared utilities
    create_comparison_plot(strategy_results, "Three Strategy Comparison")
    
    # Print performance summary using shared utilities
    print_performance_summary(strategy_results)
    
    # Eric's strategy allocation summary
    print(f"\n--- Eric's Strategy V2 Allocation ---")
    for ticker, weight in ERIC_STRATEGY_GOLD.items():
        print(f"  {ticker}: {weight*100:.0f}%")
    
    print(f"\nThree strategy comparison completed successfully!")
    print(f"Note: Eric's strategy uses Gold (GLD) instead of Bitcoin")

if __name__ == "__main__":
    main()
