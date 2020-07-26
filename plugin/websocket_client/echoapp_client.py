import sys, os
sys.path.append(os.path.join(sys.path[0], 'websocket'))

import websocket
from threading import Thread
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        for i in range(3):
            # send the message, then wait
            # so thread doesn't exit and socket
            # isn't closed
            ws.send("Hello %d" % i)
            time.sleep(1)

        time.sleep(1)
        #ws.close()
        print("Thread terminating...")

    Thread(target=run).start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://127.0.0.1:9001"
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
