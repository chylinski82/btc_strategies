import asyncio
import websockets
import json

client_id = "KAPBrIVH" #replace this with your key
client_secret = "gfMjmLDyVYNhBMleog0XFBPC2Dyc0mgBQ1icn7HQBRE" # replace with your secret

msg = \
{
  "jsonrpc" : "2.0",
  "id" : 9929,
  "method" : "public/auth",
  "params" : {
    "grant_type" : "client_credentials",
    "client_id" : client_id,
    "client_secret" : client_secret
  }
}

async def call_api(msg):
   async with websockets.connect('wss://www.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
           response = await websocket.recv()
           # process the response...
           response_json = json.loads(response)
           if 'result' in response_json:
               access_token = response_json['result'].get('access_token')
               expires_in = response_json['result'].get('expires_in')
               refresh_token = response_json['result'].get('refresh_token')
               
               print(f"Access token: {access_token}")
               print(f"Expires in: {expires_in} seconds")
               print(f"Refresh token: {refresh_token}")
               
               return access_token, expires_in, refresh_token
           else:
               print(f"Error: {response_json}")
               return None

if __name__ =='__main__':
    asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))