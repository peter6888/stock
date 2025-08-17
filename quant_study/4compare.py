"""
Four Strategy Comparison: 9Sig, Static 1.4x, Eric's Strategy, and QQQ Buy & Hold
Comprehensive backtest comparison with performance metrics and visualization.
"""

from backtest_utils import (
    download_price_data, 
    download_dividend_data, 
    calculate_performance_stats,
    create_comparison_plot,
    print_performance_summary
)
from strategies import (
    backtest_9sig_strategy,
    backtest_static_leverage_strategy, 
    backtest_eric_strategy,
    backtest_buy_and_hold,
    ERIC_STRATEGY_BTC,
    TICKERS_STATIC_14X
)

# Configuration
START = "2015-07-01"
END = "2025-07-01"
CAPITAL = 10_000

# All tickers needed for all strategies
ALL_TICKERS = ["QQQ", "QLD", "TQQQ", "BIL", "SCHD", "BTC-USD"]

def main():
    """Run the four strategy comparison."""
    
    # Download data
    prices = download_price_data(ALL_TICKERS, START, END)
    dividends = download_dividend_data(ALL_TICKERS)
    
    # Run all backtests
    print("\nRunning all strategy backtests...")
    
    # Strategy 1: 9Sig
    val_9sig, _ = backtest_9sig_strategy(prices, dividends, CAPITAL)
    
    # Strategy 2: Static 1.4x (QQQ:QLD:BIL = 4:9.67:3)
    val_14x, _ = backtest_static_leverage_strategy(
        prices, dividends, TICKERS_STATIC_14X, (4.0, 9.67, 3.0), CAPITAL, "quarterly"
    )
    
    # Strategy 3: Eric's Strategy
    val_eric, _ = backtest_eric_strategy(prices, dividends, ERIC_STRATEGY_BTC, CAPITAL)
    
    # Strategy 4: QQQ Buy & Hold
    val_qqq, _ = backtest_buy_and_hold(prices, dividends, "QQQ", CAPITAL)
    
    # Calculate risk-free rate for Sharpe ratio
    rf_daily = prices["BIL"].pct_change()
    
    # Calculate performance statistics
    print("\n" + "="*60)
    print("COMPREHENSIVE STRATEGY COMPARISON")
    print("="*60)
    
    res_9sig = calculate_performance_stats(val_9sig, rf_daily, "9Sig (TQQQ + BIL)")
    res_14x = calculate_performance_stats(val_14x, rf_daily, "Static 1.4x (QQQ + QLD + BIL)")
    res_eric = calculate_performance_stats(val_eric, rf_daily, "Eric's Strategy (BIL/QQQ/SCHD/QLD/BTC)")
    res_qqq = calculate_performance_stats(val_qqq, rf_daily, "QQQ Buy & Hold")
    
    # Prepare results for visualization
    strategy_results = {
        "9Sig": (val_9sig, res_9sig),
        "Static 1.4x": (val_14x, res_14x),
        "Eric's Strategy": (val_eric, res_eric),
        "QQQ Buy & Hold": (val_qqq, res_qqq)
    }
    
    # Create comprehensive comparison plot
    create_comparison_plot(strategy_results, "Four Strategy Comparison")
    
    # Print performance summary
    print_performance_summary(strategy_results)
    
    # Eric's strategy allocation summary
    print(f"\n--- Eric's Strategy Allocation ---")
    for ticker, weight in ERIC_STRATEGY_BTC.items():
        print(f"  {ticker}: {weight*100:.0f}%")
    
    print(f"\nBacktest completed successfully!")

if __name__ == "__main__":
    main()
