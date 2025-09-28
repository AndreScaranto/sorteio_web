from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flaskr.db import get_db
from datetime import datetime, timedelta
import sqlite3

bp = Blueprint('bilhetes', __name__)

@bp.route('/')
def index():
    return render_template('bilhetes/index.html')


@bp.route('/depositar_bilhete', methods=('GET', 'POST'))
def depositar_bilhete():
    db = get_db()

    if request.method == 'POST':
        codigo = (request.form.get('codigo') or '').strip()
        nome       = (request.form.get('nome') or '').strip()
        sobrenome  = (request.form.get('sobrenome') or '').strip()
        celular    = (request.form.get('celular') or '').strip()

        # validações
        if not codigo:
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
        codigo = (request.form.get('codigo') or '').strip()
        celular    = (request.form.get('celular') or '').strip()

        if not codigo and not celular:
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


        # filtro por celular (LIKE)
        if celular:
            sql += ' AND bilhete.celular LIKE ?'
            params.append(f'%{celular}%')

        rows = db.execute(sql, tuple(params)).fetchall()
        bilhetes_encontrados = [dict(r) for r in rows]

        return render_template('bilhetes/resultados_consulta.html',
                               bilhetes_encontrados=bilhetes_encontrados)

    # GET
    return render_template('bilhetes/consultar_bilhetes.html')



