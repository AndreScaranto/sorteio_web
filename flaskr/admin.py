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

@bp.route('/novo_sorteio')
def novo_sorteio():
    return render_template('admin/novo_sorteio.html')

@bp.route('/sortear_bilhete')
def sortear_bilhete():
    return render_template('admin/sortear_bilhete.html')
