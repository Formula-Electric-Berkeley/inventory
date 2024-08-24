"""
The Item API can create, get, update, remove, and list inventory item(s).

All routes except item retrieval require authentication, which is handled by :py:mod:`auth`.
Idempotent routes use the ``GET`` method while non-idempotent routes use ``POST``.

Base Item API endpoint:
    * ``/api/item/`` when the response contains zero or one :py:class:`models.Item`
    * ``/api/items/`` when the response contains two or more :py:class:`models.Item`s
"""
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

    :return: ``200`` on success with :py:class:`models.Item`,\n
             ``400`` if item ID was malformed,\n
             ``404`` if item was not found
    """
    return _process_get_request(item_id)


@api_item_blueprint.route('/api/item/get', methods=['GET', 'POST'])
def api_item_get_dynamic():
    """
    Get a single inventory item by item ID. Route URL is mutable by item ID (dynamic). ::

        GET /api/item/get?item_id=<item_id>
        POST /api/item/get [<item_id>]

    :return: ``200`` on success with the desired :py:class:`models.Item`,\n
             ``400`` if item ID was not found,\n
             ``400`` if item ID was malformed,\n
             ``404`` if item was not found
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
    Create an inventory item with provided attributes. ::

        POST /api/item/create [*<item_attributes>, <api_key>]

    All item attributes are required as listed:

        * ``mfg_part_number: str``
        * ``quantity: int``
        * ``description: str``
        * ``digikey_part_number: str``
        * ``mouser_part_number: str``
        * ``jlcpcb_part_number: str``

    Item ID will be generated programmatically and returned in the success model.

    Requires authentication scope :py:attr:`auth.Scope.ITEM_CREATE`

    :return: ``200`` on success with the created :py:class:`models.Item`,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if user was not found,\n
             ``404`` if any item parameter was malformed,\n
             ``500`` if any other error while authenticating
    """
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
    cursor.execute(f'INSERT INTO {common.ITEMS_TABLE_NAME} VALUES (?)', (item.to_insert_str(),))
    conn.commit()
    return item.to_response()


@api_item_blueprint.route('/api/item/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_UPDATE)
def api_item_update():
    """
    Update one or more attributes on a single inventory item, identified by item ID. ::

        POST /api/item/update [*<item_attributes>, <item_id>, <api_key>]

    Available attributes to update/modify are:

        * ``mfg_part_number: str``
        * ``quantity: int``
        * ``description: str``
        * ``digikey_part_number: str``
        * ``mouser_part_number: str``
        * ``jlcpcb_part_number: str``

    At least one attribute must be updated, though updating more than one is supported.
    Item IDs and creation user/time cannot be updated. Items must be removed and re-created to change these attributes.

    Requires authentication scope :py:attr:`auth.Scope.ITEM_UPDATE`

    :return: ``200`` on success with the updated :py:class:`models.Item`,\n
             ``400`` if no attributes to update were provided,\n
             ``400`` if item ID was malformed,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if item was not found before updating,\n
             ``404`` if the item was not found after updating,\n
             ``500`` if any other error while authenticating
    """
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

    updated_item_res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME} WHERE item_id=?', (item_id,))
    db_updated_item = updated_item_res.fetchone()
    if db_updated_item is None or len(db_updated_item) == 0:
        flask.abort(404, 'Item did not exist after updating')
    updated_item = models.Item(*db_updated_item)
    return updated_item.to_response()


@api_item_blueprint.route('/api/item/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_REMOVE)
def api_item_remove():
    """
    Remove a single inventory item, identified by item ID. ::

        POST /api/item/remove [<item_id>, <api_key>]

    Requires authentication scope :py:attr:`auth.Scope.ITEM_REMOVE`

    :return: ``200`` on success with the removed :py:class:`models.Item`,\n
             ``400`` if item ID was malformed,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if item was not found,\n
             ``500`` if more than one item was found,\n
             ``500`` if any other error while authenticating
    """
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    item_id = form.get('item_id')
    item_res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME} WHERE item_id=?', (item_id,))
    db_item = item_res.fetchall()
    if db_item is None or len(db_item) == 0 or db_item == 0:
        flask.abort(404, 'Item does not exist')
    if len(db_item) != 1:
        flask.abort(500, f'Expected 1 item with matching item ID, got {len(db_item)}')

    cursor.execute(f'DELETE FROM {common.ITEMS_TABLE_NAME} WHERE item_id=?', (item_id,))
    conn.commit()

    deleted_item = models.Item(*db_item)
    return deleted_item.to_response()


@api_item_blueprint.route('/api/items/list', methods=['GET', 'POST'])
def api_items_list():
    """
    List one or more inventory items with optional ordering. ::

        GET /api/item/list?sortby={*<item_attributes>}&direction={ASC,DESC}&limit=<limit>
        POST /api/item/list [sortby={*<item_attributes>}, <direction={ASC,DESC}>, <limit>]

    Available (all optional) parameters:

        * ``sortby``: the name of any attribute in :py:class:`models.Item` (as a string).\
                Results will then be sorted based based on this column. No sorting by default.
        * ``direction``: either ``ASC`` to sort the results in ascending order\
                or ``DESC`` to sort the results in descending order. ``ASC`` by default.
        * ``limit``: the (maximum) number of returned items. :py:data:`common.RET_ITEMS_LIMIT` at maximum (default).

    :return: ``200`` on success with a list of :py:class:`models.Item`s,\n
             ``400`` if any sorting attributes were malformed,\n
             ``400`` if ``sortby`` is present and is not a valid sort key,\n
             ``400`` if ``direction`` is not ``ASC`` or ``DESC``,\n
             ``400`` if ``limit`` is not an integer (digit string)
    """
    # TODO make this not display EVERYTHING or at least do some rate limiting
    # TODO add a search functionality option to this too
    conn = common.get_db_connection()
    cursor = conn.cursor()

    # If GET use query parameters, else if POST use form data
    request_parameters = flask.request.form if flask.request.method == 'POST' else flask.request.args

    limit = common.RET_ITEMS_LIMIT
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

        query = f'SELECT * FROM {common.ITEMS_TABLE_NAME} ORDER BY {sortby} {direction} LIMIT {limit}'
        res = cursor.execute(query)
    else:
        res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME} LIMIT {limit}')
    db_items = res.fetchall()

    items = [models.Item(*db_item) for db_item in db_items]
    return common.create_response(200, [item.to_dict() for item in items])
