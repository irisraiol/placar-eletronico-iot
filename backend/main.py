from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import PartidaCreate, EventoPlacar
from store import store, PartidaNaoEncontrada, OperacaoInvalida
from pydantic import ValidationError
import os

# Configurando os caminhos absolutos para evitar erros de diretório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

# Configurando o Flask para servir a pasta frontend/static como conteúdo estático
app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIR, 'static'))
CORS(app)

# ==========================================
# ROTAS DO FRONT-END (Entregando as telas HTML)
# ==========================================
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(FRONTEND_DIR, 'admin.html')

@app.route('/partida/<id>')
def serve_partida(id):
    return send_from_directory(FRONTEND_DIR, 'partida.html')

@app.route('/controlador/<id>')
def serve_controlador(id):
    return send_from_directory(FRONTEND_DIR, 'controlador.html')

# ==========================================
# ROTAS DA API (A lógica do Back-end)
# ==========================================
def partida_to_dict(partida):
    """Converte o modelo Pydantic para dicionário e injeta o cronômetro para o front-end."""
    d = partida.model_dump()
    d['cronometro_atual'] = partida.tempo_atual()
    return d

@app.route('/api/partidas', methods=['POST'])
def criar_partida():
    try:
        payload = PartidaCreate(**request.json)
        partida = store.criar(payload)
        return jsonify(partida_to_dict(partida)), 201
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400

@app.route('/api/partidas', methods=['GET'])
def listar_partidas():
    return jsonify([partida_to_dict(p) for p in store.listar()])

@app.route('/api/partidas/<partida_id>', methods=['GET'])
def obter_partida(partida_id):
    try:
        return jsonify(partida_to_dict(store.obter(partida_id)))
    except PartidaNaoEncontrada:
        return jsonify({"detail": "Partida não encontrada"}), 404

@app.route('/api/partidas/<partida_id>/eventos', methods=['POST'])
def enviar_evento(partida_id):
    try:
        evento = EventoPlacar(**request.json)
        p = store.aplicar_evento(partida_id, evento)
        return jsonify(partida_to_dict(p))
    except PartidaNaoEncontrada:
        return jsonify({"detail": "Partida não encontrada"}), 404
    except OperacaoInvalida as e:
        return jsonify({"detail": str(e)}), 400
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400

@app.route('/api/partidas/<partida_id>', methods=['DELETE'])
def deletar_partida(partida_id):
    try:
        store.remover(partida_id)
        return '', 204
    except PartidaNaoEncontrada:
        return jsonify({"detail": "Partida não encontrada"}), 404

if __name__ == '__main__':
    # O Front-end espera a API na porta 8000
    app.run(port=8000, debug=True)