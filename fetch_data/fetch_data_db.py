import requests
import time
import json
from datetime import datetime

# Helper function to convert date to timestamp (in seconds)
def date_to_timestamp(date):
    return int(time.mktime(date.timetuple()))

# Start and end times
start_date = datetime(2023, 6, 19)
start_timestamp = date_to_timestamp(start_date)
end_timestamp = int(time.time())  # Current time

def get_trades(start_timestamp, end_timestamp):
    url = 'https://history.deribit.com/api/v2/public/get_last_trades_by_instrument_and_time'
    params = {
        'instrument_name': 'BTC-PERPETUAL',
        'start_timestamp': start_timestamp * 1000,  # API needs timestamp in milliseconds
        'end_timestamp': end_timestamp * 1000,
        'count': 10000,  # Maximum count
        'include_old': True
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data['result']['trades']

def save_candlestick_data(trades, file_path, interval):
    with open(file_path, 'a') as f:
        for i in range(0, len(trades), interval): 
            candlestick_trades = trades[i:i+interval]

            if candlestick_trades:
                # Calculate the open, close, high, low prices and volume
                open_price = candlestick_trades[0]['price']
                close_price = candlestick_trades[-1]['price']
                high_price = max(trade['price'] for trade in candlestick_trades)
                low_price = min(trade['price'] for trade in candlestick_trades)
                volume = sum(trade['amount'] for trade in candlestick_trades)
                timestamp = candlestick_trades[0]['timestamp']  # Use the timestamp of the first trade

                # Write the candlestick data to file
                f.write(json.dumps({
                    'timestamp': timestamp,
                    'open': open_price,
                    'close': close_price,
                    'high': high_price,
                    'low': low_price,
                    'volume': volume
                }) + '\n')

def main():
    current_timestamp = start_timestamp
    while current_timestamp < end_timestamp:
        # Get the trades
        trades = get_trades(current_timestamp, current_timestamp + 86400)  # Retrieve data for 1 day at a time

        # Save the candlestick data
        save_candlestick_data(trades, 'hist_data/deribit/btc-p_3m_db_recent.txt', 180)  # Change 180 to 300 for 5-minute candlesticks

        # Print progress
        print(f'Data loaded until: {datetime.fromtimestamp(current_timestamp)}')

        # Move to the next day
        current_timestamp += 86400

        # Wait a bit before making the next request to avoid hitting rate limits
        time.sleep(1)

if __name__ == '__main__':
    main()
