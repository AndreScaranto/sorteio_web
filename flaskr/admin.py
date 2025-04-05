from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import string
import random

bp = Blueprint('admin', __name__)

@bp.route('/index')
@login_required
def index():
    return render_template('admin/index.html')

@bp.route('/gerar_codigo', methods=('GET', 'POST'))
@login_required
def gerar_codigo():
    if request.method == 'POST':
        if request.form['sorteio_id']:
            possibilidades = string.ascii_uppercase + string.digits
            codigo = ""
            for i in range(7):
                for j in range(5):
                    codigo += random.choice(possibilidades)
                if i < 6:
                    codigo += "-"
            db = get_db()
            """db.execute(
                'SELECT nome FROM sorteio INTO bilhete (codigo,nome,sobrenome,celular)'
                ' VALUES (?, ?, ?, ?)',
                (codigo,nome,sobrenome,celular)
            )"""
            db.execute('INSERT INTO codigo (codigo,id_sorteio) VALUES (?, ?)',
                       (codigo,request.form['sorteio_id']))
            db.commit()
            return render_template('admin/gerar_codigo.html',sorteio_escolhido=True,codigo=codigo)
    db = get_db()
    sorteios = db.execute(
        'SELECT * FROM sorteio'
    ).fetchall()
    return render_template('admin/gerar_codigo.html',sorteio_escolhido=False,sorteios=sorteios)

@bp.route('/novo_sorteio', methods=('GET', 'POST'))
@login_required
def novo_sorteio():
    if request.method == 'POST':
        nome = request.form['nome']
        data_limite = request.form['data_limite']
        error = None

        if not nome:
            error = 'Faltou nome do sorteio.'

        if not data_limite:
            error = 'Faltou a data limite do sorteio.'

        if error is not None:
            flash(error)
        try:
            db = get_db()
            db.execute(
                'INSERT INTO sorteio (nome,data_limite)'
                ' VALUES (?, ?)',
                (nome,data_limite)
            )
            db.commit()
            flash(f"{nome} criado com sucesso.")
        except db.IntegrityError:
            error = f"Já há um sorteio cadastrado com o nome {nome}."
            flash(error)
        finally:
            return render_template('admin/novo_sorteio.html')
    return render_template('admin/novo_sorteio.html')

@bp.route('/sortear_bilhete')
@login_required
def sortear_bilhete():
    return render_template('admin/sortear_bilhete.html')
