from flask import Blueprint, Response

from drive import Drive
from utils import path_to

blueprint = Blueprint('blueprint', __name__)

# TODO: https://git-secret.io/
CREDENTIALS_FILE = path_to(__file__, 'credentials/credentials.json')
CLIENTSECRET_FILE = path_to(__file__, 'credentials/client_secret.json')

gdrive = Drive(CREDENTIALS_FILE, CLIENTSECRET_FILE)


@blueprint.route('/')
def index():
    return 'ok'


@blueprint.route('/<file_id>/get')
def get_file(file_id):
    return gdrive.get(file_id)


@blueprint.route('/<file_id>/download')
def download(file_id):
    file = gdrive.get(file_id)
    headers = {
        "Content-disposition": "attachment; filename=" + file.get('name')
    }
    return Response(gdrive.download(file.get('id')), headers=headers)
