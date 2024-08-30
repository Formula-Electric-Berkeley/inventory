import os
import re
import sqlite3
import time
import typing
from typing import Union

import flask
from identifier import Identifier

DATABASE_PATH = os.path.abspath('inventory.db')
RET_ENTITIES_LIMIT = 200                     #: Maximum number of returned entities.

T = Union[str, int, Identifier]


class FlaskPOSTForm:
    def __init__(self, form):
        self.form = form

    def get(self, key, expected_type: typing.Type[T] = str) -> T:
        if key not in self.form:
            flask.abort(400, f'{key} was not found in request')
        value = self.form[key]
        if is_dirty(value):
            flask.abort(400, f'{key} was malformed')
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except ValueError:
                flask.abort(400, f'{key} could not be converter to type {expected_type.__name__}')
        return value


def get_db_connection():
    conn = getattr(flask.g, '_database', None)
    if conn is None:
        conn = flask.g._database = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    return conn, cursor


def is_dirty(value: str):
    return len(re.findall(r'[^\w\d\s\\\-\=\_\/\.\,]', value)) != 0


def time_ms() -> int:
    return int(time.time_ns() * 1e-6)


def create_response(code: int, body: Union[list[dict], dict]) -> dict:
    if not isinstance(body, list):
        body = [body]
    return {
        'code': code,
        'body': body,
    }
