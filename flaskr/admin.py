# flaskr/admin.py
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flaskr.auth import login_required
from flaskr.db import get_db
import secrets
import sqlite3
import random, string

bp = Blueprint('admin', __name__)

@bp.route('/index')
@login_required
def index():
    return render_template('admin/index.html')


@bp.route('/gerar_codigo', methods=('GET', 'POST'))
@login_required
def gerar_codigo():
    db = get_db()

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
            db.execute(
                'INSERT INTO codigo (codigo, id_sorteio) VALUES (?, ?)',
                (codigo, request.form['sorteio_id'])
            )
            db.commit()
            return render_template(
                'admin/gerar_codigo.html',
                sorteio_escolhido=True,
                codigo=codigo
            )

    sorteios = db.execute(
        'SELECT * FROM sorteio WHERE NOT realizado'
    ).fetchall()
    return render_template('admin/gerar_codigo.html',
                           sorteio_escolhido=False,
                           sorteios=sorteios)

@bp.route('/novo_sorteio', methods=('GET', 'POST'))
@login_required
def novo_sorteio():
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        data_limite = (request.form.get('data_limite') or '').strip()

        if not nome:
            flash('Faltou nome do sorteio.')
        elif not data_limite:
            flash('Faltou a data limite do sorteio.')
        else:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO sorteio (nome, data_limite) VALUES (?, ?)',
                    (nome, data_limite)
                )
                db.commit()
                flash(f'{nome} criado com sucesso.')
            except sqlite3.IntegrityError:
                flash(f'Já há um sorteio cadastrado com o nome {nome}.')
            return render_template('admin/novo_sorteio.html')

    return render_template('admin/novo_sorteio.html')


@bp.route('/sortear_bilhete', methods=('GET', 'POST'))
@login_required
def sortear_bilhete():
    db = get_db()

    if request.method == 'POST':
        # Caso 1: escolheu o sorteio para listar e sortear
        if 'sorteio_id' in request.form:
            sorteio_id = request.form.get('sorteio_id')

            bilhetes = db.execute(
                'SELECT * FROM bilhete WHERE id_sorteio = ?',
                (sorteio_id,)
            ).fetchall()

            if len(bilhetes) == 0:
                return render_template(
                    'admin/sortear_bilhete.html',
                    sorteio_escolhido=True,
                    bilhetes_vazio=True
                )

            # Sorteia um bilhete
            sorteado = secrets.choice(bilhetes)
            return render_template(
                'admin/sortear_bilhete.html',
                sorteio_escolhido=True,
                bilhetes_vazio=False,
                validado=False,
                sorteado=sorteado
            )

        # Caso 2: confirmou o bilhete sorteado
        elif 'id_bilhete' in request.form:
            id_bilhete = request.form.get('id_bilhete')

            sorteado = db.execute(
                'SELECT * FROM bilhete WHERE id_bilhete = ?',
                (id_bilhete,)
            ).fetchone()

            if not sorteado:
                flash('Bilhete não encontrado.')
                return redirect(url_for('admin.sortear_bilhete'))

            db.execute(
                'UPDATE sorteio SET realizado = 1, id_bilhete_sorteado = ? '
                'WHERE id_sorteio = ?',
                (sorteado['id_bilhete'], sorteado['id_sorteio'])
            )
            db.commit()

            return render_template(
                'admin/sortear_bilhete.html',
                sorteio_escolhido=True,
                validado=True,
                sorteado=sorteado
            )

    # GET: lista sorteios não realizados para escolher
    sorteios = db.execute(
        'SELECT * FROM sorteio WHERE NOT realizado'
    ).fetchall()

    return render_template(
        'admin/sortear_bilhete.html',
        sorteio_escolhido=False,
        sorteios=sorteios
    )


@bp.route('/consultar_vencedor', methods=('GET', 'POST'))
@login_required
def consultar_vencedor():
    db = get_db()

    sorteios = db.execute(
        'SELECT * FROM sorteio WHERE realizado'
    ).fetchall()

    if request.method == 'POST' and 'sorteio_id' in request.form:
        sorteio_id = request.form.get('sorteio_id')

        sorteado = db.execute(
            'SELECT id_bilhete_sorteado, nome FROM sorteio WHERE id_sorteio = ?',
            (sorteio_id,)
        ).fetchone()

        if not sorteado or not sorteado['id_bilhete_sorteado']:
            flash('Sorteio não possui bilhete sorteado.')
            return render_template(
                'admin/consultar_vencedor.html',
                sorteio_escolhido=False,
                sorteios=sorteios
            )

        vencedor = db.execute(
            'SELECT * FROM bilhete WHERE id_bilhete = ?',
            (sorteado['id_bilhete_sorteado'],)
        ).fetchone()

        return render_template(
            'admin/consultar_vencedor.html',
            sorteio_escolhido=True,
            vencedor=vencedor,
            sorteio=sorteado['nome'],
            sorteios=sorteios
        )

    return render_template(
        'admin/consultar_vencedor.html',
        sorteio_escolhido=False,
        sorteios=sorteios
    )

@bp.route("/depositar_bilhete", methods=("GET", "POST"))
@login_required
def depositar_bilhete():
    db = get_db()

    # carrega SEMPRE os sorteios (usado pelo template em qualquer retorno)
    sorteios = db.execute(
        "SELECT id_sorteio, nome FROM sorteio WHERE NOT realizado ORDER BY id_sorteio DESC"
    ).fetchall()

    if request.method == "POST":
        nome       = (request.form.get("nome") or "").strip()
        sobrenome  = (request.form.get("sobrenome") or "").strip()
        celular    = (request.form.get("celular") or "").strip()
        sorteio_id = request.form.get("sorteio_id")
        codigo_raw = (request.form.get("codigo") or "").strip()

        # validações simples
        if not nome or not sorteio_id or not codigo_raw:
            flash("Preencha nome, sorteio e código.")
            return render_template("bilhetes/depositar_bilhete.html", sorteios=sorteios)

        # código precisa ser número (INTEGER no banco)
        try:
            codigo_int = int(codigo_raw)
        except ValueError:
            flash("O código precisa ser numérico.")
            return render_template("bilhetes/depositar_bilhete.html", sorteios=sorteios)

        # 1) verifica se o código existe para esse sorteio
        existe = db.execute(
            "SELECT 1 FROM codigo WHERE codigo = ? AND id_sorteio = ?",
            (codigo_int, sorteio_id)
        ).fetchone()
        if not existe:
            flash("Código não existe para esse sorteio.")
            return render_template("bilhetes/depositar_bilhete.html", sorteios=sorteios)

        # 2) impede código repetido para o mesmo sorteio em bilhete
        repetido = db.execute(
            "SELECT 1 FROM bilhete WHERE id_sorteio = ? AND codigo = ?",
            (sorteio_id, codigo_int)
        ).fetchone()
        if repetido:
            flash("Este código já foi depositado para este sorteio.")
            return render_template("bilhetes/depositar_bilhete.html", sorteios=sorteios)

        # 3) insere o bilhete
        try:
            db.execute(
                """
                INSERT INTO bilhete (id_sorteio, codigo, nome, sobrenome, celular)
                VALUES (?, ?, ?, ?, ?)
                """,
                (sorteio_id, codigo_int, nome, sobrenome, celular or None)
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Não foi possível salvar o depósito.")
            return render_template("bilhetes/depositar_bilhete.html", sorteios=sorteios)

        flash("Bilhete depositado com sucesso!")
        return redirect(url_for("admin.depositar_bilhete"))

    # GET
    return render_template("bilhetes/depositar_bilhete.html", sorteios=sorteios)




