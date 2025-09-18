import mysql.connector as mysql # type: ignore
from datetime import datetime

import click
from flask import current_app, g
from werkzeug.security import check_password_hash, generate_password_hash

def get_db():
    if 'db' not in g:
        db = mysql.connect(
            **current_app.config['DATABASE']
        )

        g.db = db


    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with db.cursor(buffered = True) as cur:
        with current_app.open_resource('schema_mysql_workbench.sql') as f:
            cur.execute(f.read().decode('utf8'))
        #db.fetchall()

    close_db()
    db = get_db()
    with db.cursor(buffered = True) as cur:
        cur.execute(
            "INSERT INTO administrador (username, password) VALUES (%s, %s)",
            ("admin", generate_password_hash("admin"))
        )
        db.commit()
        click.echo('Administrador default adicionado.')



@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')




def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
