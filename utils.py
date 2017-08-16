from aiohttp import web
from passlib.handlers.pbkdf2 import pbkdf2_sha256


def make_password(raw_password):
    return pbkdf2_sha256.hash(raw_password)


def check_password(raw_password, password_hash):
    return pbkdf2_sha256.verify(raw_password, password_hash)


def make_response(data: dict, status: int=200):
    return web.json_response(data=data, status=status)


def make_ok_response(data=None, status: int=200):
    return make_response({
        'status': 'ok',
        'data': data
    }, status)


def make_error_response(message: str=None, status: int=400):
    return make_response({
        'status': 'error',
        'message': message
    }, status)
