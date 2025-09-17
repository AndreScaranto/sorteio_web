<<<<<<< HEAD
# flaskr/auth.py  — versão SQLite usando get_db()
import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db   # usa nosso helper (sqlite3.Row)

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        # aceita vários nomes de campo pra evitar mismatch
        username = (
            request.form.get("usuario")
            or request.form.get("username")
            or request.form.get("login")
            or ""
        ).strip()
        password = request.form.get("senha") or request.form.get("password") or ""

        db = get_db()
        user = db.execute(
            "SELECT id_admin, username, password FROM administrador WHERE username = ?",
            (username,)
        ).fetchone()

        error = None
        if user is None:
            error = "Nome de usuário incorreto."
        else:
            stored = user["password"] or ""
            ok = False
            # tenta como hash (werkzeug)
            try:
                ok = check_password_hash(stored, password)
            except Exception:
                ok = False
            # fallback: se no banco estiver texto puro, aceita também
            if not ok and stored == password:
                ok = True

            if not ok:
                error = "Senha incorreta."

        if error is None:
            session.clear()
            session["user_id"] = user["id_admin"]
            return redirect(url_for("admin.index"))

        flash(error)

    return render_template("auth/login.html")

=======
import mysql.connector as mysql # type: ignore

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')    


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['senha']
        db = get_db()
        cur = db.cursor(buffered = True)
        cur.execute(
            "SELECT * FROM administrador WHERE username = (%s)", (username,)
        )
        user = dict(zip(cur.column_names, cur.fetchone()))
        error = None
        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id_admin']
            return redirect(url_for('admin.index'))

        flash(error)

    return render_template('auth/login.html')
>>>>>>> 32afeb09a2eb65cefe44a1447c4d6a94da14dcd1


@bp.before_app_request
def load_logged_in_user():
<<<<<<< HEAD
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            "SELECT id_admin, username, password FROM administrador WHERE id_admin = ?",
            (user_id,)
        ).fetchone()


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.index"))
=======
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cur = get_db().cursor(buffered = True)
        cur.execute(
            'SELECT * FROM administrador WHERE id_admin = %s', (user_id,)
        )
        g.user = cur.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
>>>>>>> 32afeb09a2eb65cefe44a1447c4d6a94da14dcd1


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
<<<<<<< HEAD
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


@bp.route("/alterar_admin", methods=("GET", "POST"))
@login_required
def alterar_admin():
    if request.method == "POST":
        username = request.form.get("usuario_novo", "").strip()
        password = request.form.get("senha_nova", "")
        old_username = request.form.get("usuario", "").strip()
        old_password = request.form.get("senha", "")
        db = get_db()
        error = None

        if not old_username:
            error = "Preencha o nome de usuário antigo."
        elif not old_password:
            error = "Preencha a senha antiga."
        elif not username:
            error = "Preencha o nome de usuário novo."
        elif not password:
            error = "Preencha a senha nova."

        if error is None:
            # verifica senha antiga
            row = db.execute(
                "SELECT id_admin, username, password FROM administrador WHERE username = ?",
                (old_username,)
            ).fetchone()

            if row is None or not check_password_hash(row["password"], old_password):
                error = "Usuário ou senha antiga inválidos."
            else:
                # atualiza: aqui vou trocar a senha do mesmo usuário (mais simples)
                db.execute(
                    "UPDATE administrador SET username = ?, password = ? WHERE id_admin = ?",
                    (username, generate_password_hash(password), row["id_admin"])
                )
                db.commit()
                session.clear()
                session["user_id"] = row["id_admin"]
                flash("Dados alterados com sucesso")
                return redirect(url_for("admin.index"))

        flash(error)
    return render_template("auth/alterar_admin.html")


