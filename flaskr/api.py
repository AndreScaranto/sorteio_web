# flaskr/admin.py
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, jsonify
)
from flaskr.auth import admin_required
from flaskr.db import get_db
from datetime import datetime, timedelta
import sqlite3

import plotly.express as px
import pandas as pd
import plotly.utils
import json

bp = Blueprint('api', __name__)

def get_vendas_dataframe(dias):
    db = get_db()
    query = """
        SELECT 
            produto.nome, usuario.username, 
            (venda.preco_venda * venda.quantidade_vendida) AS receita,
			venda.data_venda
        FROM venda 
        INNER JOIN produto ON venda.id_produto = produto.id_produto
        INNER JOIN usuario ON venda.id_usuario = usuario.id_usuario
        WHERE venda.data_venda >= date('now', :filtro)
        ORDER BY data_venda,nome ASC
    """
    df = pd.read_sql_query(query, db, params={'filtro': f'-{dias} days'})
    return df

def get_clientes_dataframe(dias):
    db = get_db()
    query = """
        SELECT 
            usuario.username,
            SUM (venda.preco_venda * venda.quantidade_vendida) AS receita 
        FROM venda 
        INNER JOIN usuario ON venda.id_usuario = usuario.id_usuario
        WHERE venda.data_venda >= date('now', :filtro)
        GROUP BY usuario.username 
        ORDER BY receita DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, db, params={'filtro': f'-{dias} days'})
    return df

def get_produtos_dataframe(dias):
    db = get_db()
    query = """
        SELECT 
            produto.nome,
            SUM (venda.preco_venda * venda.quantidade_vendida) AS receita
        FROM venda 
        INNER JOIN produto ON venda.id_produto = produto.id_produto
        WHERE venda.data_venda >= date('now', :filtro)
        GROUP BY produto.nome 
        ORDER BY receita DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, db, params={'filtro': f'-{dias} days'})
    return df

@bp.route('/grafico')
@admin_required
def grafico():
    dias = request.args.get('dias', 30, type=int)
    tipo = request.args.get('tipo', 'vendas')
    if tipo == 'vendas':
        return grafico_vendas(dias)
    elif tipo == 'cliente':
        return grafico_clientes(dias)
    elif tipo == 'produto':
        return grafico_produtos(dias)

def empacotar_json(fig):
    chart_json = json.loads(fig.to_json())
    return jsonify(chart_json)

def grafico_vendas(dias):
    df = get_vendas_dataframe(dias)
    #df['semana'] = df.apply(lambda s: s['data_venda'].week, axis=1)
    df['data_venda'] = pd.to_datetime(df['data_venda']).dt.date
    #filtro_dias = df['data_venda'] > datetime.today()- timedelta(days=dias)
    #df = df[filtro_dias]
    df.rename(columns={'receita':'Receita','data_venda':'Data','nome':'Produto','username':'Cliente'},inplace=True)
    fig = px.bar(df, x='Data', y='Receita',hover_data = ['Receita','Data','Produto','Cliente'],color='Produto')
    fig.update_layout(
        #xaxis_title="Data",
        #yaxis_title="Receita",
        yaxis_tickprefix="R$ ",
        yaxis_tickformat = ',.2f',
        title="Histórico de Vendas")
    return empacotar_json(fig)

def grafico_clientes(dias):
    df = get_clientes_dataframe(dias)
    #df['receita'] = df['preco_venda'] * df['quantidade_vendida']
    df.rename(columns={'receita':'Receita','username':'Cliente'},inplace=True)
    fig = px.bar(df,x='Receita', y='Cliente', orientation='h', color='Cliente')
    fig.update_layout(
        title="Vendas por Cliente",
        xaxis_title="Receita",
        xaxis_tickprefix="R$ ",
        xaxis_tickformat = ',.2f',
        yaxis_title="Cliente",
        yaxis={'categoryorder':'total ascending'}
    )
    #fig.show()
    return empacotar_json(fig)

def grafico_produtos(dias):
    df = get_produtos_dataframe(dias)
    df.rename(columns={'receita':'Receita','nome':'Produto'},inplace=True)
    fig = px.bar(df,x='Produto', y='Receita',color='Produto')
    fig.update_layout(
        title="Vendas por Produto",
        #xaxis_title="Produto",
        yaxis_tickprefix="R$ ",
        yaxis_tickformat = ',.2f',
        #yaxis_title="Receita"
    )
    #fig.show()
    return empacotar_json(fig)