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
