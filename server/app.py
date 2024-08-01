import dotenv
import flask
from werkzeug.exceptions import HTTPException

import common
import models
from api_routes import api_blueprint
from root_routes import root_blueprint


def _create_table(table_name: str, key_model: models.Model):
    table_keys = ", ".join([f"{k} TEXT" for k in key_model.to_dict().keys()])
    common.get_db().cursor().execute(f'CREATE TABLE IF NOT EXISTS {table_name}({table_keys})').close()


dotenv.load_dotenv()
app = flask.Flask(__name__)

with app.app_context():
    _create_table("users", models.BLANK_USER)
    _create_table("items", models.BLANK_ITEM)

app.register_blueprint(api_blueprint)
app.register_blueprint(root_blueprint)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = flask.json.dumps({"error": {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }})
    response.content_type = "application/json"
    return response
