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
        error = None
        user = db.execute(
            'SELECT * FROM administrador WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('admin.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM administrador WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
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
                test_password = db.execute(
                    "SELECT * FROM administrador WHERE username = ?",
                    (old_username, ),
                ).fetchone()
                if (check_password_hash(test_password['password'],old_password)):
                    db.execute(
                        "DELETE FROM administrador WHERE username = ?",
                        (old_username,),
                    )
                    db.execute(
                        "INSERT INTO administrador (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                    user = db.execute(
                        'SELECT * FROM administrador WHERE username = ?', (username,)
                    ).fetchone()
                    session.clear()
                    session['user_id'] = user['id']
                    flash("Dados alterados com sucesso")
            except db.IntegrityError:
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
                test_password = db.execute(
                    "SELECT * FROM administrador WHERE username = ?",
                    (username, ),
                ).fetchone()
                if (check_password_hash(test_password['password'],password)):
                    db.execute(
                        "INSERT INTO administrador (username, password) VALUES (?, ?)",
                        (new_username, generate_password_hash(new_password)),
                    )
                    db.commit()
                    flash(f"Novo administrador cadastrado com o nome {new_username} com sucesso.")
            except db.IntegrityError:
                error = f"Já há um administrador cadastrado com o nome {new_username}."
            else:
                return render_template('auth/adicionar_admin.html',resultado=(True,username))

        flash(error)

    return render_template('auth/adicionar_admin.html')