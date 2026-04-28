


import sqlite3, os, random
from datetime import datetime,timedelta

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
    click.echo('Base de dados inicializada vazia.')

def carrega_usuarios(db):
    users = ["Andre", "Mario", "Maria", "Tamires", "Savio", "Guilherme", "Ricardo", "Armando"]
    i = 1
    for user in users:
        db.execute(
            "INSERT INTO usuario (username, password, CPF, celular) VALUES (?, ?, ?, ?)",
            (user, generate_password_hash(user.lower()),11*str(i),"9"+8*str(i)),
        )
        i = i + 1
    db.commit()

data_inicio_db = "2026-03-10"
data_inicio_sorteio = "2026-04-10"
data_final_sorteio = "2026-05-10"

def carrega_sorteios(db):
    db.execute(
        "INSERT INTO sorteio (nome, data_inicial, data_limite) VALUES (?, ?, ?)",
        ("Dia das Mães", data_inicio_sorteio, data_final_sorteio),
    )

produtos = {"Rustico Branco" : "20", 
            "Pão de Forma Integral" : "25",
            "Focaccia Gorgonzola" : "30",
            "Focaccia Calabresa" : "27"}

def carrega_produtos(db):
    for item in produtos:
        db.execute(
            "INSERT INTO produto (nome, preco_atual) VALUES (?, ?)",
            (item, produtos[item]),
        )
    db.commit()


def carrega_vendas(db):
    datetime_inicio = datetime.fromisoformat(data_inicio_db)
    datetime_inicio_sorteio = datetime.fromisoformat(data_inicio_sorteio)
    datetime_final_sorteio = datetime.fromisoformat(data_final_sorteio)
    datetime_atual = datetime_inicio
    random.seed("caso 1")
    medias_venda_dia_semana = {
        2 : (6, 6, 4, 4),
        3 : (8, 8, 7, 7),
        4 : (6, 6, 9, 9),
        5 : (3, 3, 4, 4)
    }
    nomes_produtos = ("Rustico Branco",
                "Pão de Forma Integral",
                "Focaccia Gorgonzola",
                "Focaccia Calabresa")
    while (datetime_final_sorteio - datetime_atual) > timedelta(days=-1):
        print(datetime_atual)
        print(datetime_atual.weekday())
        aleatorio = random.random()
        dia_semana = datetime_atual.weekday()
        if dia_semana >= 2 and dia_semana <= 5:
            if (datetime_atual - datetime_inicio_sorteio) > timedelta(days=-1):
                fator_sorteio = 1.2
            else:
                fator_sorteio = 1
            medias = medias_venda_dia_semana[dia_semana]
            #print(media_rust)
            #print(media_forma)
            #print(media_gorg)
            #print(media_cala)
            total = sum(medias) * fator_sorteio
            aleatorio = aleatorio * total + 1
            while aleatorio < total:
                cumulativo = 0
                for i in range(len(medias)):
                    cumulativo = cumulativo + medias[i] * fator_sorteio
                    if aleatorio < cumulativo:
                        preco_venda = produtos[nomes_produtos[i]]
                        id_produto = i + 1
                        break
                usuario = random.randrange(8) + 1
                db.execute(
                    "INSERT INTO venda (data_venda, id_usuario, id_produto, preco_venda, desconto_unitario, quantidade_vendida) " + 
                     " VALUES (?, ?, ?, ?, 0.0, 1)",
                    (datetime_atual, usuario, id_produto, preco_venda),
                )
                aleatorio = total * random.random() + 1

        datetime_atual = datetime_atual + timedelta(days=1)
    db.commit()

def carrega_test_db():
    db = get_db()
    carrega_usuarios(db)
    carrega_produtos(db)
    carrega_sorteios(db)
    carrega_vendas(db)


@click.command('carrega-test-db')
def carrega_test_db_command():
    carrega_test_db()
    click.echo('Base de dados de teste carregada.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(carrega_test_db_command)