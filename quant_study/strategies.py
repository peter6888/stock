"""
Common strategy implementations for backtesting.
Contains standardized implementations of various investment strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from backtest_utils import (
    reinvest_dividends, 
    get_quarterly_rebalance_dates, 
    get_annual_rebalance_dates,
    rebalance_portfolio
)


def backtest_9sig_strategy(prices: pd.DataFrame, 
                          dividends: Dict[str, pd.Series], 
                          start_capital: float = 10000,
                          tqqq_weight: float = 0.60, 
                          quarterly_growth: float = 1.09) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Backtest the 9Sig strategy (TQQQ + BIL with quarterly 9% growth target).
    
    Args:
        prices: DataFrame with TQQQ and BIL prices
        dividends: Dictionary of dividend series
        start_capital: Initial capital
        tqqq_weight: Target weight for TQQQ (default 60%)
        quarterly_growth: Quarterly growth target (default 9%)
    
    Returns:
        Tuple of (portfolio_values, full_dataframe)
    """
    df = prices[["TQQQ", "BIL"]].copy()
    df["TQQQ_units"] = start_capital * tqqq_weight / df.iloc[0]["TQQQ"]
    df["BIL_units"] = start_capital * (1 - tqqq_weight) / df.iloc[0]["BIL"]
    df["Target"] = np.nan

    # Reinvest dividends
    reinvest_dividends("TQQQ_units", "TQQQ", dividends["TQQQ"], df)
    reinvest_dividends("BIL_units", "BIL", dividends["BIL"], df)

    # Initial total
    df["Total"] = df["TQQQ"] * df["TQQQ_units"] + df["BIL"] * df["BIL_units"]

    # Get quarterly rebalance dates
    q_dates = get_quarterly_rebalance_dates(df)
    
    # Set quarterly targets
    for i, d in enumerate(q_dates):
        df.loc[d, "Target"] = start_capital if i == 0 else df.loc[q_dates[i-1], "Target"] * quarterly_growth

    # Quarterly rebalance toward target * tqqq_weight
    for i in range(1, len(q_dates)):
        d = q_dates[i]
        tpx, bpx = df.loc[d, ["TQQQ", "BIL"]]
        target = df.loc[q_dates[i-1], "Target"] * quarterly_growth
        desired_tqqq_val = target * tqqq_weight
        curr_tqqq_val = df.loc[d, "TQQQ_units"] * tpx
        delta = desired_tqqq_val - curr_tqqq_val
        df.loc[d:, "TQQQ_units"] += delta / tpx
        df.loc[d:, "BIL_units"] -= delta / bpx

    df["Total"] = df["TQQQ"] * df["TQQQ_units"] + df["BIL"] * df["BIL_units"]
    return df["Total"].dropna(), df


def backtest_static_leverage_strategy(prices: pd.DataFrame, 
                                    dividends: Dict[str, pd.Series],
                                    tickers: List[str],
                                    weights: Tuple[float, ...],
                                    start_capital: float = 10000,
                                    rebalance_frequency: str = "quarterly") -> Tuple[pd.Series, pd.DataFrame]:
    """
    Backtest a static leverage strategy with periodic rebalancing.
    
    Args:
        prices: DataFrame with price data
        dividends: Dictionary of dividend series
        tickers: List of tickers to use
        weights: Tuple of target weights
        start_capital: Initial capital
        rebalance_frequency: "quarterly" or "annual"
    
    Returns:
        Tuple of (portfolio_values, full_dataframe)
    """
    df = prices[tickers].copy()
    weights_array = np.array(weights, dtype=float)
    weights_array = weights_array / weights_array.sum()  # normalize

    # Initialize units by target weights
    for i, ticker in enumerate(tickers):
        df[f"{ticker}_units"] = start_capital * weights_array[i] / df.iloc[0][ticker]

    # Reinvest dividends
    for ticker in tickers:
        reinvest_dividends(f"{ticker}_units", ticker, dividends[ticker], df)

    df["Total"] = sum(df[ticker] * df[f"{ticker}_units"] for ticker in tickers)

    # Get rebalance dates
    if rebalance_frequency == "quarterly":
        rebalance_dates = get_quarterly_rebalance_dates(df)
    else:  # annual
        rebalance_dates = get_annual_rebalance_dates(df)
    
    # Rebalance to target weights
    for i in range(1, len(rebalance_dates)):
        d = rebalance_dates[i]
        rebalance_portfolio(df, d, tickers, weights_array)

    df["Total"] = sum(df[ticker] * df[f"{ticker}_units"] for ticker in tickers)
    return df["Total"].dropna(), df


