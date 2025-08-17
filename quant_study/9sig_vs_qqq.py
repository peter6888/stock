# prompt: can you also load QQQ price and it's dividend. and compare the growth? also in chart?  please update above code to compare this existing stradedy

import pandas as pd
import matplotlib.pyplot as plt
# Download QQQ data
qqq_data = yf.download("QQQ", start="2015-07-01", end="2025-07-01")

# Check for download success
if qqq_data.empty:
    raise ValueError("Failed to download QQQ data.")

# Build DataFrame for QQQ
qqq_df = pd.DataFrame()
qqq_df['QQQ'] = qqq_data['Close']
qqq_df.dropna(inplace=True)

# Download QQQ dividend data
qqq_div = yf.Ticker("QQQ").dividends

# Initialize QQQ investment (match the starting date of the strategy)
# Find the starting date that is common to both the strategy df and QQQ df
common_start_date = max(df.index[0], qqq_df.index[0])
common_end_date = min(df.index[-1], qqq_df.index[-1])

# Filter both dataframes to the common date range
strategy_df_filtered = df.loc[common_start_date:common_end_date].copy()
qqq_df_filtered = qqq_df.loc[common_start_date:common_end_date].copy()

initial_investment_qqq = strategy_df_filtered['Total'].iloc[0] # Use the strategy's initial value for comparison
qqq_df_filtered['QQQ_units'] = initial_investment_qqq / qqq_df_filtered.iloc[0]['QQQ']

# Reinvest QQQ dividends
for date, amount in qqq_div.items():
    if date in qqq_df_filtered.index:
        # Ensure we have price data for the dividend date
        if date in qqq_df_filtered.index:
            added_units = amount * qqq_df_filtered.loc[date, 'QQQ_units'] / qqq_df_filtered.loc[date, 'QQQ']
            qqq_df_filtered.loc[date:, 'QQQ_units'] += added_units

# Calculate total QQQ value over time
qqq_df_filtered['Total_QQQ'] = qqq_df_filtered['QQQ'] * qqq_df_filtered['QQQ_units']

# --- Plotting ---
plt.figure(figsize=(12, 6))
plt.plot(strategy_df_filtered.index, strategy_df_filtered['Total'], label='9Sig Strategy (TQQQ + BIL)')
plt.plot(qqq_df_filtered.index, qqq_df_filtered['Total_QQQ'], label='QQQ (Buy and Hold with Dividends)')
plt.title('Strategy vs. QQQ Growth Comparison with Dividends')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# --- Print comparison results ---
strategy_final_value = strategy_df_filtered['Total'].iloc[-1]
qqq_final_value = qqq_df_filtered['Total_QQQ'].iloc[-1]

print("\n--- Comparison Results ---")
print(f"9Sig Strategy Final Value ({strategy_df_filtered.index[-1].date()}): ${strategy_final_value:,.2f}")
print(f"QQQ Buy and Hold Final Value ({qqq_df_filtered.index[-1].date()}): ${qqq_final_value:,.2f}")

# Calculate APR for both
strategy_start_value = strategy_df_filtered['Total'].iloc[0]
qqq_start_value = qqq_df_filtered['Total_QQQ'].iloc[0]

n_years_strategy = (strategy_df_filtered.index[-1] - strategy_df_filtered.index[0]).days / 365.25
n_years_qqq = (qqq_df_filtered.index[-1] - qqq_df_filtered.index[0]).days / 365.25

strategy_apr = (strategy_final_value / strategy_start_value) ** (1 / n_years_strategy) - 1
qqq_apr = (qqq_final_value / qqq_start_value) ** (1 / n_years_qqq) - 1

print(f"9Sig Strategy APR: {strategy_apr * 100:.2f}%")
print(f"QQQ Buy and Hold APR: {qqq_apr * 100:.2f}%")
