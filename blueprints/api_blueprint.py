from flask import Blueprint, Response
import json
import os
from os import environ
from os.path import abspath, join

from services.drive import Drive
from services.database import Database
from utils import path_to, create_drive_path, fix_tag_path

blueprint = Blueprint('api', __name__)

client_secret_path = join(abspath('secrets'), 'client_secret.json')

credentials_json = environ.get('GOOGLE_CREDENTIALS')
server = environ.get('DATABASE_SERVER')
db = environ.get('DATABASE_NAME')
user = environ.get('DATABASE_USER')
password = environ.get('DATABASE_PASSWORD')

gdrive = Drive(client_secret_path, credentials_json)
db = Database(server, db, user, password)


@blueprint.route('/')
def index():
    return 'ok'


@blueprint.route('/drive/<file_id>/get')
def get_file(file_id):
    return gdrive.get_file(file_id)


@blueprint.route('/drive/<file_id>/download')
def download(file_id):
    file = gdrive.get_file(file_id)
    headers = {
        "Content-disposition": "attachment; filename=" + file.get('name')
    }
    return Response(gdrive.download(file.get('id')), headers=headers)

@blueprint.route('/<root_id>/buildTree')
def buildTree(root_id):
    all_files = gdrive.get_everything()
    root = gdrive.get_file(root_id)

    files_dict = create_drive_path(all_files=all_files, root=root, drive_path_key='drivePath')

    tags_dict = db.get_tags_from_files(files_dict.keys())

    for file_id, tags in tags_dict.items():
        files_dict[file_id]['tagPath'] = tags

    for file_id, file in files_dict.items():
        file['tagPath'] = fix_tag_path(file['tagPath'] if 'tagPath' in file else None)

    return json.dumps({"result": files_dict})