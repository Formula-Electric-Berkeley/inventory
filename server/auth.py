import enum

import flask

import common


# Evaluates to powers of two, ascending with ordinal
# See: https://docs.python.org/3/library/enum.html#enum.auto
# See: https://docs.python.org/3/library/enum.html#enum.IntFlag
class Scope(enum.IntFlag):
    ITEM_GET = enum.auto()
    ITEM_CREATE = enum.auto()
    ITEM_UPDATE = enum.auto()
    ITEM_REMOVE = enum.auto()
    RESERVATION_GET = enum.auto()
    RESERVATION_CREATE = enum.auto()
    RESERVATION_UPDATE = enum.auto()
    RESERVATION_REMOVE = enum.auto()
    ITEMS_LIST = enum.auto()
    ITEMS_BULKADD = enum.auto()
    USER_GET = enum.auto()
    USER_CREATE = enum.auto()
    USER_UPDATE = enum.auto()
    USER_REMOVE = enum.auto()


def require_auth(req_authmask: Scope, api_key: str) -> None:
    if isinstance(req_authmask, Scope):
        req_authmask = req_authmask.value

    if common.is_dirty(api_key):
        flask.abort(400)

    res = common.get_db().cursor().execute(f"SELECT authmask FROM users WHERE api_key='{api_key}'")
    db_authmask = res.fetchone()

    if db_authmask is None or len(db_authmask) != 1:
        flask.abort(401)
    try:
        authmask = int(db_authmask[0])
        if (req_authmask & authmask) != req_authmask:
            flask.abort(403)
    except ValueError:
        flask.abort(500)
