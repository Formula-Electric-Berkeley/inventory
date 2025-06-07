"""
Functions interfacing directly with the database.

DB-interfacing functions are parameterized to each :py:class:`models.Model`
(entity type) and return a :py:data:`common.Response` object for Flask routes.

For exceptions, `flask.abort` is called directly instead of returning
an errant :py:data:`common.Response`.
"""
from sqlite3.dbapi2 import Connection
from sqlite3.dbapi2 import Cursor
from typing import List
from typing import Optional
from typing import Type

import auth
import common
import flask
import models
from common import Response


def get(entity_type: Type[models.Model], id_: Optional[str] = None) -> Response:
    """
    Get a single entity from the database, keyed by its type (`entity_type`), and identifier (`id_`).

    Leaving `id_` as the default value of `None` retrieves `id_` from :py:func:`flask.Request.args`,
    assuming the `id_` was provided as POST data to the request. The key into the POST data is the
    `id_name` provided by the :py:class:`models.Model` (entity type).

    :param entity_type: the type of the entity to get (:py:class:`models.Model` subclass)
    :param id_: for GET requests, the identifier of the entity to retrieve; None (default) for POST requests.
    :return: ``200`` on success with the desired :py:class:`models.Model`,\n
             ``400`` if `id_` was not found,\n
             ``400`` if `id_` was malformed,\n
             ``404`` if the desired entity was not found (POST only), \n
             ``500`` if `id_` was not the expected length
    """
    if id_ is None:
        if entity_type.id_name not in flask.request.args:
            flask.abort(400, f'{entity_type.id_name} was not found in request')
        id_ = flask.request.args.get(entity_type.id_name)
    if common.is_dirty(id_):
        flask.abort(400, f'{entity_type.id_name} was malformed')

    conn, cursor = common.get_db_connection()
    res = cursor.execute(
        f'SELECT * FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,),
    )
    db_entity = res.fetchone()
    if db_entity is None or len(db_entity) == 0:
        flask.abort(404, f'{entity_type.__name__} does not exist')
    entity = entity_type(*db_entity)
    return entity.to_response()


def update(entity_type: Type[models.Model], immutable_props: List[str]) -> Response:
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    # Check that entity exists in DB before modifying
    id_ = form.get(entity_type.id_name)
    res = cursor.execute(
        f'SELECT 1 FROM {entity_type.table_name} WHERE {entity_type.id_name}=? LIMIT 1', (id_,),
    )
    db_entity = res.fetchone()
    if db_entity is None or len(db_entity) == 0 or db_entity == 0:
        flask.abort(404, f'{entity_type.__name__} does not exist')

    entity_properties = models.get_model_attributes(entity_type)
    for immutable_prop_name in immutable_props:
        if immutable_prop_name in form.form and immutable_prop_name != entity_type.id_name:
            flask.abort(400, f'Immutable property {immutable_prop_name} found in request body')
        entity_properties.pop(immutable_prop_name)

    properties_to_update = {
        name: type_ for name, type_ in entity_properties.items() if name in form.form
    }
    if len(properties_to_update) <= 0:
        flask.abort(400, 'No attributes to be updated were provided')

    for prop_name, prop_type in properties_to_update.items():
        query_params = (form.get(prop_name, prop_type), id_)
        cursor.execute(
            f'UPDATE {entity_type.table_name} SET {prop_name}=? WHERE {entity_type.id_name}=?', query_params,
        )
    conn.commit()

    updated_res = cursor.execute(
        f'SELECT * FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,),
    )
    db_updated_entity = updated_res.fetchone()
    if db_updated_entity is None or len(db_updated_entity) == 0:
        flask.abort(404, f'{entity_type.__class__.__name__} did not exist after updating')
    updated_entity = entity_type(*db_updated_entity)
    return updated_entity.to_response()


