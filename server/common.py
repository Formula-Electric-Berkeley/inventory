import re

import flask
import sqlite3

DATABASE_PATH = 'inventory.db'


class FlaskForm:
    def __init__(self, form):
        self.form = form

    def get(self, key) -> str:
        value = self.form[key]
        if is_dirty(value):
            flask.abort(400)
        return value


def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(DATABASE_PATH)
    return db


def is_dirty(value: str):
    return len(re.findall(r"[^\w\d\s\\\-\=\_\/\.\,]", value)) != 0
