import auth
import common
import db
import flask
import models

api_reservation_blueprint = flask.Blueprint('api_reservation', __name__)


@api_reservation_blueprint.route('/api/reservation/get', methods=['POST'])
def api_reservation_get():
    form = common.FlaskPOSTForm(flask.request.form)
    return db.get(
        id_=form.get('reservation_id'),
        id_name='reservation_id',
        table_name=common.RESERVATIONS_TABLE_NAME,
        entity_type=models.Reservation,
    )


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
    return db.update(
        id_name='reservation_id',
        table_name=common.RESERVATIONS_TABLE_NAME,
        blank_entity=models.BLANK_RESERVATION,
        immutable_props=[
            'reservation_id',
            'user_id',
            'item_id',
        ],
    )


@api_reservation_blueprint.route('/api/reservation/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_REMOVE)
def api_reservation_remove():
    # TODO documentation
    return db.remove(
        id_name='reservation_id',
        table_name=common.RESERVATIONS_TABLE_NAME,
        entity_type=models.Reservation,
    )


@api_reservation_blueprint.route('/api/reservations/list', methods=['GET', 'POST'])
@auth.route_requires_auth(auth.Scope.RESERVATIONS_LIST)
def api_reservations_list():
    # TODO documentation
    return db.list_(
        table_name=common.RESERVATIONS_TABLE_NAME,
        entity_type=models.Reservation,
    )
