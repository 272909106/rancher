import requests
import websocket
import threading
import time
import base64
import json

def on_message(ws, message):
    # print(message)
    if message:
        data=json.loads(message)
        # print(data['name'])
        if data['name'] == 'resource.change':
            # if data['data']['resource']['eventType'] != 'dns.update':
            print(data['data'])
            # with open('websocket.log','wb') as f:
            #     f.write(data['data'])
def on_error(ws, error):
    print(error)

def on_close(ws):
    print( "### closed ###")

def on_open(ws):
    time.sleep(1)
    pass
    # def run(*args):
        # for i in range(3):
            # time.sleep(1)
            # ws.send("Hello %d" % i)
            # ws.recv(1)
        # pass
        # time.sleep(1)
        # ws.close()
        # print("thread terminating...")
    # thread.start_new_thread(run, ())
    # threading._start_new_thread(run,())

if __name__ == "__main__":
    access_key = 'xxxx'
    secret_key = 'xxxxx'
	#rancher server地址及端口
    host = 'x.x.x.x'
    port = 8080
    url = ('ws://{0}:{1}/v2-beta/projects/1a5/subscribe?eventNames=resource.change&limit=-1&sockId=1').format(host,port)
    print(url)
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                                header={"Authorization": "Basic " + (base64.b64encode(b"xxxx:xxxxx")).decode('utf8')})
    ws.on_open = on_open
    ws.run_forever()