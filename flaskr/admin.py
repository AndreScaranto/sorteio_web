from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import string
import random
import secrets

bp = Blueprint('admin', __name__)

@bp.route('/index')
@login_required
def index():
    return render_template('admin/index.html')

@bp.route('/gerar_codigo', methods=('GET', 'POST'))
@login_required
def gerar_codigo():
    if request.method == 'POST':
        if 'sorteio_id' in request.form:
            possibilidades = string.ascii_uppercase + string.digits
            codigo = ""
            for i in range(7):
                for j in range(5):
                    codigo += random.choice(possibilidades)
                if i < 6:
                    codigo += "-"
            db = get_db()
            db.execute('INSERT INTO codigo (codigo,id_sorteio) VALUES (?, ?)',
                       (codigo,request.form['sorteio_id']))
            db.commit()
            return render_template('admin/gerar_codigo.html',sorteio_escolhido=True,codigo=codigo)
    db = get_db()
    sorteios = db.execute(
        'SELECT * FROM sorteio WHERE NOT realizado'
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

@bp.route('/sortear_bilhete', methods=('GET', 'POST'))
@login_required
def sortear_bilhete():
    if request.method == 'POST':
        if 'sorteio_id' in request.form:
            db = get_db()
            bilhetes = db.execute('SELECT * FROM bilhete WHERE id_sorteio = ?',
                       (request.form['sorteio_id'],)).fetchall()
            tamanho = len(bilhetes)
            if tamanho > 0:
                numero_sorteado = secrets.choice(range(tamanho))
                sorteado = bilhetes[numero_sorteado]
                return render_template('admin/sortear_bilhete.html',sorteio_escolhido=True,bilhetes_vazio=False,validado=False,sorteado=sorteado)
            else:
                return render_template('admin/sortear_bilhete.html',sorteio_escolhido=True,bilhetes_vazio=True)
        elif 'id_bilhete' in request.form:
            db = get_db()
            sorteado = db.execute('SELECT * FROM bilhete WHERE id_bilhete = ?',
                       (request.form['id_bilhete'],)).fetchone()
            db.execute('UPDATE sorteio SET realizado = 1, id_bilhete_sorteado = ? WHERE id_sorteio = ?',
                       (sorteado['id_bilhete'],sorteado['id_sorteio'])
            )
            db.commit()
            return render_template('admin/sortear_bilhete.html',sorteio_escolhido=True,validado=True,sorteado=sorteado)
    db = get_db()
    sorteios = db.execute(
        'SELECT * FROM sorteio WHERE NOT realizado'
    ).fetchall()
    return render_template('admin/sortear_bilhete.html',sorteio_escolhido=False,sorteios=sorteios)


@bp.route('/consultar_vencedor', methods=('GET', 'POST'))
@login_required
def consultar_vencedor():
    db = get_db()
    sorteios = db.execute(
        'SELECT * FROM sorteio WHERE realizado'
    ).fetchall()
    if request.method == 'POST':
        if 'sorteio_id' in request.form:
            sorteado = db.execute('SELECT id_bilhete_sorteado,nome FROM sorteio WHERE id_sorteio = ?',
                       (request.form['sorteio_id'],)).fetchone()
            vencedor = db.execute('SELECT * FROM bilhete WHERE id_bilhete = ?',
                       (sorteado['id_bilhete_sorteado'],)).fetchone()         
            return render_template('admin/consultar_vencedor.html',sorteio_escolhido=True,vencedor = vencedor,sorteio=sorteado['nome'],sorteios=sorteios)
    return render_template('admin/consultar_vencedor.html',sorteio_escolhido=False,sorteios=sorteios)