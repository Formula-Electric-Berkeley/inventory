import json
import secrets
import uuid

import flask

import auth
import models
import common


api_blueprint = flask.Blueprint('api', __name__)


@api_blueprint.route('/api/item/get/<item_id>', methods=['GET'])
def api_item_get(item_id):
    if common.is_dirty(item_id):
        flask.abort(400)
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f"SELECT * FROM items WHERE item_id='{item_id}'")
    db_item = res.fetchone()
    if db_item is None or len(db_item) == 0:
        flask.abort(404)
    item = models.Item(*db_item)
    cursor.close()
    conn.close()
    return item.to_dict()


@api_blueprint.route('/api/item/create', methods=['POST'])
def api_item_create():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.ITEM_CREATE, form.get('api_key'))

    conn = common.get_db_connection_connection()
    cursor = conn.cursor()

    user_res = cursor.execute(f"SELECT user_id FROM users WHERE api_key='{form.get('api_key')}'")
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404)
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
    cursor.close()
    conn.commit()
    conn.close()
    return item.to_dict()


@api_blueprint.route('/api/item/update', methods=['POST'])
def api_item_update():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.ITEM_UPDATE, form.get('api_key'))
    # TODO implement
    pass


@api_blueprint.route('/api/item/remove', methods=['POST'])
def api_item_remove():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.ITEM_REMOVE, form.get('api_key'))
    # TODO implement
    pass


@api_blueprint.route('/api/reservation/get/<item_id>', methods=['GET'])
def api_reservation_get(item_id):
    if common.is_dirty(item_id):
        flask.abort(400)
    # TODO implement
    pass


@api_blueprint.route('/api/reservation/create', methods=['POST'])
def api_reservation_create():
    form = common.FlaskForm(flask.request.form)
    api_key = form.get('api_key')
    auth.require_auth(auth.Scope.RESERVATION_CREATE, api_key)

    item_id = form.get('item_id')
    quantity = int(form.get('quantity'))

    conn = common.get_db_connection()
    cursor = conn.cursor()
    user_res = cursor.execute(f"SELECT user_id FROM users WHERE api_key='{api_key}'")
    db_userid = user_res.fetchone()
    if db_userid is None or len(db_userid) != 1:
        flask.abort(404)
    user_id = db_userid[0]

    item_res = cursor.execute(f"SELECT reserved FROM items WHERE item_id='{item_id}'")
    db_item = item_res.fetchone()
    if db_item is None or len(db_item) != 1:
        flask.abort(404)

    reserved = eval(db_item[0])
    if user_id in reserved:
        reserved[user_id] += quantity
    else:
        reserved[user_id] = quantity

    cursor.execute(f"UPDATE items SET reserved='{json.dumps(reserved)}' WHERE item_id='{item_id}'")
    conn.commit()
    cursor.close()
    conn.close()
    return reserved


@api_blueprint.route('/api/reservation/update', methods=['POST'])
def api_reservation_update():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.RESERVATION_UPDATE, form.get('api_key'))
    # TODO implement
    pass


@api_blueprint.route('/api/reservation/remove', methods=['POST'])
def api_reservation_remove():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.RESERVATION_REMOVE, form.get('api_key'))
    # TODO implement
    pass


@api_blueprint.route('/api/items/list', methods=['GET'])
def api_items_list():
    res = common.get_db_connection().cursor().execute("SELECT * FROM items")
    db_items = res.fetchall()
    items = [models.Item(*db_item) for db_item in db_items]
    return [item.to_dict() for item in items]


@api_blueprint.route('/api/items/bulkadd', methods=['POST'])
def api_items_bulkadd():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.ITEMS_BULKADD, form.get('api_key'))
    # TODO implement
    pass


@api_blueprint.route('/api/user/get/<user_id>', methods=['GET'])
def api_user_get(user_id):
    if common.is_dirty(user_id):
        flask.abort(400)
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f"SELECT * FROM users WHERE item_id='{user_id}'")
    db_user = res.fetchone()
    user = models.User(*db_user)
    cursor.close()
    conn.close()
    return user.to_dict()


@api_blueprint.route('/api/user/create', methods=['POST'])
def api_user_create():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_CREATE, form.get('api_key'))

    user = models.User(
        user_id=uuid.uuid4().hex,
        api_key=secrets.token_hex(),
        name=form.get('name'),
        authmask=form.get('authmask')
    )
    conn = common.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users VALUES ({user.to_insert_str()})")
    conn.commit()
    cursor.close()
    conn.close()
    return user.to_dict()


@api_blueprint.route('/api/user/update', methods=['POST'])
def api_user_update():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_UPDATE, form.get('api_key'))
    # TODO implement
    pass


@api_blueprint.route('/api/user/remove', methods=['POST'])
def api_user_remove():
    form = common.FlaskForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_REMOVE, form.get('api_key'))
    # TODO implement
    pass
