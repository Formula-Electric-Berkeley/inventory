"""
The Box API can create, get, update, remove, and list boxes which store inventory items.

Note that inventory "boxes" store item entries, each of which represents a real "container".
Containers are typically bags, but may be boxes (not inventory boxes though) in some cases.

All routes except item retrieval require authentication, which is handled by :py:mod:`auth`.
Idempotent routes use the ``GET`` method while non-idempotent routes use ``POST``.

Base Box API endpoint:
    * ``/api/box/`` when the response contains zero or one :py:class:`models.Box`
    * ``/api/boxes/`` when the response contains two or more :py:class:`models.Box` es
"""
import auth
import common
import db
import flask
import models
from identifier import Identifier

api_box_blueprint = flask.Blueprint('api_box', __name__)


@api_box_blueprint.route('/api/box/get', methods=['POST'])
def api_box_get():
    """
    Get a single inventory box by box ID. ::

        POST /api/box/get [<box_id>]

    :return: ``200`` on success with the desired :py:class:`models.Box`,\n
             ``400`` if box ID was not found,\n
             ``400`` if box ID was malformed,\n
             ``404`` if box was not found, \n
             ``500`` if box ID was not the expected length
    """
    form = common.FlaskPOSTForm(flask.request.form)
    return db.get(id_=form.get(models.Box.id_name), entity_type=models.Box)


@api_box_blueprint.route('/api/box/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.BOX_CREATE)
def api_box_create():
    """
    Create an inventory box with provided name attribute. ::

        POST /api/box/create [<name>, <api_key>]

    Box ID will be generated programmatically and returned in the success model.

    :py:class:`models.Box` contains a variety of attributes, however the only
    user-mutable attribute is the box name.

    Requires authentication scope :py:attr:`auth.Scope.BOX_CREATE`

    :return: ``200`` on success with the created :py:class:`models.Box`,\n
             ``400`` if a box with the desired name already exists, \n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if user was not found,\n
             ``404`` if name was malformed,\n
             ``500`` if any other error while authenticating
    """
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    desired_name = form.get('name')
    box_res = cursor.execute(f'SELECT * FROM {models.Box.table_name} WHERE name=?', (desired_name,))
    db_box = box_res.fetchone()
    if db_box is not None:
        flask.abort(400, f'Box with name {desired_name} already exists')

    box = models.Box(
        box_id=Identifier(length=models.Box.id_length),
        name=desired_name,
    )

    db.create_entity(conn, cursor, box)
    return box.to_response()


@api_box_blueprint.route('/api/box/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.BOX_UPDATE)
def api_box_update():
    """
    Update one or more attributes on a single inventory box, identified by box ID. ::

        POST /api/box/update [<name>, <box_id>, <api_key>]

    :py:class:`models.Box` contains a variety of attributes, however the only
    user-mutable attribute is the box name. All other attributes cannot be updated.

    Requires authentication scope :py:attr:`auth.Scope.BOX_UPDATE`

    :return: ``200`` on success with the updated :py:class:`models.Box`,\n
             ``400`` if no attributes to update were provided,\n
             ``400`` if box ID was malformed,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if box was not found before updating,\n
             ``404`` if box was not found after updating,\n
             ``500`` if any other error while authenticating
    """
    return db.update(
        entity_type=models.Box,
        immutable_props=[
            models.Box.id_name,
            models.User.id_name,
            models.Item.id_name,
        ],
    )


@api_box_blueprint.route('/api/box/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.BOX_REMOVE)
def api_box_remove():
    """
    Remove a single inventory box, identified by box ID. ::

        POST /api/box/remove [<box_id>, <api_key>]

    Requires authentication scope :py:attr:`auth.Scope.BOX_REMOVE`

    :return: ``200`` on success with the removed :py:class:`models.Box`,\n
             ``400`` if box ID was malformed,\n
             ``400`` if API key was malformed,\n
             ``401`` if API key was invalid,\n
             ``403`` if user does not have required scope,\n
             ``404`` if box was not found,\n
             ``500`` if more than one box was found,\n
             ``500`` if any other error while authenticating
    """
    return db.remove(entity_type=models.Box)


@api_box_blueprint.route('/api/boxes/list', methods=['GET', 'POST'])
def api_boxes_list():
    """
    List one or more inventory boxes with optional ordering. ::

        GET /api/boxes/list?sortby={*<box_attributes>}&direction={ASC,DESC}&limit=<limit>&offset=<offset>
        POST /api/boxes/list [sortby={*<box_attributes>}, <direction={ASC,DESC}>, <limit>, <offset>]

    Available (all optional) parameters:

        * ``sortby``: the name of any attribute in :py:class:`models.Box` (as a string).\
                Results will then be sorted based based on this column. No sorting by default.
        * ``direction``: either ``ASC`` to sort the results in ascending order\
                or ``DESC`` to sort the results in descending order. ``ASC`` by default.
        * ``limit``: the (maximum) number of returned boxes. :py:data:`common.RET_ENTITIES_DEF_LIMIT` default,\
                up to a maximum of :py:data:`common.RET_ENTITIES_MAX_LIMIT`.
        * ``offset``: the index offset within the database to respond with. 0 by default.

    :return: ``200`` on success with a list of :py:class:`models.Box` es,\n
             ``400`` if any sorting attributes were malformed,\n
             ``400`` if ``sortby`` is present and is not a valid sort key,\n
             ``400`` if ``direction`` is not ``ASC`` or ``DESC``,\n
             ``400`` if ``limit`` is not an integer (digit string), \n
             ``400`` if ``offset`` is not an integer (digit string)
    """
    return db.list_(entity_type=models.Box)
