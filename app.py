from flask import Flask
from os import environ


from os.path import isfile
if isfile('env.py'):
    import env


from blueprints.index_blueprint import blueprint as index_blueprint
from blueprints.api_blueprint import blueprint as api_blueprint



PORT = environ.get("PORT", 5643)
app = Flask(__name__)

def register_blueprints():
    app.register_blueprint(index_blueprint, url_prefix='/')
    app.register_blueprint(api_blueprint, url_prefix='/api')


if __name__ == '__main__':
    register_blueprints()
    app.run(host='0.0.0.0', port=PORT)