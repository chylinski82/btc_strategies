import requests
import json
import time
from datetime import datetime

# Define the parameters
params = {
    'currency_pair': 'btcusd',
    'step': 300,  # 15 minutes in seconds #'step': 86400,  # 1 day in seconds
    'start': int(datetime(2020, 1, 1).timestamp()),  # the start time
    'limit': 1000  # maximum number of records to fetch per API call
}

# Define the URL for the Bitstamp API endpoint
url = "https://www.bitstamp.net/api/v2/ohlc/btcusd/"

# Define a variable to hold the data
data = []

while True:
    try:
        # Send the HTTP request and get the response
        response = requests.get(url, params=params)

        # Make sure the response status code is 200 (HTTP OK)
        if response.status_code == 200:
            # Convert the response to JSON
            response_json = response.json()

            # Append the response data to the overall data list
            data += response_json['data']['ohlc']

            # Print the time of the most recent data fetched
            latest_data_time = datetime.fromtimestamp(int(response_json['data']['ohlc'][-1]['timestamp']))
            print(f"Progress: loaded data until {latest_data_time}")

            # If the length of the response data is less than the limit, break the loop (we've fetched all the data)
            if len(response_json['data']['ohlc']) < params['limit']:
                break

            # Otherwise, set the new start time as the end time of the last record in the response data
            else:
                params['start'] = int(response_json['data']['ohlc'][-1]['timestamp']) + params['step']
        else:
            print(f"Error: {response.status_code}")
            break
    except Exception as e:
        print(f"Error: {e}")
        break

    # Sleep for 1 second to avoid hitting the API rate limit
    time.sleep(1)

# Save the data to a text file
with open('btc_usd_5m_bs_20-23.txt', 'w') as file:
    for line in data:
        file.write(json.dumps(line) + '\n')
