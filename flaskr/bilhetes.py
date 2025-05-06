from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime
from datetime import timedelta

bp = Blueprint('bilhetes', __name__)

@bp.route('/')
def index():
    return render_template('bilhetes/index.html')

@bp.route('/depositar_bilhete', methods=('GET', 'POST'))
def depositar_bilhete():
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
            cur = db.cursor(buffered = True)
            cur.execute(
                'SELECT * FROM codigo WHERE codigo = %s',
                (codigo,)
            )
            if cur.rowcount > 0:
                consulta_codigo = dict(zip(cur.column_names, cur.fetchone()))
                cur.execute('SELECT data_limite,nome FROM sorteio WHERE id_sorteio = %s',
                           (consulta_codigo['id_sorteio'],))
                consulta_sorteio = dict(zip(cur.column_names, cur.fetchone()))
                data_limite = consulta_sorteio['data_limite']
                today = datetime.today()
                if (today - data_limite) > timedelta(days = 1):
                    error = f"O sorteio {consulta_sorteio['nome']} não aceita mais novos bilhetes."
                    flash(error)
                else:
                    try:
                        cur.execute(
                            'INSERT INTO bilhete (codigo,nome,sobrenome,celular,id_sorteio)'
                            ' VALUES (%s, %s, %s, %s, %s)',
                            (codigo,nome,sobrenome,celular,consulta_codigo['id_sorteio'])
                        )
                        db.commit()
                        flash("Bilhete depositado com sucesso")
                    except db.IntegrityError:
                        error = f"O código {codigo} já foi utilizado."
                        flash(error)
            else:
                flash("O código não é válido")
            return redirect(url_for('bilhetes.index'))

    return render_template('bilhetes/depositar_bilhete.html')

@bp.route('/consultar_bilhetes', methods=('GET','POST'))
def consultar_bilhetes():
    if request.method == 'POST':
        codigo = request.form['codigo']
        celular = request.form['celular']
        error = None

        if not codigo and not celular:
            error = 'Preencha pelo menos um campo.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            bilhetes_encontrados = db.execute(
                'SELECT bilhete.id_bilhete AS id_bilhete, bilhete.codigo AS codigo, bilhete.celular AS celular,' +
                 ' sorteio.nome AS nome_sorteio, sorteio.realizado AS realizado, sorteio.id_bilhete_sorteado as id_sorteado' + 
                ' FROM bilhete INNER JOIN sorteio ON bilhete.id_sorteio = sorteio.id_sorteio' +
                 ' WHERE ((? = "") OR bilhete.codigo = ?) AND bilhete.celular LIKE ?',
                (codigo,codigo,'%'+celular+'%')
            ).fetchall()
            db.commit()
            return render_template('bilhetes/resultados_consulta.html',bilhetes_encontrados=bilhetes_encontrados)

    return render_template('bilhetes/consultar_bilhetes.html')



