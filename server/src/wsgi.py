from typing import Type

import common
import dotenv
import flask
import models
from api_box_routes import api_box_blueprint
from api_item_routes import api_item_blueprint
from api_reservation_routes import api_reservation_blueprint
from api_thumbnail_routes import api_thumbnail_blueprint
from api_user_routes import api_user_blueprint
from flask_cors import CORS
from werkzeug.exceptions import HTTPException


def _create_table(entity_type: Type[models.Model]):
    """
    Creates a single table in the backing database
    representing a store for a passed model type.

    Assumes an ``INTEGER`` data type if the backing data is of type ``int``,
    otherwise assumes type ``TEXT`` (i.e. ``VARCHAR``).
    """
    model_keys = models.get_model_attributes(entity_type).items()
    table_keys = ', '.join([f'{k} {"INTEGER" if isinstance(v, int) else "TEXT"}' for k, v in model_keys])
    conn, cursor = common.get_db_connection()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {entity_type.table_name}({table_keys})').close()


def _create_tables():
    """
    Creates all tables in the backing database
    representing stores for all model types (:py:class:`models.Box`).
    """
    with app.app_context():
        _create_table(models.Item)
        _create_table(models.User)
        _create_table(models.Reservation)
        _create_table(models.Box)


dotenv.load_dotenv()
app = flask.Flask(__name__)
CORS(app)

_create_tables()

app.register_blueprint(api_item_blueprint)
app.register_blueprint(api_user_blueprint)
app.register_blueprint(api_reservation_blueprint)
app.register_blueprint(api_box_blueprint)
app.register_blueprint(api_thumbnail_blueprint)


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection, if previously opened."""
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
