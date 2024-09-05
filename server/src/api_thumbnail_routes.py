import glob
import os
from sqlite3.dbapi2 import Cursor

import auth
import common
import flask
import models
import werkzeug.utils
from PIL import Image


THUMBNAIL_FOLDER = os.path.abspath('../thumbnails')
ALLOWED_EXTENSIONS = {'jpg'}
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

api_thumbnail_blueprint = flask.Blueprint('api_thumbnail', __name__)


@api_thumbnail_blueprint.route('/api/thumbnail/get', methods=['GET', 'POST'])
def api_thumbnail_get():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form if flask.request.method == 'POST' else flask.request.args)
    item_id = form.get(models.Item.id_name)
    thumbnail_size = form.get('size', int)
    thumbnail_name = f'{item_id}_{thumbnail_size}.jpg'
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_name)

    if not os.path.exists(thumbnail_path):
        thumbnail_source_path = os.path.join(THUMBNAIL_FOLDER, f'{item_id}.jpg')
        image = Image.open(thumbnail_source_path)
        image.thumbnail((thumbnail_size, thumbnail_size))
        image.save(thumbnail_path)
        return image

    return flask.send_file(thumbnail_path, mimetype='image/jpg')


@api_thumbnail_blueprint.route('/api/thumbnail/upload', methods=['POST'])
@auth.route_requires_auth(auth.Scope.THUMBNAIL_UPLOAD)
def api_thumbnail_upload():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    if 'image' not in flask.request.files:
        flask.abort(400, 'No image sent')

    image = flask.request.files['image']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if image.filename == '':
        flask.abort(400, 'No image data sent')
    if not image:
        flask.abort(400, 'No image was specified')

    input_filename = werkzeug.utils.secure_filename(image.filename)
    input_filename_ext = input_filename.rsplit('.', 1)[1].lower() if ('.' in input_filename) else None
    if input_filename_ext not in ALLOWED_EXTENSIONS:
        flask.abort(415, f'Unsupported file type \'{input_filename_ext}\'. Expected one of {ALLOWED_EXTENSIONS}')

    # Do not overwrite existing files
    item_id = form.get(models.Item.id_name)
    output_filepath = os.path.join(THUMBNAIL_FOLDER, f'{item_id}.jpg')
    if os.path.exists(output_filepath):
        flask.abort(400, f'A thumbnail already exists for {models.Item.id_name} {item_id}. Delete this first.')

    _verify_item_exists(cursor, item_id)

    image.save(output_filepath)
    return common.create_response(200, [])


@api_thumbnail_blueprint.route('/api/thumbnail/delete', methods=['POST'])
@auth.route_requires_auth(auth.Scope.THUMBNAIL_DELETE)
def api_thumbnail_delete():
    # TODO documentation
    form = common.FlaskPOSTForm(flask.request.form)
    conn, cursor = common.get_db_connection()

    item_id = form.get(models.Item.id_name)
    _verify_item_exists(cursor, item_id)

    thumbnail_paths = glob.glob(os.path.join(THUMBNAIL_FOLDER, f'{item_id}_*.jpg'))
    thumbnail_paths.append(os.path.join(THUMBNAIL_FOLDER, f'{item_id}.jpg'))

    for path in thumbnail_paths:
        os.remove(path)

    return common.create_response(200, [])


def _verify_item_exists(cursor: Cursor, item_id: str) -> None:
    item_res = cursor.execute(f'SELECT * FROM {models.Item.table_name} WHERE {models.Item.id_name}=?', (item_id,))
    db_item = item_res.fetchone()
    if db_item is None or len(db_item) == 0:
        flask.abort(404, f'{models.Item.__name__} does not exist')
