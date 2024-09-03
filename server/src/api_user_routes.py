import secrets

import auth
import common
import db
import flask
import models
from identifier import Identifier

api_user_blueprint = flask.Blueprint('api_user', __name__)


@api_user_blueprint.route('/api/user/get', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_GET)
def api_user_get():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    return db.get(id_=form.get(models.User.id_name), entity_type=models.User)


@api_user_blueprint.route('/api/user/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_CREATE)
def api_user_create():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    existing_user_res = cursor.execute(f'SELECT * FROM {models.User.table_name} WHERE name=?', (form.get('name'),))
    existing_users = existing_user_res.fetchall()
    if len(existing_users) != 0:
        flask.abort(400, 'A user already exists with that name')

    user = models.User(
        user_id=Identifier(length=models.User.id_length),
        api_key=secrets.token_hex(),
        name=form.get('name'),
        authmask=form.get('authmask'),
    )
    db.create_entity(conn, cursor, user)
    return user.to_response()


@api_user_blueprint.route('/api/user/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_UPDATE)
def api_user_update():
    # TODO documentation
    return db.update(
        entity_type=models.User,
        immutable_props=[
            models.User.id_name,
            auth.API_KEY_NAME,
            'name',
        ],
    )


@api_user_blueprint.route('/api/user/delete', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_DELETE)
def api_user_delete():
    # TODO documentation
    return db.delete(entity_type=models.User)
