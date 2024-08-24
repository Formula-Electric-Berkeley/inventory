import auth
import common
import flask
import models

api_reservation_blueprint = flask.Blueprint('api_reservation', __name__)


@api_reservation_blueprint.route('/api/reservation/get/<reservation_id>', methods=['GET'])
def api_reservation_get(reservation_id):
    # TODO documentation
    if common.is_dirty(reservation_id):
        flask.abort(400, 'Reservation ID is malformed')
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f'SELECT * FROM {common.RESERVATIONS_TABLE_NAME} WHERE reservation_id=?', (reservation_id,))
    db_reservation = res.fetchone()
    if db_reservation is None or len(db_reservation) == 0:
        flask.abort(404, 'Reservation does not exist')
    reservation = models.Reservation(*db_reservation)
    return reservation.to_response()


@api_reservation_blueprint.route('/api/reservation/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_CREATE)
def api_reservation_create():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    user_res = cursor.execute(f'SELECT user_id FROM {common.USERS_TABLE_NAME} WHERE api_key=?', (form.get('api_key'),))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user_id = db_user[0]

    item_id = form.get('item_id')
    item_res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME} WHERE item_id=?')
    db_item = item_res.fetchone()
    if db_item is None or len(db_item) == 0:
        flask.abort(404, 'Item does not exist')
    item = models.Item(*db_item)

    desired_quantity = form.get('quantity', int)
    if desired_quantity > item.quantity:
        flask.abort(400, f'Insufficient item quantity. Requested {desired_quantity}, had {item.quantity}')

    reservation = models.Reservation(
        reservation_id=common.create_random_id(length=8),
        user_id=user_id,
        item_id=item_id,
        quantity=desired_quantity,
    )
    cursor.execute(f'INSERT INTO {common.RESERVATIONS_TABLE_NAME} VALUES (?)', (reservation.to_insert_str(),))
    conn.commit()
    return reservation.to_response()


@api_reservation_blueprint.route('/api/reservation/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_UPDATE)
def api_reservation_update():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    # Check that item exists in DB before modifying
    reservation_id = form.get('reservation_id')
    reservation_res = cursor.execute(
        f'SELECT 1 FROM {common.RESERVATIONS_TABLE_NAME} WHERE reservation_id=?', (reservation_id,),
    )
    db_reservation = reservation_res.fetchone()
    if db_reservation is None or len(db_reservation) == 0 or db_reservation == 0:
        flask.abort(404, 'Reservation does not exist')

    # TODO have a better solution for mutability
    reservation_properties = models.BLANK_RESERVATION.to_dict()
    reservation_properties.pop('reservation_id')
    reservation_properties.pop('user_id')
    reservation_properties.pop('item_id')

    properties_to_update = {k: v for k, v in reservation_properties.items() if k in form.form}
    if len(properties_to_update) <= 0:
        flask.abort(400, 'No attributes to be updated were provided')

    for key, value in properties_to_update.items():
        query_params = (form.get(key, type(value)), reservation_id)
        cursor.execute(f'UPDATE {common.RESERVATIONS_TABLE_NAME} SET {key}=? WHERE reservation_id=?', query_params)
    conn.commit()

    updated_reservation_res = cursor.execute(
        f'SELECT * FROM {common.RESERVATIONS_TABLE_NAME} WHERE item_id=?', (reservation_id,),
    )
    db_updated_reservation = updated_reservation_res.fetchone()
    if db_updated_reservation is None or len(db_updated_reservation) == 0:
        flask.abort(404, 'Reservation did not exist after updating')
    updated_reservation = models.Reservation(*db_updated_reservation)
    return updated_reservation.to_response()


@api_reservation_blueprint.route('/api/reservation/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_REMOVE)
def api_reservation_remove():
    # TODO documentation
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


@api_reservation_blueprint.route('/api/reservations/list', methods=['GET', 'POST'])
@auth.route_requires_auth(auth.Scope.RESERVATIONS_LIST)
def api_reservations_list():
    # TODO documentation
    # TODO implement
    pass
