from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from apiclient.discovery import build
from apiclient.http import MediaIoBaseDownload
from httplib2 import Http

import io

from utils import natural_sort_key, ChunkHolder


class Drive:
    def __init__(self, credentials_path, client_secrets_path=''):
        SCOPE = 'https://www.googleapis.com/auth/drive'

        store = Storage(credentials_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = flow_from_clientsecrets(
                client_secrets_path, SCOPE)
            credentials = run_flow(flow, store)

        http = credentials.authorize(Http())

        self.drive = build('drive', 'v3', http=http)

    def get_file(self, file_id):
        return self.drive.files().get(fileId=file_id, fields="*").execute()

    def list_children(self, file_id):
        q = "'"+file_id+"' in parents and trashed = false"
        children = self.drive.files().list(q=q, fields="*").execute()['files']
        children.sort(key=natural_sort_key)
        return children

    def get_everything(self):
        q = "trashed=false"
        fields = "*"

        return self.drive.files().list(q=q, fields=fields).execute()['files']

    def create_folder(self, name, parent):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent]
        }

        folder = self.drive.files().create(
            body=file_metadata, fields='id').execute()
        return folder.get('id')

    def download(self, file_id):
        request = self.drive.files().get_media(fileId=file_id)
        fh = ChunkHolder()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            yield fh.chunk

    def download_chunk(self, file_id, start, end):
        request = self.drive.files().get_media(fileId=file_id)
        request.headers["Range"] = "bytes={}-{}".format(start, end)
        fh = io.BytesIO(request.execute())
        return fh.getvalue()
