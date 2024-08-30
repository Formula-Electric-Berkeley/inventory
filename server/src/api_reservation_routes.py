import auth
import common
import db
import flask
import models
from identifier import Identifier


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
    conn, cursor = common.get_db_connection()

    user_id = db.get_request_user_id(cursor, form)

    item_id = form.get(models.Item.id_name)
    item_res = cursor.execute(f'SELECT * FROM {models.Item.table_name} WHERE {models.Item.id_name}=?', (item_id,))
    db_item = item_res.fetchone()
    if db_item is None or len(db_item) == 0:
        flask.abort(404, 'Item does not exist')
    item = models.Item(*db_item)

    desired_quantity = form.get('quantity', int)
    if desired_quantity > item.quantity:
        flask.abort(400, f'Insufficient item quantity. Requested {desired_quantity}, had {item.quantity}')

    reservation = models.Reservation(
        reservation_id=Identifier(length=models.Reservation.id_length),
        user_id=Identifier(length=models.User.id_length, id_=user_id),
        item_id=Identifier(length=models.Item.id_length, id_=item_id),
        quantity=desired_quantity,
    )
    db.create_entity(conn, cursor, reservation)
    return reservation.to_response()


@api_reservation_blueprint.route('/api/reservation/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.RESERVATION_UPDATE)
def api_reservation_update():
    return db.update(
        entity_type=models.Reservation,
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