@bp.route("/adicionar_admin", methods=("GET", "POST"))
@login_required
def adicionar_admin():
    if request.method == "POST":
        new_username = request.form.get("usuario_novo", "").strip()
        new_password = request.form.get("senha_nova", "")
        username = request.form.get("usuario", "").strip()
        password = request.form.get("senha", "")
        db = get_db()
        error = None

        if not username:
            error = "Preencha seu nome de usuário."
        elif not password:
            error = "Preencha sua senha."
        elif not new_username:
            error = "Preencha o nome de usuário novo."
        elif not new_password:
            error = "Preencha a senha nova."

        if error is None:
            # valida o admin atual
            row = db.execute(
                "SELECT id_admin, username, password FROM administrador WHERE username = ?",
                (username,)
            ).fetchone()

            if row is None or not check_password_hash(row["password"], password):
                error = "Usuário/senha inválidos."
            else:
                # verifica duplicidade de username novo
                dup = db.execute(
                    "SELECT 1 FROM administrador WHERE username = ?",
                    (new_username,)
                ).fetchone()
                if dup:
                    error = f"Já há um administrador cadastrado com o nome {new_username}."
                else:
                    db.execute(
                        "INSERT INTO administrador (username, password) VALUES (?, ?)",
                        (new_username, generate_password_hash(new_password))
                    )
                    db.commit()
                    flash(f"Novo administrador cadastrado com o nome {new_username} com sucesso.")
                    return render_template("auth/adicionar_admin.html", resultado=(True, username))

        flash(error)
    return render_template("auth/adicionar_admin.html")
=======
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/alterar_admin', methods=('GET', 'POST'))
@login_required
def alterar_admin():
    if request.method == 'POST':
        username = request.form['usuario_novo']
        password = request.form['senha_nova']
        old_username = request.form['usuario']
        old_password = request.form['senha']
        db = get_db()
        error = None
        cur = db.cursor()

        if not old_username:
            error = 'Preencha o nome de usuário antigo.'
        elif not old_password:
            error = 'Preencha a senha antiga.'
        elif not username:
            error = 'Preencha o nome de usuário novo.'
        elif not password:
            error = 'Preencha a senha nova.'

        if error is None:
            try:
                cur.execute(
                    "SELECT * FROM administrador WHERE username = %s",
                    (old_username, ),
                )
                test_password = dict(zip(cur.column_names, cur.fetchone()))
                if (check_password_hash(test_password['password'],old_password)):
                    cur.execute(
                        "DELETE FROM administrador WHERE username = %s",
                        (old_username,),
                    )
                    cur.execute(
                        "INSERT INTO administrador (username, password) VALUES (%s, %s)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                    cur.execute(
                        'SELECT * FROM administrador WHERE username = %s', (username,)
                    )
                    user = dict(zip(cur.column_names, cur.fetchone()))
                    session.clear()
                    session['user_id'] = user['id_admin']
                    flash("Dados alterados com sucesso")
            except mysql.IntegrityError:
                error = f"Já há um administrador cadastrado com o nome {username}."
            else:
                return redirect(url_for("admin.index"))

        flash(error)

    return render_template('auth/alterar_admin.html')

@bp.route('/adicionar_admin', methods=('GET', 'POST'))
@login_required
def adicionar_admin():
    if request.method == 'POST':
        new_username = request.form['usuario_novo']
        new_password = request.form['senha_nova']
        username = request.form['usuario']
        password = request.form['senha']
        db = get_db()
        cur = db.cursor()
        error = None

        if not username:
            error = 'Preencha seu nome de usuário.'
        elif not password:
            error = 'Preencha sua senha.'
        elif not new_username:
            error = 'Preencha o nome de usuário novo.'
        elif not new_password:
            error = 'Preencha a senha nova.'

        if error is None:
            try:
                cur.execute(
                    "SELECT * FROM administrador WHERE username = %s",
                    (username, ),
                )
                test_password = dict(zip(cur.column_names, cur.fetchone()))
                if (check_password_hash(test_password['password'],password)):
                    cur.execute(
                        "INSERT INTO administrador (username, password) VALUES (%s, %s)",
                        (new_username, generate_password_hash(new_password)),
                    )
                    db.commit()
                    flash(f"Novo administrador cadastrado com o nome {new_username} com sucesso.")
                 
            except mysql.IntegrityError:
                error = f"Já há um administrador cadastrado com o nome {new_username}."
            else:
                return render_template('auth/adicionar_admin.html',resultado=(True,username))

        flash(error)

    return render_template('auth/adicionar_admin.html')
>>>>>>> 32afeb09a2eb65cefe44a1447c4d6a94da14dcd1
