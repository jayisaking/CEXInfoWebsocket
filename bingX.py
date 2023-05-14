
import gzip
import requests
import json
import io
import websocket
import time
import threading
url = 'https://open-api.bingx.com/openApi/user/auth/userDataStream'
params = {'X-BX-APIKEY': 'fill you own'}
response = requests.post(url, headers = params)
responseText = json.loads(response.text)
listenKey = responseText['listenKey']
statuses = []
timeout_interval = 50
ws = websocket.WebSocket()
"""
    This is a Python script that connects to a WebSocket API and listens for BingX messages, processing them
    and printing out relevant details.
    
    :param ws: This is a variable that is used to store the WebSocket connection object
    :param message: This code sets up a WebSocket connection to the Bingx API and listens for messages.
    When a message is received, it is processed and printed to the console. The `detail_names`
    dictionary maps the keys in the received messages to human-readable names. The `on_message` function
    handles the received messages
"""
# listenKey = 'ee5c360ff160dc5af07d31c2e9e45e28f03a016b5ced6e6bc74f06df104e7609'
print(listenKey)
detail_names = {
    "s":"trading pair",
    "c":"client custom order ID", 
    "i": "Order ID",
    "S": "order direction", 
    "o": "MAorder type",
    "q": "order quantity",
    "p": "order price",
    "ap":"order average price", 
    "x": "The specific execution type of this event",
    "X": "current status of the order", 
    "N": "Fee asset type", 
    "n": "handling fee",
    "T": "transaction time",
    "wt": "trigger price type",
    "ps": "Position direction",
    "rp": "The transaction achieves profit and loss",
    "z": "Order Filled Accumulated Quantity",
    "a": "asset name",
    "wb": "wallet balance", 
    "cw": "Wallet balance excluding isolated margin",
    "bc": "wallet balance change amount", 
    "s":  "trading pair",
    "pa": "position", 
    "ep": "entry price",
    "up": "unrealized profit and loss of positions", 
    "mt": "margin mode",
    "iw": "If it is an isolated position, the position margin", 
    "ps": "position direction",
    "s": "trading pair",
    "l": "long position leverage", 
    "S": "long position leverage",
    "mt": "margin mode"
}
def on_message(ws, message):
    gzip_bytes_io = io.BytesIO(message)

# open the gzip file and read its contents
    with gzip.GzipFile(fileobj=gzip_bytes_io, mode='rb') as gzip_file:
        uncompressed_data = gzip_file.read()
    message = uncompressed_data.decode()
    # print(message)
    if(message == 'Ping'):
        ws.send('Pong')
    else:
        # This code block is responsible for processing the messages received from the WebSocket
        # connection.
        message = json.loads(message)
        print()
        # print(message)
        if "e" in message:
            event = message['e']
            if event == 'ACCOUNT_CONFIG_UPDATE' and 'ac' in message:
                for key in message['ac']:
                    print(detail_names[key], message['ac'][key])
            elif event == 'ORDER_TRADE_UPDATE' and 'o' in message:
                for key in message['o']:
                    print(detail_names[key], message['o'][key])
            elif event == 'ACCOUNT_UPDATE' and 'a' in message:
                if 'B' in message['a']:
                    for i in message['a']['B']:
                        for key in i:
                            print(detail_names[key], i[key])
                if 'P' in message['a']:
                    for i in message['a']['P']:
                        for key in i:
                            print(detail_names[key], i[key])
            
        print()
def on_error(ws, error):
    print('there is error')
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
def extend_listen_key():
    url = 'https://open-api.bingx.com/openApi/user/auth/userDataStream'
    params = {'listenKey': listenKey}
    response = requests.put(url, headers = params)
    threading.Timer(timeout_interval, extend_listen_key).start()
def connect_websocket():
    # `global ws` is declaring that the variable `ws` is a global variable, meaning it can be accessed
    # and modified from anywhere in the code.
    global ws
    ws = websocket.WebSocketApp("wss://open-api-swap.bingx.com/swap-market?listenKey=" + listenKey, #?listenKey=" + listenKey,
                            on_open = on_open,
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
    threading.Timer(timeout_interval, extend_listen_key).start()
    ws.run_forever()

while True:
    try:
        connect_websocket()
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        continue
    time.sleep(5)  # Wait for 5 seconds before reconnecting
