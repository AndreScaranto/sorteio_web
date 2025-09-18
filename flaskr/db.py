# flaskr/db.py — SQLite com caminho absoluto + init_app
import sqlite3, os
from flask import g

# /home/RICARDO/sorteio/sorteio_web-main
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'flaskr.sqlite')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Registra o fechamento de conexão ao fim do request e garante a pasta instance."""
    app.teardown_appcontext(close_db)
    try:
        os.makedirs(os.path.join(PROJECT_ROOT, 'instance'), exist_ok=True)
    except OSError:
        pass
