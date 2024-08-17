import os
import re
import time
import typing
import uuid

import flask
import sqlite3

DATABASE_PATH = os.path.abspath('inventory.db')
ITEMS_TABLE_NAME = 'items'
USERS_TABLE_NAME = 'users'
RESERVATIONS_TABLE_NAME = 'reservations'


class FlaskPOSTForm:
    def __init__(self, form):
        self.form = form

    def get(self, key) -> str:
        if key not in self.form:
            flask.abort(400, f"{key} was not found in request")
        value = self.form[key]
        if is_dirty(value):
            flask.abort(400, f"{key} was malformed")
        return value


def get_db_connection():
    conn = getattr(flask.g, '_database', None)
    if conn is None:
        conn = flask.g._database = sqlite3.connect(DATABASE_PATH)
    return conn


def is_dirty(value: str):
    return len(re.findall(r"[^\w\d\s\\\-\=\_\/\.\,]", value)) != 0


def time_ms() -> int:
    return int(time.time_ns() * 1e-6)


def create_random_id(length: int = 32) -> str:
    return uuid.uuid4().hex[:min(length, 32)]


def create_response(code: int, body: typing.Union[list[dict], dict]) -> dict:
    if not isinstance(body, list):
        body = [body]
    return {
        "code": code,
        "body": body
    }
