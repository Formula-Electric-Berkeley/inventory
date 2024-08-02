import uuid

import flask

import auth
import models
import common


api_item_blueprint = flask.Blueprint('api/item', __name__)


@api_item_blueprint.route('/api/item/get/<item_id>', methods=['GET'])
def api_item_get(item_id):
    # Do not require authentication for item retrieve if item ID is known
    if common.is_dirty(item_id):
        flask.abort(400, "Item ID was malformed")
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f"SELECT * FROM items WHERE item_id='{item_id}'")
    db_item = res.fetchone()
    if db_item is None or len(db_item) == 0:
        flask.abort(404, "Item does not exist")
    item = models.Item(*db_item)
    return item.to_dict()


@api_item_blueprint.route('/api/item/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_CREATE)
def api_item_create():
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    user_res = cursor.execute(f"SELECT user_id FROM users WHERE api_key='{form.get('api_key')}'")
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, "Item does not exist")
    user_id = db_user[0]

    item = models.Item(
        item_id=uuid.uuid4().hex[:8],
        mfg_part_number=form.get('mfg_part_number'),
        quantity=form.get('quantity'),
        description=form.get('description'),
        digikey_part_number=form.get('digikey_part_number'),
        mouser_part_number=form.get('mouser_part_number'),
        jlcpcb_part_number=form.get('jlcpcb_part_number'),
        created_by=user_id,
        created_epoch_millis=common.time_ms()
    )
    cursor.execute(f"INSERT INTO items VALUES ({item.to_insert_str()})")
    conn.commit()
    return item.to_dict()


@api_item_blueprint.route('/api/item/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_UPDATE)
def api_item_update():
    # TODO implement
    pass
    return 'hello world'


@api_item_blueprint.route('/api/item/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEM_REMOVE)
def api_item_remove():
    form = common.FlaskPOSTForm(flask.request.form)
    item_id = form.get('item_id')

    conn = common.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM items WHERE item_id='{item_id}'")
    return str()


@api_item_blueprint.route('/api/items/list', methods=['GET'])
def api_items_list():
    # TODO make this not display EVERYTHING or at least do some rate limiting
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM items")
    db_items = res.fetchall()
    items = [models.Item(*db_item) for db_item in db_items]
    return [item.to_dict() for item in items]


@api_item_blueprint.route('/api/items/bulkadd', methods=['POST'])
@auth.route_requires_auth(auth.Scope.ITEMS_BULKADD)
def api_items_bulkadd():
    # TODO implement
    pass
