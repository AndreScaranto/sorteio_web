# flaskr/auth.py  — versão SQLite usando get_db()
import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db   # usa nosso helper (sqlite3.Row)

bp = Blueprint("auth", __name__)

@bp.route('/')
def index():
    return render_template('auth/index.html')

@bp.route("/login_admin", methods=("GET", "POST"))
def login_admin():
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

            if not ok:
                error = "Senha incorreta."

        if error is None:
            session.clear()
            session["user_id"] = user["id_admin"]
            session["auth_type"] = "admin"
            return redirect(url_for("admin.index_admin"))

        flash(error)

    return render_template("auth/login_admin.html")


@bp.route("/login_usuario", methods=("GET", "POST"))
def login_usuario():
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
            "SELECT id_usuario, username, password FROM usuario WHERE username = ?",
            (username,)
        ).fetchone()

        error = None
        if user is None:
            error = "Nome de usuário incorreto."
        else:
            stored = user["password"] or ""
            ok = False

            try:
                ok = check_password_hash(stored, password)
            except Exception:
                ok = False

            if not ok:
                error = "Senha incorreta."

        if error is None:
            session.clear()
            session["user_id"] = user["id_usuario"]
            session["auth_type"] = "usuario"
            return redirect(url_for("usuario.index_usuario"))

        flash(error)

    return render_template("auth/login_usuario.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    auth_type = session.get("auth_type")
    if user_id is None:
        g.admin = None
        g.usuario = None
    elif auth_type == "admin":
        db = get_db()
        g.admin = db.execute(
            "SELECT id_admin, username, password FROM administrador WHERE id_admin = ?",
            (user_id,)
        ).fetchone()
        g.usuario = None
    elif auth_type == "usuario":
        db = get_db()
        g.usuario = db.execute(
            "SELECT id_usuario, username, password FROM usuario WHERE id_usuario = ?",
            (user_id,)
        ).fetchone()
        g.admin = None
    


@bp.route("/logout_admin")
def logout_admin():
    session.clear()
    return redirect(url_for("admin.index_admin"))


@bp.route("/logout_usuario")
def logout_usuario():
    session.clear()
    return redirect(url_for("auth.index"))

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for("auth.login_admin"))
        return view(**kwargs)
    return wrapped_view


def usuario_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.usuario is None:
            return redirect(url_for("auth.login_usuario"))
        return view(**kwargs)
    return wrapped_view

@bp.route("/alterar_admin", methods=("GET", "POST"))
@admin_required
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
@admin_required
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


@bp.route("/cadastrar_usuario", methods=("GET", "POST"))
def cadastrar_usuario():
    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("senha", "")
        cpf = request.form.get("cpf", "")
        celular = request.form.get("celular", "")
        db = get_db()
        error = None

        if not username:
            error = "Preencha seu nome de usuário."
        elif not password:
            error = "Preencha sua senha."
        elif not cpf:
            error = "Preencha o CPF."
        elif not celular:
            error = "Preencha o celular."

        if error is None:

            dup = db.execute(
                "SELECT 1 FROM usuario WHERE cpf = ?",
                (cpf,)
            ).fetchone()
            if dup:
                error = f"Já há um usuário cadastrado com o CPF {cpf}."
            else:
                db.execute(
                    "INSERT INTO usuario (username, password, cpf,celular) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password), cpf, celular)
                )
                db.commit()
                flash(f"Novo usuario cadastrado com o nome {username} com sucesso.")
                return render_template("auth/cadastrar_usuario.html", resultado=(True, username))

        flash(error)
    return render_template("auth/cadastrar_usuario.html")