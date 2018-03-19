import asyncio                       
import asyncws
import json
import os
from time import sleep

# 树莓派上配置
wslocalAdd = 'ws://hassio/homeassistant/websocket'
password = os.environ.get('HASSIO_TOKEN')
wsServerAdd = 'ws://aligenie.xujialiang.net/socket.io'

# 调试配置
# wslocalAdd = 'ws://192.168.2.120:8123/api/websocket'
# wsServerAdd = 'ws://aligenie.xujialiang.net/socket.io'
# password = 'xjlabcd1234'


msgId = 1
websocketFromServer = None;
websocket = None;

config_serverAdd = os.environ.get('SOCKET_SERVER');
auth_token = os.environ.get('AUTH_TOKEN');

if config_serverAdd is not None:
    wsServerAdd = 'ws://' + config_serverAdd + '/socket.io'
print (wsServerAdd)
print (auth_token)

@asyncio.coroutine
def wslocal():
    global websocketFromServer
    global websocket
    global wslocalAdd
    global password
    global msgId
    try:
        print ('连接add-on内部代理')
        print (wslocalAdd)
        websocket = yield from asyncws.connect(wslocalAdd)
        authPass = False;
        while True:
            message = yield from websocket.recv()
            if message == '' or message is None:
                continue
            messageObj = json.loads(message)
            if messageObj['type'] == 'auth_ok':
                print ('websocket api 认证成功')
                authPass = True
                msgId += 1
                yield from websocket.send(json.dumps({'id': msgId, 'type': 'subscribe_events', 'event_type': 'state_changed'}))
                continue
            if messageObj['type'] == 'auth_invalid':
                print ('websocket api 认证失败')
                break
            if messageObj['type'] == 'auth_required':
                print ('auth_required 认证中')
                res = json.dumps({'type': 'auth','api_password': password })
                yield from websocket.send(res)
                continue

            if not authPass:
                continue

            if message is not None:
                if websocketFromServer is not None:
                    messageObj['token'] = auth_token
                    messageObj['auth_token'] = auth_token
                    yield from websocketFromServer.send(json.dumps(messageObj))
            else:
                continue

    except Exception as inst:
        print (inst)
        raise Exception

@asyncio.coroutine
def wsServer():
    global websocketFromServer
    global websocket
    global wsServerAdd
    global loop
    try:
        print ('连接转发服务器')
        print (wsServerAdd)
        websocketFromServer = yield from asyncws.connect(wsServerAdd)
        while True:
            messageFromServer = yield from websocketFromServer.recv()
            if messageFromServer == '' or messageFromServer is None:
                continue
            messageFromServerObj = json.loads(messageFromServer)

            if messageFromServerObj is not None and messageFromServerObj['code'] == 0:
                if websocket is not None:
                    print("Rev Command:" + messageFromServer)
                    yield from websocket.send(json.dumps(messageFromServerObj['command']))

    except Exception as inst:
        print(inst)
        raise Exception


while True:
    try:
        tasks = [asyncio.Task(wslocal()), asyncio.Task(wsServer())]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as inst:
        print('开始重连')
        sleep(5)
