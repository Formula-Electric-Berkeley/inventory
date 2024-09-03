"""
Common tools and utilities, mainly for API routes.
"""
import os
import re
import sqlite3
import time
import typing
from sqlite3.dbapi2 import Connection
from sqlite3.dbapi2 import Cursor
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import flask
from identifier import Identifier


DATABASE_PATH = os.path.abspath('inventory.db')
RET_ENTITIES_DEF_LIMIT = 100                     #: Default number of returned entities.
RET_ENTITIES_MAX_LIMIT = 1000                    #: Maximum number of returned entities.

Response = Dict[str, Any]
T = Union[str, int, Identifier]


class FlaskPOSTForm:
    """
    Wraps around any key-value map for safety checking.
    Intended for Flask's POST form data response object.
    """

    def __init__(self, form):
        self.form = form

    def get(self, key, expected_type: typing.Type[T] = str) -> T:
        """
        Get the value of ``form[key]`` with a given expected type.

        Intended to be used within a Flask application context.
        Responds with a ``400`` error if:

            - The key was not found in the request
            - The value was malformed
            - The value could not be converted to the expected type

        If an expected type is passed, the form result will be
        cast from the default type of ``str``.
        """
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


def get_db_connection() -> Tuple[Connection, Cursor]:
    """Get a connection to the backing SQL database. May be cached/already open."""
    conn = getattr(flask.g, '_database', None)
    if conn is None:
        conn = flask.g._database = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    return conn, cursor


def is_dirty(value: str) -> bool:
    """
    Check if the passed string contains dangerous characters.

    Permitted characters/character ranges:

        - Uppercase letters [A-Z]
        - Lowercase letters [a-z]
        - Numbers [0-9]
        - Hyphen (-)
        - Underscore (_)
        - Backslash (\\)
        - Forward slash (/)
        - Period (.)
        - Comma (,)
        - Equals sign (=)

    All other characters are considered dangerous.

    :return: ``True`` if the string contains dangerous characters, else ``False``.
    """
    return len(re.findall(r'[^\w\d\s\\\-\=\_\/\.\,]', value)) != 0


def time_ms() -> int:
    """Get the current time in milliseconds (floor'd from nanosecond-precision)."""
    return int(time.time_ns() * 1e-6)


def create_response(code: int, body: Union[List[dict], dict]) -> Dict[str, Any]:
    """
    Create a response from some status code and response body.

    The format of a standard response from any Flask API route is: ::

        {
            'code': <number>,
            'body': [
                <one or more of models.Model>
                ...
            ]
        }

    :see also: :py:class:`models.Model`
    """
    if not isinstance(body, list):
        body = [body]
    return {
        'code': code,
        'body': body,
    }
