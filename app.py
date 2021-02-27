from flask import Flask
import api


PORT = 5643
app = Flask(__name__)

app.register_blueprint(api.blueprint, url_prefix='/api')


@app.route('/')
def index():
    return 'Welcome to Jukebrox! Web app under development.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True)
