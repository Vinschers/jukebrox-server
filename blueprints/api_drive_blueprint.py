from flask import Blueprint, Response
import json
import os
from os import environ
from os.path import abspath, isdir, isfile, join

from services.drive import Drive
from utils import path_to

SECRETS_PATH = abspath(environ.get('SECRETS_PATH', 'secrets'))

blueprint = Blueprint('drive', __name__)

SECRETS_PATH = abspath('secrets')
client_secret_path = join(SECRETS_PATH, 'client_secret.json')
credentials_path = join(SECRETS_PATH, 'credentials.json')

def setup_secrets_structure():
    if not isdir(SECRETS_PATH):
        os.mkdir(SECRETS_PATH)
    if not isfile(client_secret_path):
        with open(client_secret_path, 'w') as client_secret:
            client_secret.write(environ.get('CLIENT_SECRET'))


setup_secrets_structure()
#gdrive = Drive(client_secret_path, credentials_path)
gdrive = None


@blueprint.route('/')
def index():
    return 'ok'


@blueprint.route('/<file_id>/get')
def get_file(file_id):
    return gdrive.get_file(file_id)


@blueprint.route('/<file_id>/download')
def download(file_id):
    file = gdrive.get_file(file_id)
    headers = {
        "Content-disposition": "attachment; filename=" + file.get('name')
    }
    return Response(gdrive.download(file.get('id')), headers=headers)

@blueprint.route('<id>/buildTree')
def buildTree(id):
    all_files = gdrive.get_everything()
    parents_map = {}
    for file in all_files:
        if not 'parents' in file:
            continue
        for parent in file['parents']:
            if not parent in parents_map:
                parents_map[parent] = []
            parents_map[parent].append(file)
    files_list = []

    def get_files_in_folder(folder, path):
        children = parents_map[folder['id']]
        for child in children:
            if not 'folder' in child['mimeType']:
                child['drivePath'] = path
                files_list.append(child)
            else:
                new_path = list(path)
                new_path.append({'id': child['id'], 'name': child['name']})
                get_files_in_folder(child, new_path)
    
    root = gdrive.get_file(id)
    get_files_in_folder(root, [{'id': root['id'], 'name': root['name']}])

    return json.dumps({"result": files_list})