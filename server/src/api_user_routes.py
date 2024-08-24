import secrets

import auth
import common
import flask
import models


api_user_blueprint = flask.Blueprint('api_user', __name__)


@api_user_blueprint.route('/api/user/get/<user_id>', methods=['GET'])
@auth.route_requires_auth(auth.Scope.USER_GET)
def api_user_get(user_id):
    # TODO documentation
    # TODO other methods? (opt)
    if common.is_dirty(user_id):
        flask.abort(400, 'User ID was malformed')
    conn = common.get_db_connection()
    cursor = conn.cursor()
    res = cursor.execute(f'SELECT * FROM {common.USERS_TABLE_NAME} WHERE item_id=?', (user_id,))
    db_user = res.fetchone()
    if db_user is None or len(db_user) == 0:
        flask.abort(404, 'User does not exist')
    user = models.User(*db_user)
    return user.to_response()


@api_user_blueprint.route('/api/user/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_CREATE)
def api_user_create():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    existing_user_res = cursor.execute(f'SELECT * FROM {common.USERS_TABLE_NAME} WHERE name=?', (form.get('name'),))
    existing_users = existing_user_res.fetchall()
    if len(existing_users) != 0:
        flask.abort(400, 'A user already exists with that name')

    user = models.User(
        user_id=common.create_random_id(),
        api_key=secrets.token_hex(),
        name=form.get('name'),
        authmask=form.get('authmask'),
    )

    cursor.execute(f'INSERT INTO {common.USERS_TABLE_NAME} VALUES (?)', (user.to_insert_str(),))
    conn.commit()
    return user.to_response()


@api_user_blueprint.route('/api/user/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_UPDATE)
def api_user_update():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    # Check that user exists in DB before modifying
    user_id = form.get('user_id')
    user_res = cursor.execute(f'SELECT 1 FROM {common.USERS_TABLE_NAME} WHERE user_id=? LIMIT 1', (user_id,))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0 or db_user == 0:
        flask.abort(404, 'User does not exist')

    # TODO have a better solution for mutability
    user_properties = models.BLANK_USER.to_dict()
    user_properties.pop('user_id')
    user_properties.pop('api_key')
    user_properties.pop('name')

    properties_to_update = {k: v for k, v in user_properties.items() if k in form.form}
    if len(properties_to_update) <= 0:
        flask.abort(400, 'No attributes to be updated were provided')

    for key, value in properties_to_update.items():
        query_params = (form.get(key, type(value)), user_id)
        cursor.execute(f'UPDATE {common.USERS_TABLE_NAME} SET {key}=? WHERE user_id=?', query_params)
    conn.commit()

    return common.create_response(200, {})


@api_user_blueprint.route('/api/user/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_REMOVE)
def api_user_remove():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)

    conn = common.get_db_connection()
    cursor = conn.cursor()

    user_id = form.get('user_id')
    user_res = cursor.execute(f'SELECT 1 FROM {common.USERS_TABLE_NAME} WHERE user_id=? LIMIT 1', (user_id,))
    db_user = user_res.fetchone()
    if db_user is None or len(db_user) == 0 or db_user == 0:
        flask.abort(404, 'User does not exist')

    cursor.execute(f'DELETE FROM {common.USERS_TABLE_NAME} WHERE user_id=?', (user_id,))
    conn.commit()

    return common.create_response(200, {})
