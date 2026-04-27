


import sqlite3, os
from datetime import datetime

import click
from flask import current_app, g
from werkzeug.security import check_password_hash, generate_password_hash

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

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        """"""
        db.execute(
            "INSERT INTO administrador (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin")),
        )
        db.commit()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def load_usuarios(db):
    users = ["Andre", "Mario", "Maria", "Tamires", "Savio", "Guilherme", "Ricardo", "Armando"]
    i = 1
    for user in users:
        db.execute(
            "INSERT INTO usuario (username, password, CPF, celular) VALUES (?, ?, ?, ?)",
            (user, generate_password_hash(user.lower()),11*str(i),"9"+8*str(i)),
        )
        i = i + 1
    db.commit()

def load_sorteios(db):
    pass

def load_produtos(db):
    produtos = {"Rustico Branco" : "20", 
                "Focaccia Gorgonzola" : "30",
                "Focaccia Calabresa" : "27",
                "Pão de Forma Integral" : "25"}
    for item in produtos:
        db.execute(
            "INSERT INTO produto (nome, preco_atual) VALUES (?, ?)",
            (item, produtos[item]),
        )
    db.commit()


def load_vendas(db):
    pass

def load_test_db():
    db = get_db()
    load_usuarios(db)
    load_produtos(db)
    load_sorteios(db)
    load_vendas(db)


@click.command('load-test-db')
def load_test_db_command():
    """Clear the existing data and create new tables."""
    load_test_db()
    click.echo('Loaded the test database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_test_db_command)