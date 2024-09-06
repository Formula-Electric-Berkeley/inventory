"""
The Item API can create, get, update, delete, and list inventory item(s).

All routes except item retrieval require authentication, which is handled by :py:mod:`auth`.
Idempotent routes use the ``GET`` method while non-idempotent routes use ``POST``.

Base Item API endpoint:
    * ``/api/item/`` when the response contains zero or one :py:class:`models.Item`
    * ``/api/items/`` when the response contains two or more :py:class:`models.Item` s
"""
import auth
import common
import db
import flask
import models
from identifier import Identifier

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
    return db.get(entity_type=models.Item, id_=item_id)


@api_item_blueprint.route('/api/item/get', methods=['GET'])
def api_item_get_dynamic():
    """
    Get a single inventory item by item ID. Route URL is mutable by item ID (dynamic). ::

        GET /api/item/get?item_id=<item_id>

    :return: ``200`` on success with the desired :py:class:`models.Item`,\n
             ``400`` if item ID was not found,\n
             ``400`` if item ID was malformed,\n
             ``404`` if item was not found, \n
             ``500`` if item ID was not the expected length
    """
    return db.get(entity_type=models.Item)


@api_item_blueprint.route('/api/item/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_CREATE)
def api_item_create():
    """
    Create an inventory item with provided attributes. ::

        POST /api/item/create [*<item_attributes>, <api_key>]

    All item attributes are required as listed:

        * ``box_id:`` :py:class:`identifier.Identifier`
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
    conn, cursor = common.get_db_connection()

    user_id = db.get_request_user_id(cursor, form)
    box_id = form.get(models.Box.id_name)

    item = models.Item(
        item_id=Identifier(length=models.Item.id_length),
        box_id=Identifier(length=models.Box.id_length, id_=box_id),
        mfg_part_number=form.get('mfg_part_number'),
        quantity=form.get('quantity', int),
        description=form.get('description'),
        digikey_part_number=form.get('digikey_part_number'),
        mouser_part_number=form.get('mouser_part_number'),
        jlcpcb_part_number=form.get('jlcpcb_part_number'),
        created_by=Identifier(length=models.User.id_length, id_=user_id),
        created_epoch_millis=common.time_ms(),
    )

    db.create_entity(conn, cursor, item)
    return item.to_response()


@api_item_blueprint.route('/api/item/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_UPDATE)
def api_item_update():
    """
    Update one or more attributes on a single inventory item, identified by item ID. ::

        POST /api/item/update [*<item_attributes>, <item_id>, <api_key>]

    Available attributes to update/modify are:

        * ``box_id:`` :py:class:`identifier.Identifier`
        * ``mfg_part_number: str``
        * ``quantity: int``
        * ``description: str``
        * ``digikey_part_number: str``
        * ``mouser_part_number: str``
        * ``jlcpcb_part_number: str``

    At least one attribute must be updated, though updating more than one is supported.
    Item IDs and creation user/time cannot be updated. Items must be deleted and re-created to change these attributes.

    Requires authentication scope :py:attr:`auth.Scope.ITEM_UPDATE`

    :return: ``200`` on success with the updated :py:class:`models.Item`,\n
             ``400`` if no attributes to update were provided,\n
             ``400`` if item ID was malformed,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if item was not found before updating,\n
             ``404`` if item was not found after updating,\n
             ``500`` if any other error while authenticating
    """
    return db.update(
        entity_type=models.Item,
        immutable_props=[
            models.Item.id_name,
            'created_by',
            'created_epoch_millis',
        ],
    )


@api_item_blueprint.route('/api/item/delete', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_DELETE)
def api_item_delete():
    """
    Delete a single inventory item, identified by item ID. ::

        POST /api/item/delete [<item_id>, <api_key>]

    Requires authentication scope :py:attr:`auth.Scope.ITEM_DELETE`

    :return: ``200`` on success with the deleted :py:class:`models.Item`,\n
             ``400`` if item ID was malformed,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if item was not found,\n
             ``500`` if more than one item was found,\n
             ``500`` if any other error while authenticating
    """
    return db.delete(entity_type=models.Item)


@api_item_blueprint.route('/api/items/list', methods=['GET'])
def api_items_list():
    """
    List one or more inventory items with optional ordering. ::

        GET /api/items/list?sortby={*<item_attributes>}&direction={ASC,DESC}&limit=<limit>&offset=<offset>

    Available (all optional) parameters:

        * ``sortby``: the name of any attribute in :py:class:`models.Item` (as a string).\
                Results will then be sorted based based on this column. No sorting by default.
        * ``direction``: either ``ASC`` to sort the results in ascending order\
                or ``DESC`` to sort the results in descending order. ``ASC`` by default.
        * ``limit``: the (maximum) number of returned items. :py:data:`common.RET_ENTITIES_DEF_LIMIT` default,\
                up to a maximum of :py:data:`common.RET_ENTITIES_MAX_LIMIT`.
        * ``offset``: the index offset within the database to respond with. 0 by default.

    :return: ``200`` on success with a list of :py:class:`models.Item` s,\n
             ``400`` if any sorting attributes were malformed,\n
             ``400`` if ``sortby`` is present and is not a valid sort key,\n
             ``400`` if ``direction`` is not ``ASC`` or ``DESC``,\n
             ``400`` if ``limit`` is not an integer (digit string), \n
             ``400`` if ``offset`` is not an integer (digit string)
    """
    return db.list_(entity_type=models.Item)
