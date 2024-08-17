import dotenv
import flask
from werkzeug.exceptions import HTTPException

import common
import models
from api_item_routes import api_item_blueprint
from api_user_routes import api_user_blueprint
from api_reservation_routes import api_reservation_blueprint


def _create_table(table_name: str, key_model: models.Model):
    table_keys = ", ".join([f"{k} TEXT" for k in key_model.to_response().keys()])
    conn = common.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name}({table_keys})').close()


dotenv.load_dotenv()
app = flask.Flask(__name__)

with app.app_context():
    _create_table(common.ITEMS_TABLE_NAME, models.BLANK_ITEM)
    _create_table(common.USERS_TABLE_NAME, models.BLANK_USER)
    _create_table(common.RESERVATIONS_TABLE_NAME, models.BLANK_RESERVATION)

app.register_blueprint(api_item_blueprint)
app.register_blueprint(api_user_blueprint)
app.register_blueprint(api_reservation_blueprint)


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
    response.data = flask.json.dumps(common.create_response(
        e.code,
        {
            "name": e.name,
            "description": e.description,
        }
    ))
    response.content_type = "application/json"
    return response
