import pandas as pd
import pandas_ta as ta
import ast

def read_data_from_txt(file):
    data = []
    with open(file, 'r') as f:
        for line in f:
            data.append(ast.literal_eval(line))
    df = pd.DataFrame(data)
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'time_close', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
    return df

def calculate_signals(df, rr_ratio=2.0, rsi_len=14, vol_ma_len=20):
    df['sma'] = ta.sma(df['close'], length=50)
    df['rsi'] = ta.rsi(df['close'], length=rsi_len)
    df['vol_ma'] = ta.sma(df['volume'], length=vol_ma_len)
    df['smaDailyLong'] = df['close'] > df['sma'] * 1.01
    df['smaDailyShort'] = df['close'] < df['sma'] * 0.99
    df['stop_loss_long'] = df['low'].rolling(rsi_len).min()
    df['stop_loss_short'] = df['high'].rolling(rsi_len).max()
    df['limit_long'] = df['close'] + (df['close'] - df['stop_loss_long']) * rr_ratio
    df['limit_short'] = df['close'] - (df['stop_loss_short'] - df['close']) * rr_ratio
    return df

def write_data_to_txt(df, file):
    with open(file, 'w') as f:
        f.write(df.to_string())

df = calculate_signals(read_data_from_txt('btc_usdt_1d.txt'))
write_data_to_txt(df, 'output.txt')
