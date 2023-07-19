import pandas as pd
import pandas_ta as ta
import numpy as np
import ast

def read_data_from_txt(file):
    data = []
    with open(file, 'r') as f:
        for line in f:
            record = ast.literal_eval(line.strip())
            data.append(record)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Change timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Drop duplicated rows based on the 'timestamp' column
    df.drop_duplicates(subset='timestamp', inplace=True)

    # Change column names
    df = df.rename(columns={'timestamp': 'time', 'volume': 'volume', 'open': 'open', 'close': 'close', 'high': 'high', 'low': 'low'})

    # Ensure the numeric columns have the correct type
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)

    # Set 'time' as index
    df.set_index('time', inplace=True)

    # Resample to 3-minute intervals
    df = resample_to_3_minutes(df)
    print(df.head())

    return df



def resample_to_3_minutes(df):
    # Determine the time range of the data
    min_time = df.index.min()
    max_time = df.index.max()

    # Create a new index with 3-minute intervals
    new_index = pd.date_range(start=min_time, end=max_time, freq='3T')

    # Remove any duplicate labels in the original index
    df = df[~df.index.duplicated()]

    # Reindex the dataframe
    df = df.reindex(new_index)

    # Forward-fill missing values to propagate the last valid observation
    df = df.ffill()

    # Remove any rows with missing values
    df = df.dropna()

    return df


def calculate_signals(df, length=350, low_level=30, high_level=70, vol_ma_length=50, vol_level_short=0.7, vol_level_long=0.0):
    df['highest_close'] = df['close'].rolling(window=length, min_periods=1).max()
    df['lowest_close'] = df['close'].rolling(window=length, min_periods=1).min()
    df['normalized_close'] = (df['close'] - df['lowest_close']) / (df['highest_close'] - df['lowest_close']) * 100
    df['vol_ma'] = ta.sma(df['volume'], length=vol_ma_length)

    df['crossunder'] = df['normalized_close'].shift() < low_level
    df['crossover'] = df['normalized_close'].shift() > high_level
    df['enter_long'] = (df['normalized_close'].shift(1) > low_level) & df['crossunder'].shift(1) & (df['volume'].shift(1) > vol_level_long * df['vol_ma'].shift(1))
    df['enter_short'] = (df['normalized_close'].shift(1) < high_level) & df['crossover'].shift(1) & (df['volume'].shift(1) < vol_level_short * df['vol_ma'].shift(1))
    
    # Only keep rows starting from 'length' position
    df = df.iloc[length:]

    return df

def backtest(df, stop_loss_pcnt=1.5, rr_ratio=3.0):
    cash = 10000.0  # initial cash
    position = 0.0
    trades = []
    ongoing_trade = False
    stop_level_long = 0.0
    stop_level_short = 0.0
    take_profit_long = 0.0
    take_profit_short = 0.0

    for i, row in df.iterrows():
        trade_cash = 10000.0  # cash dedicated to every trade

        if not ongoing_trade:
            if row['enter_long']:
                position = trade_cash / row['close'] * (1 - 0.0005)  # 0.05% commission
                stop_level_long = row['close'] * (1 - stop_loss_pcnt / 100)
                take_profit_long = row['close'] + rr_ratio * abs(row['close'] - stop_level_long)
                trades.append((i, 'entry long', 'buy', round(row['close'], 2), round(position, 2), round(cash, 2)))
                ongoing_trade = True
            elif row['enter_short']:
                position = -trade_cash / row['close'] * (1 - 0.0005)  # 0.05% commission
                stop_level_short = row['close'] * (1 + stop_loss_pcnt / 100)
                take_profit_short = row['close'] - rr_ratio * abs(row['close'] - stop_level_short)
                trades.append((i, 'entry short', 'sell', round(row['close'], 2), round(-position, 2), round(cash, 2)))
                ongoing_trade = True

        elif ongoing_trade:
            if position > 0 and (row['close'] < stop_level_long or row['close'] >= take_profit_long):
                trade_value = position * row['close'] * (1 - 0.0005)  # 0.05% commission
                profit = trade_value - trade_cash
                cash += profit
                trades.append((i, 'exit long', 'sell', round(row['close'], 2), round(position, 2), round(cash, 2)))
                position = 0.0
                ongoing_trade = False
            elif position < 0 and (row['close'] > stop_level_short or row['close'] <= take_profit_short):
                trade_value = -position * row['close'] * (1 - 0.0005)  # 0.05% commission
                profit = trade_cash - trade_value
                cash += profit
                trades.append((i, 'exit short', 'buy', round(row['close'], 2), round(-position, 2), round(cash, 2)))
                position = 0.0
                ongoing_trade = False

    return trades

def write_trades(trades, filename):
    with open(filename, 'w') as f:
        for i, trade in enumerate(trades, 1):
            timestamp, action, side, price, size, cash = trade
            f.write(f"Trade {i}: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} {action} {side} at {price}, size={size}, cash={cash}\n")

if __name__ == '__main__':
    df = read_data_from_txt('hist_data/deribit/btc-p_3m_db_recent.txt')
    df = calculate_signals(df)

    # Print after calculate_signals has modified df
    #print(df['highest_close'].head(400))
    #print(df['lowest_close'].head(400))

    trades = backtest(df)

    # Write trades to a text file
    write_trades(trades, 'deribit/trades_db_350_n07_recent.txt') 


print(df[['normalized_close', 'enter_long', 'enter_short', 'crossunder', 'crossover', 'vol_ma']].head(2000))