def delete(entity_type: Type[models.Model]) -> Response:
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    id_ = form.get(entity_type.id_name)
    entity_res = cursor.execute(
        f'SELECT * FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,),
    )
    db_entities = entity_res.fetchall()
    if db_entities is None or len(db_entities) == 0 or db_entities == 0:
        flask.abort(404, f'{entity_type.__name__} does not exist')
    if len(db_entities) != 1:
        flask.abort(
            500, f'Expected 1 item with matching {entity_type.__name__.lower()} ID, got {len(db_entities)}',
        )
    db_entity = db_entities[0]

    cursor.execute(
        f'DELETE FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,),
    )
    conn.commit()

    deleted_entity = entity_type(*db_entity)
    return deleted_entity.to_response()


_list_cache = models.EntityCache()


def list_(entity_type: Type[models.Model]) -> Response:
    # TODO documentation
    conn, cursor = common.get_db_connection()

    limit = get_int_parameter(
        'limit', common.RET_ENTITIES_DEF_LIMIT, flask.request.args,
    )
    limit = min(limit, common.RET_ENTITIES_MAX_LIMIT)

    offset = get_int_parameter('offset', 0, flask.request.args)

    direction = flask.request.args.get('direction', default='ASC').upper()
    if common.is_dirty(direction) or (direction not in ('DESC', 'ASC')):
        flask.abort(400, 'direction is malformed, should be DESC or ASC')

    sortby = None
    if 'sortby' in flask.request.args:
        sortby = flask.request.args.get('sortby')
        if common.is_dirty(sortby):
            flask.abort(400, 'sortby is malformed')
        if sortby not in models.get_model_attributes(entity_type).keys():
            flask.abort(400, f'{sortby} is not a valid sort key')

        query = f'SELECT * FROM {entity_type.table_name} ORDER BY {sortby} {direction}'
    else:
        query = f'SELECT * FROM {entity_type.table_name}'

    cache_key = models.EntityCacheKey(entity_type, direction=direction, sortby=sortby)
    cached_result = _list_cache.get(cache_key)
    if cached_result is not None:
        entities = cached_result
    else:
        res = cursor.execute(query)
        db_entities = res.fetchall()
        entities = [entity_type(*db_entity) for db_entity in db_entities]
        _list_cache.add(cache_key, entities)

    cut_entities = models.EntityCache.cut(entities, limit, offset)
    return common.create_response(200, [item.to_dict() for item in cut_entities])


def count(entity_type: Type[models.Model]) -> Response:
    # TODO documentation
    _, cursor = common.get_db_connection()
    query = f'SELECT COUNT(*) FROM {entity_type.table_name}'
    res = cursor.execute(query)
    entity_count = res.fetchone()
    if len(entity_count) != 1:
        flask.abort(500, f'could not count {entity_type.table_name}')
    return common.create_response(200, [{'count': int(entity_count[0])}])


def get_int_parameter(key: str, default: int, request_parameters) -> int:
    # TODO documentation
    value = default
    if key in request_parameters:
        value_raw = request_parameters.get(key)
        if common.is_dirty(value_raw):
            flask.abort(400, f'{key} is malformed')
        if not value_raw.isdigit():
            flask.abort(400, f'{value_raw} is not a valid integer {key}')
        value = int(value_raw)
        if value < 0:
            flask.abort(400, f'{key} cannot be negative')
    return value


def get_request_user_id(cursor: Cursor, form: common.FlaskPOSTForm) -> str:
    # TODO documentation
    user_query = f'SELECT {models.User.id_name} FROM {models.User.table_name} WHERE {auth.API_KEY_NAME}=?'
    user_res = cursor.execute(user_query, (form.get(auth.API_KEY_NAME),))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user_id = db_user[0]
    return user_id


def get_user_id_exists(user_id: str) -> bool:
    conn, cursor = common.get_db_connection()
    user_query = f"SELECT {models.User.id_name} FROM {models.User.table_name} WHERE user_id='{user_id}'"
    user_res = cursor.execute(user_query)
    db_user = user_res.fetchone()
    return db_user is not None and len(db_user) != 0


def create_entity(conn: Connection, cursor: Cursor, entity: models.Model) -> None:
    # TODO documentation
    query_placeholders = ', '.join('?' for _ in range(len(entity.to_dict())))
    query = f'INSERT INTO {entity.table_name} VALUES ({query_placeholders})'
    cursor.execute(query, (*entity,))
    conn.commit()
