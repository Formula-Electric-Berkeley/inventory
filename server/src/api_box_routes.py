import auth
import common
import db
import flask
import models
from identifier import Identifier

api_box_blueprint = flask.Blueprint('api_box', __name__)


@api_box_blueprint.route('/api/box/get', methods=['POST'])
def api_box_get():
    form = common.FlaskPOSTForm(flask.request.form)
    return db.get(id_=form.get(models.Box.id_name), entity_type=models.Box)


@api_box_blueprint.route('/api/box/create', methods=['POST'])
@auth.route_requires_auth(auth.Scope.BOX_CREATE)
def api_box_create():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    desired_name = form.get('name')
    box_res = cursor.execute(f'SELECT * FROM {models.Box.table_name} WHERE name=?', (desired_name,))
    db_box = box_res.fetchone()
    if db_box is not None:
        flask.abort(400, f'Box with name {desired_name} already exists')

    box = models.Box(
        box_id=Identifier(length=models.Box.id_length),
        name=desired_name,
    )

    db.create_entity(conn, cursor, box)
    return box.to_response()


@api_box_blueprint.route('/api/box/update', methods=['POST'])
@auth.route_requires_auth(auth.Scope.BOX_UPDATE)
def api_box_update():
    return db.update(
        entity_type=models.Box,
        immutable_props=[
            models.Box.id_name,
            models.User.id_name,
            models.Item.id_name,
        ],
    )


@api_box_blueprint.route('/api/box/remove', methods=['POST'])
@auth.route_requires_auth(auth.Scope.BOX_REMOVE)
def api_box_remove():
    # TODO documentation
    return db.remove(entity_type=models.Box)


@api_box_blueprint.route('/api/boxes/list', methods=['GET', 'POST'])
def api_boxes_list():
    # TODO documentation
    return db.list_(entity_type=models.Box)
