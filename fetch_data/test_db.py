import requests
import time
import json
from datetime import datetime, timedelta

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

def save_candlestick_data(trades, file_path):
    # Create a list to hold the current interval's trades
    current_interval_trades = []
    # Set the end of the current interval to the time of the first trade plus 3 minutes
    current_interval_end = datetime.fromtimestamp(trades[0]['timestamp'] / 1000) + timedelta(minutes=3)

    with open(file_path, 'a') as f:
        for trade in trades:
            trade_time = datetime.fromtimestamp(trade['timestamp'] / 1000)

            # If this trade is still in the current 3-minute interval
            if trade_time < current_interval_end:
                # Add it to the current interval's trades
                current_interval_trades.append(trade)
            else:
                # This trade is in the next 3-minute interval,
                # so calculate and save the previous interval's data
                if current_interval_trades:
                    open_price = current_interval_trades[0]['price']
                    close_price = current_interval_trades[-1]['price']
                    high_price = max(t['price'] for t in current_interval_trades)
                    low_price = min(t['price'] for t in current_interval_trades)
                    volume = sum(t['amount'] for t in current_interval_trades)
                    timestamp = date_to_timestamp(current_interval_end - timedelta(minutes=3))

                    f.write(json.dumps({
                        'timestamp': timestamp * 1000,  # convert to milliseconds
                        'open': open_price,
                        'close': close_price,
                        'high': high_price,
                        'low': low_price,
                        'volume': volume
                    }) + '\n')

                # Start the next interval
                current_interval_trades = [trade]
                current_interval_end += timedelta(minutes=3)

        # Save the last interval's data
        if current_interval_trades:
            open_price = current_interval_trades[0]['price']
            close_price = current_interval_trades[-1]['price']
            high_price = max(t['price'] for t in current_interval_trades)
            low_price = min(t['price'] for t in current_interval_trades)
            volume = sum(t['amount'] for t in current_interval_trades)
            timestamp = date_to_timestamp(current_interval_end - timedelta(minutes=3))

            f.write(json.dumps({
                'timestamp': timestamp * 1000,  # convert to milliseconds
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
        save_candlestick_data(trades, 'hist_data/deribit/btc-p_3m_db_recent.txt')

        # Print progress
        print(f'Data loaded until: {datetime.fromtimestamp(current_timestamp)}')

        # Move to the next day
        current_timestamp += 86400

        # Wait a bit before making the next request to avoid hitting rate limits
        time.sleep(1)

if __name__ == '__main__':
    main()
