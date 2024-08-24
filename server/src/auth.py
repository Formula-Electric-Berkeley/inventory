import enum
from functools import wraps

import common
import flask


class Scope(enum.IntFlag):
    """
    Authentication scopes required for each API route.

    Each user stores an ``authmask`` composite of scopes such that they may access
    any combination of API routes and access may be modified after user creation.

    Each enum int flag value evaluates to powers of two, ascending with ordinal.

        * See: https://docs.python.org/3/library/enum.html#enum.auto
        * See: https://docs.python.org/3/library/enum.html#enum.IntFlag
    """
    ITEM_GET = enum.auto()
    ITEM_CREATE = enum.auto()
    ITEM_UPDATE = enum.auto()
    ITEM_REMOVE = enum.auto()
    ITEMS_LIST = enum.auto()
    RESERVATION_GET = enum.auto()
    RESERVATION_CREATE = enum.auto()
    RESERVATION_UPDATE = enum.auto()
    RESERVATION_REMOVE = enum.auto()
    RESERVATIONS_LIST = enum.auto()
    USER_GET = enum.auto()
    USER_CREATE = enum.auto()
    USER_UPDATE = enum.auto()
    USER_REMOVE = enum.auto()


def route_requires_auth(scope):
    def for_route(route):
        @wraps(route)
        def execute():
            if 'api_key' not in flask.request.form:
                flask.abort(400, 'API key was not present')
            require_auth(scope, flask.request.form.get('api_key'))
            return route()
        execute.__name__ = route.__name__
        execute.__doc__ = route.__doc__
        return execute

    return for_route


def require_auth(req_authmask: Scope, api_key: str) -> None:
    if isinstance(req_authmask, Scope):
        req_authmask = req_authmask.value

    if common.is_dirty(api_key):
        flask.abort(400, 'API key was malformed')

    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f'SELECT authmask FROM {common.USERS_TABLE_NAME} WHERE api_key=?', (api_key,))
    db_authmask = res.fetchone()

    if db_authmask is None or len(db_authmask) != 1:
        flask.abort(401, 'User was not found')
    try:
        authmask = int(db_authmask[0])
        if (req_authmask & authmask) != req_authmask:
            flask.abort(403, 'User was not authorized to access this resource')
    except ValueError:
        flask.abort(500, 'Error while determining user permissions')
