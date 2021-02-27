from flask import Flask
import json

from drive import Drive
from utils import sendUntilEndOfRequest, path_to


PORT = 5643
app = Flask(__name__)
# TODO: https://git-secret.io/
gdrive = Drive(path_to(__file__, 'credentials/credentials.json'))


@app.route('/')
def index():
    return json.dumps(gdrive.getChildren('1wjdeBBMqQBUN_MUY19xic32zrkQ8gtYq'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True)
