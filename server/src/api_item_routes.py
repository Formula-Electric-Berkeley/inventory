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
import db
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
    return db.get(id_=item_id, entity_type=models.Item)


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
    if models.Item.id_name not in request_parameters:
        flask.abort(400, 'Item ID was not found')
    return db.get(id_=request_parameters.get(models.Item.id_name), entity_type=models.Item)


@api_item_blueprint.route('/api/item/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_CREATE)
def api_item_create():
    """
    Create an inventory item with provided attributes. ::

        POST /api/item/create [*<item_attributes>, <api_key>]

    All item attributes are required as listed:

        * ``box_id: str``
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

    user_query = f'SELECT {models.User.id_name} FROM {common.USERS_TABLE_NAME} WHERE api_key=?'
    user_res = cursor.execute(user_query, (form.get('api_key'),))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user_id = db_user[0]

    item = models.Item(
        item_id=common.create_random_id(length=8),
        box_id=form.get(models.Box.id_name),
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

        * ``box_id: str``
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
    return db.update(
        blank_entity=models.BLANK_ITEM,
        immutable_props=[
            models.Item.id_name,
            'created_by',
            'created_epoch_millis',
        ],
    )


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
    return db.remove(entity_type=models.Item)


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
    return db.list_(entity_type=models.Item)
