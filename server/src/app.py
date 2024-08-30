import inspect
from typing import Type

import common
import dotenv
import flask
import models
from api_box_routes import api_box_blueprint
from api_item_routes import api_item_blueprint
from api_reservation_routes import api_reservation_blueprint
from api_user_routes import api_user_blueprint
from werkzeug.exceptions import HTTPException


def _create_table(entity_type: Type[models.Model]):
    model_keys = inspect.signature(entity_type.__init__).parameters.items()
    table_keys = ', '.join([f'{k} {"INTEGER" if isinstance(v, int) else "TEXT"}' for k, v in model_keys])
    conn, cursor = common.get_db_connection()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {entity_type.table_name}({table_keys})').close()


dotenv.load_dotenv()
app = flask.Flask(__name__)

with app.app_context():
    _create_table(models.Item)
    _create_table(models.User)
    _create_table(models.Reservation)
    _create_table(models.Box)

app.register_blueprint(api_item_blueprint)
app.register_blueprint(api_user_blueprint)
app.register_blueprint(api_reservation_blueprint)
app.register_blueprint(api_box_blueprint)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # Start with the correct headers and status code from the error
    response = e.get_response()
    # Replace the body with JSON
    response.data = flask.json.dumps(
        common.create_response(
            e.code,
            {
                'name': e.name,
                'description': e.description,
            },
        ),
        indent=4,
    )
    response.content_type = 'application/json'
    return response
