from flask import Flask
from flask_cors import CORS

SQLALCHEMY_DATABASE_URI = '' # confidential info

def create_app_models_only():
    import models
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    models.init_app(app)
    return app


def create_app():
    import models
    import controllers
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    CORS(app)
    models.init_app(app)
    controllers.init_app(app)

    return app


if __name__ == '__main__':
    server_app = create_app()
    server_app.run(host='localhost', port=5000, debug=True)

