from typing import Type

import common
import flask
import models


def get(id_: str, id_name: str, table_name: str, entity_type: Type[models.Model]):
    if common.is_dirty(id_):
        flask.abort(400, f'{id_name} was malformed')
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f'SELECT * FROM {table_name} WHERE {id_name}=?', (id_,))
    db_entity = res.fetchone()
    if db_entity is None or len(db_entity) == 0:
        flask.abort(404, 'Item does not exist')
    entity = entity_type(*db_entity)
    return entity.to_response()


def update(id_name: str, table_name: str, blank_entity: models.Model, immutable_props: list[str]):
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    # Check that entity exists in DB before modifying
    id_ = form.get(id_name)
    res = cursor.execute(f'SELECT 1 FROM {table_name} WHERE {id_name}=? LIMIT 1', (id_,))
    db_entity = res.fetchone()
    if db_entity is None or len(db_entity) == 0 or db_entity == 0:
        flask.abort(404, f'{blank_entity.__class__.__name__} does not exist')

    # TODO have a better solution for mutability
    entity_properties = blank_entity.to_dict()
    for immutable_prop in immutable_props:
        entity_properties.pop(immutable_prop)

    properties_to_update = {k: v for k, v in entity_properties.items() if k in form.form}
    if len(properties_to_update) <= 0:
        flask.abort(400, 'No attributes to be updated were provided')

    for key, value in properties_to_update.items():
        query_params = (form.get(key, type(value)), id_)
        cursor.execute(f'UPDATE {table_name} SET {key}=? WHERE {id_name}=?', query_params)
    conn.commit()

    updated_res = cursor.execute(f'SELECT * FROM {table_name} WHERE {id_name}=?', (id_,))
    db_updated_entity = updated_res.fetchone()
    if db_updated_entity is None or len(db_updated_entity) == 0:
        flask.abort(404, f'{blank_entity.__class__.__name__} did not exist after updating')
    updated_entity = blank_entity.__class__.__new__(*db_updated_entity)
    return updated_entity.to_response()


def remove(id_name: str, table_name: str, entity_type: Type[models.Model]):
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    id_ = form.get(id_name)
    entity_res = cursor.execute(f'SELECT * FROM {table_name} WHERE {id_name}=?', (id_,))
    db_entity = entity_res.fetchall()
    if db_entity is None or len(db_entity) == 0 or db_entity == 0:
        flask.abort(404, f'{entity_type.__name__} does not exist')
    if len(db_entity) != 1:
        flask.abort(500, f'Expected 1 item with matching {entity_type.__name__.lower()} ID, got {len(db_entity)}')

    cursor.execute(f'DELETE FROM {table_name} WHERE {id_name}=?', (id_,))
    conn.commit()

    deleted_entity = entity_type(*db_entity)
    return deleted_entity.to_response()


def list_(table_name: str, entity_type: Type[models.Model]):
    # TODO make this not display EVERYTHING or at least do some rate limiting
    # TODO add a search functionality option to this too
    conn = common.get_db_connection()
    cursor = conn.cursor()

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
        if sortby not in models.BLANK_ITEM.to_dict().keys():
            flask.abort(400, f'{sortby} is not a valid sort key')

        query = f'SELECT * FROM {table_name} ORDER BY {sortby} {direction} LIMIT {limit}'
        res = cursor.execute(query)
    else:
        res = cursor.execute(f'SELECT * FROM {table_name} LIMIT {limit}')
    db_entities = res.fetchall()

    entities = [entity_type(*db_entity) for db_entity in db_entities]
    return common.create_response(200, [item.to_dict() for item in entities])
