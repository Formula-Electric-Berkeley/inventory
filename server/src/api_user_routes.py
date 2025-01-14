import secrets

import auth
import common
import db
import firebase_admin
import flask
import models
from auth import Scope
from firebase_admin import auth as fauth
from firebase_admin import credentials
from identifier import Identifier


DEFAULT_AUTHMASK = Scope.ITEM_GET | Scope.ITEM_CREATE | Scope.ITEM_UPDATE | Scope.ITEMS_LIST \
    | Scope.RESERVATION_GET | Scope.RESERVATION_CREATE | Scope.RESERVATION_UPDATE \
    | Scope.RESERVATION_DELETE | Scope.RESERVATIONS_LIST \
    | Scope.USER_GET \
    | Scope.BOX_GET | Scope.BOX_UPDATE | Scope.BOXES_LIST | Scope.THUMBNAIL_GET | Scope.THUMBNAIL_UPLOAD

api_user_blueprint = flask.Blueprint('api_user', __name__)

cred = credentials.Certificate('../inventory-a7bb6-firebase-adminsdk-ikk5m-492b597eea.json')
firebase_admin.initialize_app(cred)


def create_user(user_id: Identifier, name: str, authmask: int) -> models.User:
    conn, cursor = common.get_db_connection()
    existing_user_res = cursor.execute(f'SELECT * FROM {models.User.table_name} WHERE name=?', (name,))
    existing_users = existing_user_res.fetchall()

    if len(existing_users) != 0:
        flask.abort(400, 'A user already exists with that name')

    user = models.User(
        user_id=user_id,
        api_key=secrets.token_hex(),
        name=name,
        authmask=authmask,
    )
    db.create_entity(conn, cursor, user)
    return user


@api_user_blueprint.route('/api/user/google_auth', methods=['POST'])
def api_google_auth_user():
    # TODO documentation
    token = flask.request.json.get('token')
    name = flask.request.json.get('name')
    try:
        decoded_token = fauth.verify_id_token(token)
        user_id = decoded_token['uid']
        if not db.get_user_id_exists(user_id):
            create_user(user_id, name, DEFAULT_AUTHMASK)
        return flask.jsonify({'name': name, 'id': user_id})
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 401


@api_user_blueprint.route('/api/user/get', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_GET)
def api_user_get():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    return db.get(entity_type=models.User, id_=form.get(models.User.id_name))


@api_user_blueprint.route('/api/user/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.USER_CREATE)
def api_user_create():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    return create_user(
        Identifier(length=models.User.id_length),
        form.get('name'),
        form.get('authmask'),
    ).to_response()


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
