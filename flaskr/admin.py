from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('admin', __name__)

@bp.route('/index')
def index():
    return render_template('admin/index.html')

@bp.route('/gerar_codigo', methods=('GET', 'POST'))
def gerar_codigo():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        celular = request.form['celular']
        error = None

        if not codigo:
            error = 'Faltou o código do bilhete.'

        if not nome:
            error = 'Faltou o nome do sorteado.'

        if not sobrenome:
            error = 'Faltou o sobrenome do sorteado.'

        if not celular:
            error = 'Faltou o celular do sorteado.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO bilhete (codigo,nome,sobrenome,celular)'
                ' VALUES (?, ?, ?, ?)',
                (codigo,nome,sobrenome,celular)
            )
            db.commit()
            return redirect(url_for('bilhetes.index'))

    return render_template('admin/gerar_codigo.html')

@bp.route('/consultar_bilhetes', methods=('GET','POST'))
def consultar_bilhetes():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        celular = request.form['celular']
        error = None

        if not codigo and not nome and not sobrenome and not celular:
            error = 'Preencha pelo menos um campo.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            bilhetes_encontrados = db.execute(
                'SELECT codigo,nome,sobrenome,celular FROM bilhete WHERE codigo LIKE ? AND nome LIKE ? AND sobrenome LIKE ? AND celular LIKE ?',
                ('%'+codigo+'%','%'+nome+'%','%'+sobrenome+'%','%'+celular+'%')
            ).fetchall()
            db.commit()
            return render_template('bilhetes/resultados_consulta.html',bilhetes_encontrados=bilhetes_encontrados)

    return render_template('bilhetes/consultar_bilhetes.html')

