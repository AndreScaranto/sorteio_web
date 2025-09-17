<<<<<<< HEAD
from flask import Flask
import os
from . import db, auth, bilhetes, admin

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE={
            'host': 'localhost',
            'user': 'root',
            'password': 'univesp123',
            'database': 'sorteio_web'
        }
    )

    if test_config is not None:
        app.config.update(test_config)

    # Inicializa o banco
    db.init_app(app)

    # Registra blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(bilhetes.bp)
    app.register_blueprint(admin.bp)

    return app
=======
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE={'user':'root', 'password':'root1234',
                              'host':'127.0.0.1','port':'3305',
                              'database':'sorteio_web'}
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)


    from . import bilhetes
    app.register_blueprint(bilhetes.bp)
    app.add_url_rule('/', endpoint='index')

    from . import admin
    app.register_blueprint(admin.bp)

    return app
>>>>>>> 32afeb09a2eb65cefe44a1447c4d6a94da14dcd1