def backtest_eric_strategy(prices: pd.DataFrame, 
                          dividends: Dict[str, pd.Series],
                          weights: Dict[str, float],
                          start_capital: float = 10000) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Backtest Eric's diversified strategy with annual rebalancing.
    
    Args:
        prices: DataFrame with price data
        dividends: Dictionary of dividend series
        weights: Dictionary mapping tickers to target weights
        start_capital: Initial capital
    
    Returns:
        Tuple of (portfolio_values, full_dataframe)
    """
    tickers = list(weights.keys())
    df = prices[tickers].copy()
    
    # Initialize units based on target weights
    for ticker in tickers:
        weight = weights[ticker]
        df[f"{ticker}_units"] = start_capital * weight / df.iloc[0][ticker]
    
    # Reinvest dividends
    for ticker in tickers:
        reinvest_dividends(f"{ticker}_units", ticker, dividends[ticker], df)
    
    # Calculate total value
    def calc_total(row):
        return sum(row[ticker] * row[f"{ticker}_units"] for ticker in tickers)
    
    df["Total"] = df.apply(calc_total, axis=1)
    
    # Annual rebalancing
    rebalance_dates = get_annual_rebalance_dates(df)
    
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


def backtest_buy_and_hold(prices: pd.DataFrame, 
                         dividends: Dict[str, pd.Series],
                         ticker: str = "QQQ",
                         start_capital: float = 10000) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Backtest a simple buy and hold strategy with dividend reinvestment.
    
    Args:
        prices: DataFrame with price data
        dividends: Dictionary of dividend series
        ticker: Ticker to buy and hold
        start_capital: Initial capital
    
    Returns:
        Tuple of (portfolio_values, full_dataframe)
    """
    df = prices[[ticker]].copy()
    df[f"{ticker}_units"] = start_capital / df.iloc[0][ticker]
    
    # Reinvest dividends
    reinvest_dividends(f"{ticker}_units", ticker, dividends[ticker], df)
    
    df["Total"] = df[ticker] * df[f"{ticker}_units"]
    return df["Total"].dropna(), df


# Strategy configuration constants
ERIC_STRATEGY_BTC = {
    'BIL': 0.20,     # 20% T-Bills
    'QQQ': 0.30,     # 30% QQQ
    'SCHD': 0.40,    # 40% SCHD
    'QLD': 0.10,     # 10% QLD
    'BTC-USD': 0.10  # 10% Bitcoin
}

ERIC_STRATEGY_GOLD = {
    'BIL': 0.20,     # 20% T-Bills
    'QQQ': 0.30,     # 30% QQQ
    'SCHD': 0.40,    # 40% SCHD
    'QLD': 0.10,     # 10% QLD
    'GLD': 0.10      # 10% Gold
}

# Common ticker lists
TICKERS_9SIG = ["TQQQ", "BIL"]
TICKERS_STATIC_14X = ["QQQ", "QLD", "BIL"]
TICKERS_STATIC_1X = ["QQQ", "QLD", "BIL"]
TICKERS_ERIC_BTC = ["BIL", "QQQ", "SCHD", "QLD", "BTC-USD"]
TICKERS_ERIC_GOLD = ["BIL", "QQQ", "SCHD", "QLD", "GLD"]
