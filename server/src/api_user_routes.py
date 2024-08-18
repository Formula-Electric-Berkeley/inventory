import secrets
import uuid

import auth
import common
import flask
import models


api_user_blueprint = flask.Blueprint('api_user', __name__)


@api_user_blueprint.route('/api/user/get/<user_id>', methods=['GET'])
def api_user_get(user_id):
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_CREATE, form.get('api_key'))

    if common.is_dirty(user_id):
        flask.abort(400, 'User ID was malformed')
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f"SELECT * FROM users WHERE item_id='{user_id}'")
    db_user = res.fetchone()
    user = models.User(*db_user)
    return user.to_response()


@api_user_blueprint.route('/api/user/create', methods=['POST'])
def api_user_create():
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_CREATE, form.get('api_key'))

    user = models.User(
        user_id=uuid.uuid4().hex,
        api_key=secrets.token_hex(),
        name=form.get('name'),
        authmask=form.get('authmask'),
    )
    conn = common.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO users VALUES ({user.to_insert_str()})')
    conn.commit()
    return user.to_response()


@api_user_blueprint.route('/api/user/update', methods=['POST'])
def api_user_update():
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_UPDATE, form.get('api_key'))
    # TODO implement
    pass


@api_user_blueprint.route('/api/user/remove', methods=['POST'])
def api_user_remove():
    form = common.FlaskPOSTForm(flask.request.form)
    auth.require_auth(auth.Scope.USER_REMOVE, form.get('api_key'))
    # TODO implement
    pass
