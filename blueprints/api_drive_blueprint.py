from flask import Blueprint, Response
import json
import os

from services.drive import Drive
from utils import path_to

blueprint = Blueprint('drive', __name__)

# TODO: https://git-secret.io/
CREDENTIALS_FILE = os.path.abspath('credentials/credentials.json')
CLIENTSECRET_FILE = os.path.abspath('credentials/client_secret.json')

gdrive = Drive(CREDENTIALS_FILE, CLIENTSECRET_FILE)


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