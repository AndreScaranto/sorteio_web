from flask import (
<<<<<<< HEAD
    Blueprint, flash, redirect, render_template, request, url_for
)
from flaskr.db import get_db
from datetime import datetime, timedelta
import sqlite3
=======
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime
from datetime import timedelta
>>>>>>> 32afeb09a2eb65cefe44a1447c4d6a94da14dcd1

bp = Blueprint('bilhetes', __name__)

@bp.route('/')
def index():
    return render_template('bilhetes/index.html')

<<<<<<< HEAD

@bp.route('/depositar_bilhete', methods=('GET', 'POST'))
def depositar_bilhete():
    db = get_db()

    if request.method == 'POST':
        codigo_raw = (request.form.get('codigo') or '').strip()
        nome       = (request.form.get('nome') or '').strip()
        sobrenome  = (request.form.get('sobrenome') or '').strip()
        celular    = (request.form.get('celular') or '').strip()

        # validações
        if not codigo_raw:
            flash('Faltou o código do bilhete.')
            return render_template('bilhetes/depositar_bilhete.html')

        if not nome:
            flash('Faltou o nome do sorteado.')
            return render_template('bilhetes/depositar_bilhete.html')

        if not sobrenome:
            flash('Faltou o sobrenome do sorteado.')
            return render_template('bilhetes/depositar_bilhete.html')

        if not celular:
            flash('Faltou o celular do sorteado.')
            return render_template('bilhetes/depositar_bilhete.html')

        # codigo deve ser INTEGER (seu schema)
        try:
            codigo = int(codigo_raw)
        except ValueError:
            flash('O código precisa ser numérico.')
            return render_template('bilhetes/depositar_bilhete.html')

        # 1) verifica se o código existe na tabela codigo
        cod_row = db.execute(
            'SELECT id_sorteio FROM codigo WHERE codigo = ?',
            (codigo,)
        ).fetchone()

        if not cod_row:
            flash('O código não é válido.')
            return render_template('bilhetes/depositar_bilhete.html')

        id_sorteio = cod_row['id_sorteio']

        # 2) pega o sorteio e checa a data_limite
        sort_row = db.execute(
            'SELECT data_limite, nome, realizado FROM sorteio WHERE id_sorteio = ?',
            (id_sorteio,)
        ).fetchone()

        if not sort_row:
            flash('Sorteio não encontrado para esse código.')
            return render_template('bilhetes/depositar_bilhete.html')

        if sort_row['realizado']:
            flash(f"O sorteio {sort_row['nome']} já foi realizado.")
            return render_template('bilhetes/depositar_bilhete.html')

        # data_limite pode estar como 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
        raw = sort_row['data_limite']
        data_limite = None
        if isinstance(raw, str):
            try:
                data_limite = datetime.fromisoformat(raw)
            except ValueError:
                # tenta só data
                try:
                    data_limite = datetime.strptime(raw, '%Y-%m-%d')
                except ValueError:
                    # última tentativa: cortar só a parte da data
                    data_limite = datetime.strptime(raw.split(' ')[0], '%Y-%m-%d')
        elif isinstance(raw, datetime):
            data_limite = raw

        if data_limite is None:
            # se não conseguiu parsear, deixa passar (ou bloqueia, escolha sua)
            pass
        else:
            hoje = datetime.now()
            if (hoje - data_limite) > timedelta(days=1):
                flash(f"O sorteio {sort_row['nome']} não aceita mais novos bilhetes.")
                return render_template('bilhetes/depositar_bilhete.html')

        # 3) impede duplicidade do mesmo código neste sorteio
        dup = db.execute(
            'SELECT 1 FROM bilhete WHERE id_sorteio = ? AND codigo = ?',
            (id_sorteio, codigo)
        ).fetchone()
        if dup:
            flash(f"O código {codigo} já foi utilizado neste sorteio.")
            return render_template('bilhetes/depositar_bilhete.html')

        # 4) insere o bilhete
        try:
            db.execute(
                'INSERT INTO bilhete (codigo, nome, sobrenome, celular, id_sorteio) '
                'VALUES (?, ?, ?, ?, ?)',
                (codigo, nome, sobrenome, celular, id_sorteio)
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash(f"O código {codigo} já foi utilizado.")
            return render_template('bilhetes/depositar_bilhete.html')

        flash("Bilhete depositado com sucesso")
        return redirect(url_for('bilhetes.index'))

    # GET
    return render_template('bilhetes/depositar_bilhete.html')


@bp.route('/consultar_bilhetes', methods=('GET','POST'))
def consultar_bilhetes():
    if request.method == 'POST':
        codigo_raw = (request.form.get('codigo') or '').strip()
        celular    = (request.form.get('celular') or '').strip()

        if not codigo_raw and not celular:
            flash('Preencha pelo menos um campo.')
            return render_template('bilhetes/consultar_bilhetes.html')

        db = get_db()

        sql = (
            'SELECT '
            '  bilhete.id_bilhete AS id_bilhete, '
            '  bilhete.codigo    AS codigo, '
            '  bilhete.celular   AS celular, '
            '  sorteio.nome      AS nome_sorteio, '
            '  sorteio.realizado AS realizado, '
            '  sorteio.id_bilhete_sorteado AS id_sorteado '
            'FROM bilhete '
            'INNER JOIN sorteio ON bilhete.id_sorteio = sorteio.id_sorteio '
            'WHERE 1=1 '
        )
        params = []

        # filtro por codigo (INTEGER)
        if codigo_raw:
            try:
                codigo = int(codigo_raw)
                sql += ' AND bilhete.codigo = ?'
                params.append(codigo)
            except ValueError:
                flash('O código precisa ser numérico.')
                return render_template('bilhetes/consultar_bilhetes.html')

        # filtro por celular (LIKE)
        if celular:
            sql += ' AND bilhete.celular LIKE ?'
            params.append(f'%{celular}%')

        rows = db.execute(sql, tuple(params)).fetchall()
        bilhetes_encontrados = [dict(r) for r in rows]

        return render_template('bilhetes/resultados_consulta.html',
                               bilhetes_encontrados=bilhetes_encontrados)

    # GET
=======
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
                    except:
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
            cur = db.cursor()
            cur.execute(
                'SELECT bilhete.id_bilhete AS id_bilhete, bilhete.codigo AS codigo, bilhete.celular AS celular,' +
                 ' sorteio.nome AS nome_sorteio, sorteio.realizado AS realizado, sorteio.id_bilhete_sorteado as id_sorteado' + 
                ' FROM bilhete INNER JOIN sorteio ON bilhete.id_sorteio = sorteio.id_sorteio' +
                 ' WHERE ((%s = "") OR bilhete.codigo = %s) AND bilhete.celular LIKE %s',
                (codigo,codigo,'%'+celular+'%')
            )
            bilhetes_encontrados = []
            for resultado in cur.fetchall():
                bilhetes_encontrados.append(dict(zip(cur.column_names, resultado)))
            db.commit()
            return render_template('bilhetes/resultados_consulta.html',bilhetes_encontrados=bilhetes_encontrados)

>>>>>>> 32afeb09a2eb65cefe44a1447c4d6a94da14dcd1
    return render_template('bilhetes/consultar_bilhetes.html')



