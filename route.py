import os
from app.controllers.application import Application
from bottle import Bottle, run, request, static_file

app = Bottle()
ctl = Application()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    static_root = os.path.join(BASE_DIR, 'app', 'static')
    return static_file(filepath, root=static_root)

@app.route('/pagina', method='GET') 
def action_pagina():
    return ctl.render('pagina')

@app.route('/rankings', method='GET') 
def action_rankings():
    return ctl.render('rankings')

@app.route('/', method='GET') 
def action_index():
    return ctl.render('index')

@app.route('/api/iniciar', method='POST') 
def api_iniciar():
    dados = request.json or {}
    modo = dados.get('modo', 'medio')
    username = dados.get('username', 'Convidado') 
    return ctl.novo_jogo(modo, username)

@app.route('/api/tentativa', method='POST') 
def api_tentativa():
    dados = request.json or {}
    palpite = dados.get('palpite', '')
    return ctl.processar_tentativa(palpite)

@app.route('/api/rankings', method='GET') 
def api_rankings():
    return ctl.obter_rankings_data()

if __name__ == '__main__':
    run(app, host='127.0.0.1', port=8080, debug=True)