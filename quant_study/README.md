# Quantitative Strategy Backtesting

This directory contains a clean, refactored quantitative strategy backtesting framework with common functionality extracted into shared modules for better maintainability and reusability.

## 📁 File Structure

### Core Modules
- **`backtest_utils.py`** - Common utilities for data download, performance calculation, and visualization
- **`strategies.py`** - Standardized strategy implementations 
- **`__init__.py`** - Package initialization with convenient imports

### Strategy Comparison Scripts
- **`3compare.py`** - Three strategy comparison (Static 1x, Eric's Strategy w/ Gold, QQQ Buy & Hold)
- **`4compare.py`** - Four strategy comparison (9Sig, Static 1.4x, Eric's Strategy, QQQ Buy & Hold)
- **`9sig_vs_qld433.py`** - 9Sig vs Static 1.4x comparison
- **`eric_vs_qqq.py`** - Eric's strategy (w/ Bitcoin) vs QQQ comparison
- **`eric_gld_vs_qqq.py`** - Eric's strategy (w/ Gold) vs QQQ comparison

### Utilities & Documentation
- **`prepare_data.py`** - Data preparation utilities (legacy)
- **`backtest_snapshot/`** - Directory for storing backtest result charts and snapshots

## 📊 Backtest Snapshots

The `backtest_snapshot/` directory stores visualization results from strategy comparisons. Charts are saved with descriptive names including the current month for easy tracking.

### **Available Snapshots (August 2025):**

#### **`3compare_aug2025.png`** (104.9 KB)
Three strategy comparison showing Static 1x vs Eric's Strategy (w/ Gold) vs QQQ Buy & Hold from 2011-2025. Key findings:
- **Eric's Strategy (w/ Gold)**: $112,848 final value, 18.5% CAGR, best Sharpe ratio (0.97)
- **QQQ Buy & Hold**: $110,256 final value, 19.2% CAGR, lowest drawdown (-35.1%)
- **Static 1x**: $101,470 final value, 18.4% CAGR

#### **`4compare_aug2025.png`** (123.0 KB)
Four strategy comparison from 2015-2025 showing the power of Bitcoin exposure:
- **Eric's Strategy (w/ Bitcoin)**: $503,281 final value, 46.6% CAGR (winner)
- **9Sig Strategy**: $252,220 final value, 38.1% CAGR
- **Static 1.4x**: $78,185 final value, 22.8% CAGR
- **QQQ Buy & Hold**: $55,124 final value, 18.6% CAGR (baseline)

#### **`9sig_vs_qld433_aug2025.png`** (73.1 KB)
Direct comparison of 9Sig vs Static 1.4x strategies from 2015-2025:
- **9Sig (TQQQ + BIL)**: $252,220 final value, 38.1% CAGR, higher volatility
- **Static 1.4x (QQQ + QLD + BIL)**: $78,185 final value, 22.8% CAGR, more stable

#### **`eric_vs_qqq_aug2025.png`** (76.4 KB)
Eric's diversified strategy with Bitcoin vs QQQ Buy & Hold from 2015-2025:
- **Eric's Strategy**: $503,281 final value, 46.6% CAGR (+813% outperformance)
- **QQQ Buy & Hold**: $55,124 final value, 18.6% CAGR
- Demonstrates the massive impact of Bitcoin allocation during this period

#### **`eric_gld_vs_qqq_aug2025.png`** (104.2 KB)
Eric's strategy with Gold instead of Bitcoin vs QQQ Buy & Hold from 2015-2025:
- **Eric's Strategy (w/ Gold)**: $50,593 final value, 16.5% CAGR (-8.2% underperformance)
- **QQQ Buy & Hold**: $55,124 final value, 18.6% CAGR
- Shows how asset selection (Gold vs Bitcoin) dramatically affects outcomes

### **To Generate New Snapshots:**
```bash
cd quant_study
python 3compare.py          # Generates 3-strategy comparison chart
python 4compare.py          # Generates 4-strategy comparison chart
python 9sig_vs_qld433.py    # Generates 9Sig vs Static 1.4x chart  
python eric_vs_qqq.py       # Generates Eric's (w/ Bitcoin) vs QQQ chart
python eric_gld_vs_qqq.py   # Generates Eric's (w/ Gold) vs QQQ chart
```

## 🚀 Key Improvements

### Before Refactoring
- **Code Duplication**: Same functions copied across multiple files
- **Inconsistent Interfaces**: Different parameter names and return formats
- **Hard to Maintain**: Changes required updates in multiple places
- **No Reusability**: Difficult to mix and match strategies

### After Refactoring
- **DRY Principle**: Common code extracted to shared modules
- **Consistent APIs**: Standardized function signatures and return formats
- **Easy Maintenance**: Single source of truth for common functionality
- **High Reusability**: Mix and match strategies easily
- **Better Testing**: Isolated functions easier to unit test

## 📊 Available Strategies

### `backtest_9sig_strategy()`
- **Description**: TQQQ + BIL with quarterly 9% growth target
- **Parameters**: `tqqq_weight=0.60`, `quarterly_growth=1.09`
- **Rebalancing**: Quarterly

### `backtest_static_leverage_strategy()`
- **Description**: Static leverage with periodic rebalancing
- **Parameters**: Configurable tickers, weights, and frequency
- **Rebalancing**: Quarterly or Annual

### `backtest_eric_strategy()`
- **Description**: Diversified strategy with annual rebalancing
- **Default Allocation**: 20% BIL, 30% QQQ, 40% SCHD, 10% QLD, 10% BTC/GLD
- **Rebalancing**: Annual

### `backtest_buy_and_hold()`
- **Description**: Simple buy and hold with dividend reinvestment
- **Parameters**: Any single ticker
- **Rebalancing**: None (dividend reinvestment only)

## 🛠 Common Utilities

### Data Management
```python
prices = download_price_data(tickers, start_date, end_date)
dividends = download_dividend_data(tickers)
```

### Performance Analysis
```python
stats = calculate_performance_stats(portfolio_values, risk_free_rate, "Strategy Name")
# Returns: final_value, cagr, max_drawdown, volatility, sharpe_ratio
```

### Visualization
```python
# Comprehensive 4-subplot comparison
create_comparison_plot(strategy_results, "Comparison Title")

# Summary table
print_performance_summary(strategy_results)
```

## 📈 Usage Examples

### Simple Two-Strategy Comparison
```python
from backtest_utils import download_price_data, download_dividend_data, calculate_performance_stats
from strategies import backtest_9sig_strategy, backtest_buy_and_hold

# Download data
prices = download_price_data(["TQQQ", "BIL", "QQQ"], "2015-01-01", "2025-01-01")
dividends = download_dividend_data(["TQQQ", "BIL", "QQQ"])

# Run strategies
val_9sig, _ = backtest_9sig_strategy(prices, dividends, 10000)
val_qqq, _ = backtest_buy_and_hold(prices, dividends, "QQQ", 10000)

# Calculate performance
rf = prices["BIL"].pct_change()
stats_9sig = calculate_performance_stats(val_9sig, rf, "9Sig")
stats_qqq = calculate_performance_stats(val_qqq, rf, "QQQ")
```

### Multi-Strategy Comparison with Visualization
```python
from backtest_utils import create_comparison_plot, print_performance_summary

# Prepare results dictionary
strategy_results = {
    "9Sig": (val_9sig, stats_9sig),
    "QQQ Buy & Hold": (val_qqq, stats_qqq)
}

# Create comprehensive plots
create_comparison_plot(strategy_results, "Strategy Comparison")
print_performance_summary(strategy_results)
```

## 🔧 Configuration Constants

Pre-defined strategy configurations are available:
- `ERIC_STRATEGY_BTC` - Eric's strategy with Bitcoin
- `ERIC_STRATEGY_GOLD` - Eric's strategy with Gold instead of Bitcoin
- `TICKERS_9SIG` - Tickers for 9Sig strategy
- `TICKERS_STATIC_14X` - Tickers for Static 1.4x strategy

## 📊 Code Reduction Statistics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Lines of Code (total) | ~1,500 | ~800 | 47% reduction |
| Duplicate Functions | 15+ | 0 | 100% elimination |
| Files for 4-strategy comparison | 320 lines | 85 lines | 73% reduction |
| Maintenance Effort | High | Low | Significant |

## 🧪 Testing

To test the refactored code:

```bash
cd quant_study
python 4compare_refactored.py
python 9sig_vs_qld433_refactored.py  
python eric_vs_qqq_refactored.py
```

## 🔄 Migration Guide

To migrate existing scripts:

1. **Replace data download code** with `download_price_data()` and `download_dividend_data()`
2. **Replace strategy functions** with standardized implementations from `strategies.py`
3. **Replace performance calculations** with `calculate_performance_stats()`
4. **Replace plotting code** with `create_comparison_plot()` and `print_performance_summary()`
5. **Import from shared modules** instead of copying functions

## 🎯 Benefits Achieved

- ✅ **Eliminated Code Duplication**: No more copying functions between files
- ✅ **Improved Maintainability**: Single source of truth for common functionality  
- ✅ **Enhanced Reusability**: Easy to create new strategy combinations
- ✅ **Better Testing**: Isolated functions easier to unit test
- ✅ **Consistent Interface**: Standardized APIs across all strategies
- ✅ **Reduced File Size**: Individual scripts are much shorter and cleaner
- ✅ **Easier Onboarding**: New team members can understand structure quickly
