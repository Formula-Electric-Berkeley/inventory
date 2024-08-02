import os
import re
import time

import flask
import sqlite3

DATABASE_PATH = os.path.abspath('inventory.db')


class FlaskPOSTForm:
    def __init__(self, form):
        self.form = form

    def get(self, key) -> str:
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
