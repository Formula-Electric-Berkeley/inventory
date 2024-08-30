# TODO documentation
from sqlite3.dbapi2 import Connection
from sqlite3.dbapi2 import Cursor
from typing import Type

import auth
import common
import flask
import models


def get(id_: str, entity_type: Type[models.Model]):
    # TODO documentation
    if common.is_dirty(id_):
        flask.abort(400, f'{entity_type.id_name} was malformed')
    conn, cursor = common.get_db_connection()
    res = cursor.execute(f'SELECT * FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,))
    db_entity = res.fetchone()
    if db_entity is None or len(db_entity) == 0:
        flask.abort(404, 'Item does not exist')
    entity = entity_type(*db_entity)
    return entity.to_response()


def update(entity_type: Type[models.Model], immutable_props: list[str]):
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    # Check that entity exists in DB before modifying
    id_ = form.get(entity_type.id_name)
    res = cursor.execute(f'SELECT 1 FROM {entity_type.table_name} WHERE {entity_type.id_name}=? LIMIT 1', (id_,))
    db_entity = res.fetchone()
    if db_entity is None or len(db_entity) == 0 or db_entity == 0:
        flask.abort(404, f'{entity_type.__class__.__name__} does not exist')

    # TODO have a better solution for mutability
    entity_properties = models.get_entity_parameters(entity_type)
    for immutable_prop in immutable_props:
        entity_properties.pop(immutable_prop)

    properties_to_update = {k: v for k, v in entity_properties.items() if k in form.form}
    if len(properties_to_update) <= 0:
        flask.abort(400, 'No attributes to be updated were provided')

    for key, value in properties_to_update.items():
        query_params = (form.get(key, type(value)), id_)
        cursor.execute(f'UPDATE {entity_type.table_name} SET {key}=? WHERE {entity_type.id_name}=?', (query_params,))
    conn.commit()

    updated_res = cursor.execute(f'SELECT * FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,))
    db_updated_entity = updated_res.fetchone()
    if db_updated_entity is None or len(db_updated_entity) == 0:
        flask.abort(404, f'{entity_type.__class__.__name__} did not exist after updating')
    updated_entity = entity_type.__class__.__new__(*db_updated_entity)
    return updated_entity.to_response()


def remove(entity_type: Type[models.Model]):
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    id_ = form.get(entity_type.id_name)
    entity_res = cursor.execute(f'SELECT * FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,))
    db_entity = entity_res.fetchall()
    if db_entity is None or len(db_entity) == 0 or db_entity == 0:
        flask.abort(404, f'{entity_type.__name__} does not exist')
    if len(db_entity) != 1:
        flask.abort(500, f'Expected 1 item with matching {entity_type.__name__.lower()} ID, got {len(db_entity)}')

    cursor.execute(f'DELETE FROM {entity_type.table_name} WHERE {entity_type.id_name}=?', (id_,))
    conn.commit()

    deleted_entity = entity_type(*db_entity)
    return deleted_entity.to_response()


def list_(entity_type: Type[models.Model]):
    # TODO documentation
    # TODO make this not display EVERYTHING or at least do some rate limiting
    # TODO add a search functionality option to this too
    conn, cursor = common.get_db_connection()

    # If GET use query parameters, else if POST use form data
    request_parameters = flask.request.form if flask.request.method == 'POST' else flask.request.args

    limit = common.RET_ENTITIES_LIMIT
    if 'limit' in request_parameters:
        limit_raw = request_parameters.get('sortby')
        if common.is_dirty(limit_raw):
            flask.abort(400, 'limit is malformed')
        if not limit_raw.isdigit():
            flask.abort(400, f'{limit_raw} is not a valid integer limit')
        limit = int(limit_raw)

    if 'sortby' in request_parameters:
        direction = request_parameters.get('direction', default='ASC').upper()
        if common.is_dirty(direction) or (direction not in ('DESC', 'ASC')):
            flask.abort(400, 'direction is malformed, should be DESC or ASC')

        sortby = request_parameters.get('sortby')
        if common.is_dirty(sortby):
            flask.abort(400, 'sortby is malformed')
        if sortby not in models.get_entity_parameters(entity_type).keys():
            flask.abort(400, f'{sortby} is not a valid sort key')

        query = f'SELECT * FROM {entity_type.table_name} ORDER BY {sortby} {direction} LIMIT {limit}'
        res = cursor.execute(query)
    else:
        res = cursor.execute(f'SELECT * FROM {entity_type.table_name} LIMIT {limit}')
    db_entities = res.fetchall()

    entities = [entity_type(*db_entity) for db_entity in db_entities]
    return common.create_response(200, [item.to_dict() for item in entities])


def get_request_user_id(cursor: Cursor, form: common.FlaskPOSTForm) -> str:
    user_query = f'SELECT {models.User.id_name} FROM {models.User.table_name} WHERE {auth.API_KEY_NAME}=?'
    user_res = cursor.execute(user_query, (form.get(auth.API_KEY_NAME),))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user_id = db_user[0]
    return user_id


def create_entity(conn: Connection, cursor: Cursor, entity: models.Model):
    query_placeholders = ', '.join('?' for _ in range(len(entity.to_dict())))
    query = f'INSERT INTO {entity.table_name} VALUES ({query_placeholders})'
    cursor.execute(query, (*entity,))
    conn.commit()
