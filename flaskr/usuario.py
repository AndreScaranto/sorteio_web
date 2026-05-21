from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session, current_app
)
from flaskr.auth import usuario_required
from flaskr.db import get_db
from datetime import datetime, timedelta
import sqlite3

bp = Blueprint('usuario', __name__)

@bp.route('/index_usuario')
@usuario_required
def index_usuario():
    return render_template('usuario/index.html')



@bp.route('/participar_sorteio', methods=('GET','POST'))
@usuario_required
def participar_sorteio():
    id_usuario = session["user_id"]
    db = get_db()
    # GET

    with current_app.open_resource('query_usuario.sql') as f:
        sorteios = db.execute(f.read().decode('utf8'),(id_usuario,id_usuario,)).fetchall()

    if request.method == 'GET':
        if sorteios:
            return render_template('usuario/participar_sorteio.html',sorteios=sorteios,sorteios_abertos=True)
        else:
            return render_template('usuario/participar_sorteio.html',get=True,sorteios_abertos=False)        

    # POST
    if request.method == 'POST':
        quantidade = int(request.form.get('quantidade_bilhetes'))
        id_sorteio = int(request.form.get('id_sorteio'))
        valor_por_bilhete = float(request.form.get('valor_por_bilhete'))
        depositados = 0
        with current_app.open_resource('query_usuario.sql') as f:
            query = f.read().decode('utf8') + "\n WHERE sorteio.id_sorteio = ?"
            print(query)
            dados = db.execute(query,(id_usuario,id_usuario,id_sorteio,)).fetchone()
            print(dados)
            while depositados < quantidade and dados["total_comprado"] - dados["valor_convertido"] > valor_por_bilhete:
                db.execute('INSERT INTO bilhete (id_sorteio,id_usuario,valor_depositado) VALUES (?,?,?)', (id_sorteio,id_usuario,valor_por_bilhete,))
                dados = db.execute(query,(id_usuario,id_usuario,id_sorteio,)).fetchone()
                depositados = depositados + 1
        db.commit()
        if depositados == 1:
            flash("Foi depositado 1 bilhete no sorteio " + dados["nome_sorteio"] + ".")
        elif depositados == 0:
            flash("Não foi possível depositar bilhetes.")
        else:
            flash("Foram depositados " + str(depositados) + " bilhetes no sorteio " + dados["nome_sorteio"] + ".")
        with current_app.open_resource('query_usuario.sql') as f:
            sorteios = db.execute(f.read().decode('utf8'),(id_usuario,id_usuario,)).fetchall()
        return render_template('usuario/participar_sorteio.html',sorteios=sorteios,sorteios_abertos=True)



@bp.route('/consultar_compras')
@usuario_required
def consultar_compras():
    id_usuario = session["user_id"]
    db = get_db()
    compras = db.execute(
        'SELECT ' + 
        ' venda.id_venda AS id_venda, ' +
        ' venda.id_usuario AS id_usuario, ' +
        ' venda.preco_venda AS preco, ' +
        ' venda.quantidade_vendida AS quantidade, ' +
        ' venda.data_venda AS data, ' +
        ' produto.nome AS produto ' +
        ' FROM venda ' +
        ' INNER JOIN produto ON venda.id_produto = produto.id_produto '+
         ' WHERE id_usuario = ? ' + 
         ' ORDER BY data_venda DESC', (id_usuario,)
    ).fetchall()
    if compras:
        return render_template('usuario/consultar_compras.html',compra_encontrada=True,compras=compras)
    else:
        return render_template('usuario/consultar_compras.html',compra_encontrada=False)