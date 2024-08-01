import flask

import api_routes
import models


root_blueprint = flask.Blueprint('root', __name__)


@root_blueprint.route('/', methods=['GET'])
def root():
    items = [models.Item(*item.values()) for item in api_routes.api_items_list()]
    return flask.render_template('view_multiple.html', items=items)


@root_blueprint.route('/<item_id>', methods=['GET'])
def root_item_id(item_id: str):
    api_resp = api_routes.api_item_get(item_id)
    item = models.Item(*api_resp.values())
    return flask.render_template('view_single.html', item=item, view_url=flask.request.base_url)


@root_blueprint.route('/ingress', methods=['GET'])
def root_ingress():
    pass


@root_blueprint.route('/egress', methods=['GET'])
def root_egress():
    pass


@root_blueprint.route('/label', methods=['GET'])
def root_label():
    pass
