import json

import aiohttp
from aiohttp import web
import jwt
from pony import orm

from models import User, Room, Message
from utils import make_error_response, make_password, make_ok_response

SECRET = 'YREwod23beLXiJ[IDIRvAKW3JbUPapn4B%UBxOpw4B@pQIkiviLIwj'


async def register(request: web.Request):
    body = await request.json()
    if not {'username', 'password1', 'password2'}.issubset(body.keys()):
        return make_error_response('Not all params were provided: '
                                   '`username`, `password1` and `password2` are required.')

    if body['password1'] != body['password2']:
        return make_error_response('Passwords do not match', 422)

    with orm.db_session:
        try:
            User(username=body['username'], password=make_password(body['password1']))
            orm.commit()
        except orm.ConstraintError:
            return make_error_response('Username is already taken', 409)

    return make_ok_response()


async def auth(request: web.Request):
    body = await request.json()
    if not {'username', 'password'}.issubset(body.keys()):
        return make_error_response('Not all params were provided: `username` and `password` are required.')

    with orm.db_session:
        try:
            user = User.get(lambda u: u.username == body['username'])
            if not user.check_password(body['password']):
                raise orm.ObjectNotFound(User)
        except orm.ObjectNotFound:
            return make_error_response('Username and/or password are incorrect', 422)

        return make_ok_response({
            'token': jwt.encode({'username': user.username}, SECRET).decode()
        })


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    with orm.db_session:
        try:
            jwt_payload = jwt.decode(request.query['token'], SECRET)
            user = User.get(lambda u: u.username == jwt_payload['username'])
        except jwt.DecodeError:
            ws.send_json({'type': 'error', 'code': 'Malformed JWT'})
            await ws.close()
        except orm.ObjectNotFound:
            ws.send_json({'type': 'error', 'code': 'User was not found'})
            await ws.close()

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

    return ws


app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/auth', auth)
app.router.add_get('/chat_ws', websocket_handler)

web.run_app(app, host='0.0.0.0', port=10080)
