import auth
import common
import db
import flask
import models

api_reservation_blueprint = flask.Blueprint('api_reservation', __name__)


@api_reservation_blueprint.route('/api/reservation/get', methods=['POST'])
def api_reservation_get():
    form = common.FlaskPOSTForm(flask.request.form)
    return db.get(id_=form.get(models.Reservation.id_name), entity_type=models.Reservation)


@api_reservation_blueprint.route('/api/reservation/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_CREATE)
def api_reservation_create():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    user_query = f'SELECT {models.User.id_name} FROM {common.USERS_TABLE_NAME} WHERE {auth.API_KEY_NAME}=?'
    user_res = cursor.execute(user_query, (form.get(auth.API_KEY_NAME),))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user_id = db_user[0]

    item_id = form.get(models.Item.id_name)
    item_res = cursor.execute(f'SELECT * FROM {common.ITEMS_TABLE_NAME} WHERE {models.Item.id_name}=?')
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
        blank_entity=models.BLANK_RESERVATION,
        immutable_props=[
            models.Reservation.id_name,
            models.User.id_name,
            models.Item.id_name,
        ],
    )


@api_reservation_blueprint.route('/api/reservation/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_REMOVE)
def api_reservation_remove():
    # TODO documentation
    return db.remove(entity_type=models.Reservation)


@api_reservation_blueprint.route('/api/reservations/list', methods=['GET', 'POST'])
def api_reservations_list():
    # TODO documentation
    return db.list_(entity_type=models.Reservation)
