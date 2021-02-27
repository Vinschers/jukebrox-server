from flask import Flask
from drive import Drive
import json

PORT = 5643
app = Flask(__name__)
gdrive = Drive()


@app.route('/')
def index():
    return json.dumps(gdrive.getChildren('1wjdeBBMqQBUN_MUY19xic32zrkQ8gtYq'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True)
