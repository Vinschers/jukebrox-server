from flask import Flask
from os import environ

from blueprints.index_blueprint import blueprint as index_blueprint
from blueprints.api_drive_blueprint import blueprint as api_drive_blueprint


PORT = environ.get("PORT", 5643)
app = Flask(__name__)

def register_blueprints():
    app.register_blueprint(index_blueprint, url_prefix='/')
    app.register_blueprint(api_drive_blueprint, url_prefix='/api/drive')


if __name__ == '__main__':
    register_blueprints()
    app.run(host='0.0.0.0', port=PORT)