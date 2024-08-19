import auth
import common
import flask
import models

api_item_blueprint = flask.Blueprint('api_item', __name__)


@api_item_blueprint.route('/api/item/get/<item_id>', methods=['GET'])
def api_item_get_static(item_id):
    """
    Get a single inventory item by item ID. Route forms a permalink (static) URL. ::

        GET /api/item/get/<item_id>

    :return: 200 on success with :py:class:`models.Item`,\n
             400 if item ID was malformed,\n
             404 if item was not found
    """
    return _process_get_request(item_id)


@api_item_blueprint.route('/api/item/get', methods=['GET', 'POST'])
def api_item_get_dynamic():
    """
    Get a single inventory item by item ID. Route URL is mutable by item ID (dynamic). ::

        GET /api/item/get?item_id=<item_id>
        POST /api/item/get [<item_id>]

    :return: 200 on success with :py:class:`models.Item`,\n
             400 if item ID was not found,\n
             400 if item ID was malformed,\n
             404 if item was not found
    """
    # If GET use query parameters, else if POST use form data
    request_parameters = flask.request.form if flask.request.method == 'POST' else flask.request.args
    if 'item_id' not in request_parameters:
        flask.abort(400, 'Item ID was not found')
    return _process_get_request(request_parameters.get('item_id'))


def _process_get_request(item_id):
    # Do not require authentication for item retrieve if item ID is known
    if common.is_dirty(item_id):
        flask.abort(400, 'Item ID was malformed')
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME} WHERE item_id=?', (item_id,))
    db_item = res.fetchone()
    if db_item is None or len(db_item) == 0:
        flask.abort(404, 'Item does not exist')
    item = models.Item(*db_item)
    return item.to_response()


@api_item_blueprint.route('/api/item/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_CREATE)
def api_item_create():
    """
    Create an inventory item with given parameters.

    Requires :py:attr:`auth.Scopes.ITEM_CREATE`
    :return:
    """
    # TODO description
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    user_res = cursor.execute(f'SELECT user_id FROM {common.USERS_TABLE_NAME} WHERE api_key=?', (form.get('api_key'),))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user_id = db_user[0]

    item = models.Item(
        item_id=common.create_random_id(length=8),
        mfg_part_number=form.get('mfg_part_number'),
        quantity=form.get('quantity', int),
        description=form.get('description'),
        digikey_part_number=form.get('digikey_part_number'),
        mouser_part_number=form.get('mouser_part_number'),
        jlcpcb_part_number=form.get('jlcpcb_part_number'),
        created_by=user_id,
        created_epoch_millis=common.time_ms(),
    )
    cursor.execute('INSERT INTO items VALUES (?)', (item.to_insert_str(),))
    conn.commit()
    return item.to_response()


@api_item_blueprint.route('/api/item/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_UPDATE)
def api_item_update():
    # TODO description
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    # Check that item exists in DB before modifying
    item_id = form.get('item_id')
    item_res = cursor.execute(f'SELECT 1 FROM {common.ITEMS_TABLE_NAME} WHERE item_id=? LIMIT 1', (item_id,))
    db_item = item_res.fetchone()
    if db_item is None or len(db_item) == 0 or db_item == 0:
        flask.abort(404, 'Item does not exist')

    # TODO have a better solution for mutability
    item_properties = models.BLANK_ITEM.to_dict()
    item_properties.pop('item_id')
    item_properties.pop('created_by')
    item_properties.pop('created_epoch_millis')

    properties_to_update = {k: v for k, v in item_properties.items() if k in form.form}
    if len(properties_to_update) <= 0:
        flask.abort(400, 'No attributes to be updated were provided')

    for key, value in properties_to_update.items():
        query_params = (form.get(key, type(value)), item_id)
        cursor.execute(f'UPDATE {common.ITEMS_TABLE_NAME} SET {key}=? WHERE item_id=?', query_params)
    conn.commit()

    return common.create_response(200, {})


@api_item_blueprint.route('/api/item/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_REMOVE)
def api_item_remove():
    # TODO description
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    item_id = form.get('item_id')
    item_res = cursor.execute(f'SELECT 1 FROM {common.ITEMS_TABLE_NAME} WHERE item_id=? LIMIT 1', (item_id,))
    db_item = item_res.fetchone()
    if db_item is None or len(db_item) == 0 or db_item == 0:
        flask.abort(404, 'Item does not exist')

    cursor.execute(f'DELETE FROM {common.ITEMS_TABLE_NAME} WHERE item_id=?', (item_id,))
    conn.commit()

    return common.create_response(200, {})


@api_item_blueprint.route('/api/items/list', methods=['GET', 'POST'])
def api_items_list():
    # TODO description
    # TODO make this not display EVERYTHING or at least do some rate limiting
    conn = common.get_db_connection()
    cursor = conn.cursor()

    # If GET use query parameters, else if POST use form data
    request_parameters = flask.request.form if flask.request.method == 'POST' else flask.request.args

    if 'sortby' in request_parameters:
        direction = request_parameters.get('direction', default='ASC').upper()
        if common.is_dirty(direction) or (direction not in ('DESC', 'ASC')):
            flask.abort(400, 'direction is malformed, should be DESC or ASC')

        sortby = request_parameters.get('sortby')
        if common.is_dirty(sortby):
            flask.abort(400, 'sortby is malformed')
        if sortby not in models.BLANK_ITEM.to_dict().keys():
            flask.abort(400, f'{sortby} is not a valid sort key')

        query = f'SELECT * FROM {common.ITEMS_TABLE_NAME} ORDER BY {sortby} {direction}'
        res = cursor.execute(query)
    else:
        res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME}')
    db_items = res.fetchall()

    items = [models.Item(*db_item) for db_item in db_items]
    return common.create_response(200, [item.to_dict() for item in items])
