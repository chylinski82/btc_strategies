import requests
import json
import time
from datetime import datetime

# Define your API Key and Secret Key here. You can get them from Binance's website.
API_KEY = "KeKH9Vfl1u8Mlo4WJwRlDxLGI8PZZE97VTKV8QNUZehyUArNTqGw7Gl7savcADcW"
SECRET_KEY = "bgl44ejIfugCdHoZBqw4AQrEx5yfJ9qWGxuRwNMvJLTum7fKVQ6MAE3NTbN180E8"

# Define headers for the HTTP request
headers = {
    'X-MBX-APIKEY': API_KEY
}

# Define the parameters
params = {
    'symbol': 'BTCUSDT',
    'interval': '1M',  # 1 month
    'startTime': int(datetime(2016, 1, 1).timestamp() * 1000),  # the start time
    'endTime': int(datetime.now().timestamp() * 1000),  # the end time
    'limit': 1000  # maximum number of records to fetch per API call
}

# Define the URL for the Binance API endpoint
url = "https://api.binance.com/api/v3/klines"

# Define a variable to hold the data
data = []

while True:
    try:
        # Send the HTTP request and get the response
        response = requests.get(url, headers=headers, params=params)

        # Make sure the response status code is 200 (HTTP OK)
        if response.status_code == 200:
            # Convert the response to JSON
            response_json = response.json()

            # Append the response data to the overall data list
            data += response_json

            # Print the time of the most recent data fetched
            latest_data_time = datetime.fromtimestamp(response_json[-1][6] / 1000)
            print(f"Progress: loaded data until {latest_data_time}")

            # If the length of the response data is less than the limit, break the loop (we've fetched all the data)
            if len(response_json) < params['limit']:
                break

            # Otherwise, set the new start time as the end time of the last record in the response data
            else:
                params['startTime'] = response_json[-1][6] + 1  # add 1 to avoid fetching the same record again
        else:
            print(f"Error: {response.status_code}")
            break
    except Exception as e:
        print(f"Error: {e}")
        break

    # Sleep for 1 second to avoid hitting the API rate limit
    time.sleep(1)

# Save the data to a text file
with open('hist_data/binance/btc_usdt_monthly_bn_16-23.txt', 'w') as file:
    for line in data:
        file.write(json.dumps(line) + '\n')