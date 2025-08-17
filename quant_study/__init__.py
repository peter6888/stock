"""
Quantitative Strategy Backtesting Package

This package provides utilities and implementations for backtesting various investment strategies.

Modules:
- backtest_utils: Common utilities for data download, performance calculation, and visualization
- strategies: Standardized strategy implementations (9Sig, Eric's strategy, static leverage, etc.)
"""

from backtest_utils import (
    download_price_data,
    download_dividend_data,
    reinvest_dividends,
    calculate_performance_stats,
    create_comparison_plot,
    print_performance_summary,
    get_quarterly_rebalance_dates,
    get_annual_rebalance_dates,
    rebalance_portfolio
)

from strategies import (
    backtest_9sig_strategy,
    backtest_static_leverage_strategy,
    backtest_eric_strategy,
    backtest_buy_and_hold,
    ERIC_STRATEGY_BTC,
    ERIC_STRATEGY_GOLD,
    TICKERS_9SIG,
    TICKERS_STATIC_14X,
    TICKERS_STATIC_1X,
    TICKERS_ERIC_BTC,
    TICKERS_ERIC_GOLD
)

__version__ = "1.0.0"
__author__ = "Quantitative Strategy Team"
