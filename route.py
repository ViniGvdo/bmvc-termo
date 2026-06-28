from .app.controllers.application import Application
from bottle import Bottle, run, request, static_file

app = Bottle()
ctl = Application()

# -----------------------------------------------------------------------------
# Rotas de Recursos Estáticos:
@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static')

@app.route('/helper')
def helper(info=None):
    return ctl.render('helper')

# -----------------------------------------------------------------------------
# Rota da Interface do Usuário:
@app.route('/pagina', method='GET')
def action_pagina():
    return ctl.render('pagina')

# -----------------------------------------------------------------------------
# Novas Rotas da API para o Jogo Termo:
@app.route('/api/iniciar', method='POST')
def api_iniciar():
    # Obtém o JSON enviado pelo JavaScript frontend
    dados = request.json or {}
    modo = dados.get('modo', 'medio')
    return ctl.novo_jogo(modo)

@app.route('/api/tentativa', method='POST')
def api_tentativa():
    dados = request.json or {}
    palpite = dados.get('palpite', '')
    return ctl.processar_tentativa(palpite)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080, debug=True)