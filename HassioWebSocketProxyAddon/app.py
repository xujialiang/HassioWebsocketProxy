import asyncio                       
import asyncws
import json
import os

# 树莓派上配置
wslocalAdd = 'ws://hassio/homeassistant/websocket'
password = os.environ.get('HASSIO_TOKEN')
wsServerAdd = 'ws://aligenie.xujialiang.net/socket.io'

# 调试配置
# wslocalAdd = 'ws://192.168.2.120:8123/api/websocket'
# wsServerAdd = 'ws://192.168.2.115:9001/socket.io'
# password = 'xjlabcd1234'


msgId = 1
websocketFromServer = None;
websocket = None;

config_serverAdd = os.environ.get('SOCKET_SERVER');
config_token = os.environ.get('TOKEN');

if config_serverAdd is not None:
    wsServerAdd = 'ws://' + config_serverAdd + '/socket.io'
print (wsServerAdd)
print (config_token)


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
            print ('准备接收数据')
            message = yield from websocket.recv()
            print ('Rev Message:')
            print (message)
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
                    messageObj['token'] = config_token
                    yield from websocketFromServer.send(json.dumps(messageObj))
            else:
                continue

    except Exception as inst:
        print (inst)


@asyncio.coroutine
def wsServer():
    global websocketFromServer
    global websocket
    global wsServerAdd
    try:
        print ('连接转发服务器')
        print (wsServerAdd)
        websocketFromServer = yield from asyncws.connect(wsServerAdd)
        while True:
            print ('准备接收指令')
            messageFromServer = yield from websocketFromServer.recv()
            print('Rev Order:')
            print (messageFromServer)
            messageFromServerObj = json.loads(messageFromServer)

            if messageFromServerObj is not None and messageFromServerObj['code'] == 0:
                if websocket is not None:
                    print ("Rev Command:"+messageFromServer)
                    yield from websocket.send(json.dumps(messageFromServerObj['command']))
    except Exception as inst:
        print (inst)

tasks = [asyncio.Task(wslocal()), asyncio.Task(wsServer())]
asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
asyncio.get_event_loop().close() 
