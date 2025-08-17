"""
Shared utilities for backtesting strategies in the quant_study module.
Contains common functions for data download, dividend reinvestment, 
performance calculations, and visualization.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Union


def download_price_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """
    Download price data for multiple tickers from yfinance.
    
    Args:
        tickers: List of ticker symbols
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
    
    Returns:
        DataFrame with close prices for each ticker
    """
    print(f"Downloading price data for {len(tickers)} tickers...")
    data = yf.download(tickers, start=start, end=end, group_by='ticker')
    if data.empty:
        raise ValueError("Failed to download data")
    
    # Extract close prices for each ticker
    prices_dict = {}
    for ticker in tickers:
        if len(tickers) == 1:
            prices_dict[ticker] = data['Close']
        else:
            prices_dict[ticker] = data[ticker]['Close']
    
    return pd.DataFrame(prices_dict).dropna()


def download_dividend_data(tickers: List[str]) -> Dict[str, pd.Series]:
    """
    Download dividend data for multiple tickers.
    
    Args:
        tickers: List of ticker symbols
    
    Returns:
        Dictionary mapping ticker to dividend Series
    """
    print("Downloading dividend data...")
    divs = {}
    for ticker in tickers:
        try:
            div_data = yf.Ticker(ticker).dividends
            divs[ticker] = div_data if div_data is not None and len(div_data) > 0 else pd.Series(dtype=float)
        except:
            divs[ticker] = pd.Series(dtype=float)
    return divs


def reinvest_dividends(units_col: str, price_col: str, div_series: pd.Series, df: pd.DataFrame) -> None:
    """
    Reinvest dividends by adding units to the portfolio.
    
    Args:
        units_col: Column name for units held
        price_col: Column name for asset price
        div_series: Series of dividend payments
        df: DataFrame to modify in-place
    """
    for dt, amt in div_series.items():
        if dt in df.index:
            add_units = (amt * df.loc[dt, units_col]) / df.loc[dt, price_col]
            df.loc[dt:, units_col] += add_units


def get_quarterly_rebalance_dates(df: pd.DataFrame) -> List[pd.Timestamp]:
    """
    Get quarterly rebalance dates aligned to actual trading days.
    
    Args:
        df: DataFrame with price data (DatetimeIndex)
    
    Returns:
        List of quarterly rebalance dates
    """
    q_end_dates = df.resample("QE").first().index
    q_dates = []
    for q_end in q_end_dates:
        available_dates = df.index[df.index <= q_end]
        if len(available_dates) > 0:
            q_dates.append(available_dates[-1])
    return q_dates


def get_annual_rebalance_dates(df: pd.DataFrame) -> List[pd.Timestamp]:
    """
    Get annual rebalance dates aligned to actual trading days.
    
    Args:
        df: DataFrame with price data (DatetimeIndex)
    
    Returns:
        List of annual rebalance dates
    """
    annual_dates = df.resample("YE").first().index
    rebalance_dates = []
    for year_end in annual_dates:
        available_dates = df.index[df.index <= year_end]
        if len(available_dates) > 0:
            rebalance_dates.append(available_dates[-1])
    return rebalance_dates


def calculate_performance_stats(portfolio_values: pd.Series, 
                              risk_free_rate: Optional[pd.Series] = None, 
                              name: str = "Strategy") -> Dict[str, float]:
    """
    Calculate comprehensive performance statistics for a strategy.
    
    Args:
        portfolio_values: Time series of portfolio values
        risk_free_rate: Risk-free rate series for Sharpe calculation
        name: Strategy name for display
    
    Returns:
        Dictionary with performance metrics
    """
    v = portfolio_values.dropna()
    r = v.pct_change().dropna()
    
    if risk_free_rate is not None:
        rf = risk_free_rate.reindex(r.index).fillna(0.0)
        excess_returns = r - rf
    else:
        excess_returns = r
    
    years = (v.index[-1] - v.index[0]).days / 365.25
    cagr = (v.iloc[-1] / v.iloc[0])**(1/years) - 1
    
    # Calculate maximum drawdown
    roll_max = v.cummax()
    drawdown = v / roll_max - 1.0
    max_drawdown = drawdown.min()
    
    # Calculate volatility and Sharpe ratio
    volatility = excess_returns.std() * np.sqrt(252)
    sharpe = (excess_returns.mean() / excess_returns.std() * np.sqrt(252)) if excess_returns.std() > 0 else np.nan
    
    print(f"\n{name} results:")
    print(f"  Period: {v.index[0].date()} → {v.index[-1].date()}")
    print(f"  Final value: ${v.iloc[-1]:,.2f}")
    print(f"  CAGR: {cagr*100:.2f}%")
    print(f"  Max drawdown: {max_drawdown*100:.2f}%")
    print(f"  Volatility: {volatility*100:.2f}%")
    print(f"  Sharpe ratio: {sharpe:.2f}")
    
    return {
        "final": v.iloc[-1], 
        "cagr": cagr, 
        "mdd": max_drawdown, 
        "vol": volatility, 
        "sharpe": sharpe
    }


def create_comparison_plot(strategy_results: Dict[str, Tuple[pd.Series, Dict]], 
                         title: str = "Strategy Comparison",
                         figsize: Tuple[int, int] = (16, 10)) -> None:
    """
    Create a comprehensive 4-subplot comparison of multiple strategies.
    
    Args:
        strategy_results: Dict mapping strategy names to (values_series, stats_dict)
        title: Main plot title
        figsize: Figure size tuple
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
    
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    strategy_names = list(strategy_results.keys())
    
    # Main comparison plot
    for i, (name, (values, stats)) in enumerate(strategy_results.items()):
        color = colors[i % len(colors)]
        ax1.plot(values.index, values, label=name, linewidth=2, color=color)
    
    ax1.set_title(f"{title} - Portfolio Value", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Portfolio Value ($)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_yscale('log')  # Log scale to better show all strategies
    
    # CAGR comparison
    cagrs = [stats['cagr']*100 for _, stats in strategy_results.values()]
    bars = ax2.bar(strategy_names, cagrs, color=colors[:len(strategy_names)], alpha=0.7)
    ax2.set_title("CAGR Comparison", fontsize=14, fontweight='bold')
    ax2.set_ylabel("CAGR (%)")
    ax2.grid(True, alpha=0.3)
    for bar, cagr in zip(bars, cagrs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{cagr:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Max Drawdown comparison
    mdds = [stats['mdd']*100 for _, stats in strategy_results.values()]
    bars = ax3.bar(strategy_names, mdds, color=colors[:len(strategy_names)], alpha=0.7)
    ax3.set_title("Max Drawdown Comparison", fontsize=14, fontweight='bold')
    ax3.set_ylabel("Max Drawdown (%)")
    ax3.grid(True, alpha=0.3)
    for bar, mdd in zip(bars, mdds):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 2, 
                f'{mdd:.1f}%', ha='center', va='top', fontweight='bold')
    
    # Sharpe Ratio comparison
    sharpes = [stats['sharpe'] for _, stats in strategy_results.values()]
    bars = ax4.bar(strategy_names, sharpes, color=colors[:len(strategy_names)], alpha=0.7)
    ax4.set_title("Sharpe Ratio Comparison", fontsize=14, fontweight='bold')
    ax4.set_ylabel("Sharpe Ratio")
    ax4.grid(True, alpha=0.3)
    for bar, sharpe in zip(bars, sharpes):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{sharpe:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def print_performance_summary(strategy_results: Dict[str, Tuple[pd.Series, Dict]]) -> None:
    """
    Print a formatted performance summary table.
    
    Args:
        strategy_results: Dict mapping strategy names to (values_series, stats_dict)
    """
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    print(f"{'Strategy':<25} {'Final Value':<15} {'CAGR':<8} {'Max DD':<8} {'Volatility':<12} {'Sharpe':<8}")
    print("-" * 80)
    
    for name, (_, stats) in strategy_results.items():
        print(f"{name:<25} ${stats['final']:>12,.0f} {stats['cagr']*100:>6.1f}% "
              f"{stats['mdd']*100:>6.1f}% {stats['vol']*100:>10.1f}% {stats['sharpe']:>6.2f}")


def rebalance_portfolio(df: pd.DataFrame, rebalance_date: pd.Timestamp, 
                       tickers: List[str], target_weights: np.ndarray) -> None:
    """
    Rebalance portfolio to target weights on a specific date.
    
    Args:
        df: DataFrame with price and units data (must have 'Total' column)
        rebalance_date: Date to perform rebalancing
        tickers: List of ticker symbols
        target_weights: Array of target weights (must sum to 1)
    """
    # Use pre-calculated Total column (matches reference implementation)
    total_value = df.loc[rebalance_date, "Total"]
    target_values = total_value * target_weights
    
    for i, ticker in enumerate(tickers):
        current_value = df.loc[rebalance_date, f"{ticker}_units"] * df.loc[rebalance_date, ticker]
        delta = target_values[i] - current_value
        df.loc[rebalance_date:, f"{ticker}_units"] += delta / df.loc[rebalance_date, ticker]
