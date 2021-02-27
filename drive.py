from apiclient import discovery, errors
from httplib2 import Http
from oauth2client import client, file, tools
from apiclient.http import *
import mimetypes
import os
import io
import requests
from utils import natural_sort_key


class Drive:
    def __init__(self):
        # define variables
        self.credentials_file_path = './credentials/credentials.json'
        self.clientsecret_file_path = './credentials/client_secret.json'

        # define scope
        self.SCOPE = 'https://www.googleapis.com/auth/drive'

        # define store
        self.store = file.Storage(self.credentials_file_path)
        self.credentials = self.store.get()

        if not self.credentials or self.credentials.invalid:
            flow = client.flow_from_clientsecrets(
                self.clientsecret_file_path, self.SCOPE)
            self.credentials = tools.run_flow(flow, self.store)

        # define API service
        http = self.credentials.authorize(Http())
        self.drive = discovery.build('drive', 'v3', http=http)

    def getFile(self, file_id):
        return self.drive.files().get(fileId=file_id, fields="*").execute()

    def getChildren(self, file_id):
        children = self.drive.files().list(
            q="'"+file_id+"' in parents and trashed = false", fields="*").execute()['files']
        children.sort(key=natural_sort_key)
        return children

    def createFolder(self, name, parent):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent]
        }

        folder = self.drive.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    def getFileFromFolder(self, folderID):
        res = self.drive.files().list(q="mimeType='application/vnd.google-apps.file' and parents in '" +
                                      folderID+"' and trashed = false", fields="files(name)").execute()['files']
        if len(res) > 0:
            return res[0]
        else:
            return None

    def getFolderIDFromFolder(self, name, folderID):
        res = self.drive.files().list(q="mimeType='application/vnd.google-apps.folder' and parents in '" +
                                      folderID+"' and trashed = false", fields="files(id, name)").execute()
        res = res['files']
        for folder in res:
            if folder.get('name').replace("-", "").replace(":", "") == name:
                return folder.get('id')
        file_metadata = {
            'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [folderID]}
        folder = self.drive.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    def deleteFile(self, id):
        self.drive.files().delete(fileId=id).execute()
        return "ok"

    def downloadFile(self, file_id):
        request = self.drive.files().get_media(fileId=file_id)
        fh = ChunkHolder()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
            yield fh.chunk

    def downloadChunkFromFile(self, file_id, start, end):
        request = self.drive.files().get_media(fileId=file_id)
        request.headers["Range"] = "bytes={}-{}".format(start, end)
        fh = io.BytesIO(request.execute())
        return fh.getvalue()
