import websocket
import threading
import time
import hmac
import hashlib
import base64
import json
# WebSocket endpoint URL
ws_url = "wss://ws.bitget.com/mix/v1/stream"

# Timer interval in seconds
timer_interval = 25

# Create a WebSocket connection
ws = websocket.WebSocket()

# Flag to indicate whether a message has been received
message_received = False

api_key = 000000
passphrase = 000000
secret_key = 000000

def on_message(ws, message_str):
# This is the `on_message` function that is called whenever a message is received from the WebSocket
# connection.
    global message_received
    if message_str == 'pong':
        # print('Received pong')
        message_received = True
        return
    # print(f"Received message: {message_str}")
    message_received = True
    message = json.loads(message_str)
    # This code block is checking if the received message is a login event with a code of 0,
    # indicating a successful login. If so, it sends a subscription request to the WebSocket to
    # subscribe to channels related to account, positions, orders, and ordersAlgo. The subscription
    # request is in the form of a JSON object and is sent using the `ws.send()` method.
    if 'event' in message and message['event'] == 'login' and message['code'] == 0:
        print('Login Succeed')
        subscribe = {
                        "op": "subscribe",
                        "args": [{
                            "instType": "UMCBL",
                            "channel": "account",
                            "instId": "default"
                        },
                                 {
                            "instType": "UMCBL",
                            "channel": "positions",
                            "instId": "default"
                        },
                                 {
                            "instType": "UMCBL",
                            "channel": "orders",
                            "instId": "default"
                        },
                                 {
                            "instType": "UMCBL",
                            "channel": "ordersAlgo",
                            "instId": "default"
                        }]
                    }
        ws.send(json.dumps(subscribe))
    # This code block is checking if the received message is related to account, positions, orders, or
    # ordersAlgo channels. If it is, it prints the data contained in the message in a formatted way.
    # The `for` loop is used to iterate over the data in the message and print each key-value pair on
    # a new line.
    elif 'arg' in message:
        if 'channel' in message['arg'] and message['arg']['channel'] in ['positions', 'orders', 'ordersAlgo', 'account'] and 'data' in message:
            for i in message['data']:
                print('\n')
                for key in i:
                    print(key, i[key])
                print('\n')
        

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_error(ws, error):
    print(f"WebSocket error: {error}")

def send_ping():
    threading.Timer(timer_interval, send_ping).start()

def on_open(ws):
    """
    This function sends a login request to a WebSocket using an API key, passphrase, and signature.
    
    :param ws: The WebSocket object used to communicate with the server
    """
    threading.Timer(timer_interval, send_ping).start()
    hmac_obj = hmac.new(secret_key.encode(), digestmod = hashlib.sha256)
    unix_time = str(int(time.time()))
    message = unix_time + 'GET' + '/user/verify'
    hmac_obj.update(message.encode())
    # Get the encrypted message
    encrypted_message = hmac_obj.digest()
    print('encrpted: ', encrypted_message)
    sign = base64.b64encode(encrypted_message).decode('utf-8')
    print('Signature: ', sign)
    request = {
    "op":"login",
    "args":[
        {
            "apiKey": api_key,
            "passphrase": passphrase,
            "timestamp": unix_time,
            "sign": sign
        }
    ]
    }
    json_req = json.dumps(request)
    ws.send(json_req)

def connect_websocket():
    global ws
    ws = websocket.WebSocketApp(ws_url,
                                on_message = on_message,
                                on_close = on_close,
                                on_error = on_error,
                                on_open = on_open)
    ws.run_forever()

while True:
    try:
        connect_websocket()
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        continue
    time.sleep(5)  # Wait for 5 seconds before reconnecting
