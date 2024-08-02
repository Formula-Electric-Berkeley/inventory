import flask

import auth
import common


api_reservation_blueprint = flask.Blueprint('api/reservation', __name__)


@api_reservation_blueprint.route('/api/reservation/get/<item_id>', methods=['GET'])
def api_reservation_get(item_id):
    if common.is_dirty(item_id):
        flask.abort(400)
    # TODO implement
    pass


@api_reservation_blueprint.route('/api/reservation/create', methods=['POST'])
def api_reservation_create():
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.RESERVATION_CREATE, form.get('api_key'))
    # TODO implement
    pass


@api_reservation_blueprint.route('/api/reservation/update', methods=['POST'])
def api_reservation_update():
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.RESERVATION_UPDATE, form.get('api_key'))
    # TODO implement
    pass


@api_reservation_blueprint.route('/api/reservation/remove', methods=['POST'])
def api_reservation_remove():
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.RESERVATION_REMOVE, form.get('api_key'))
    # TODO implement
    pass