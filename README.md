# 🏆 Sistema de Placar Eletrônico IoT e API Esportiva

Projeto acadêmico — **Equipe 1**
* **Instituição:** Faculdade de Tecnologia do Senac (FATESE)
* **Curso:** Análise e Desenvolvimento de Sistemas (ADS) - 2º Período
* **Disciplina:** Desenvolvimento de Serviços e APIs
* **Professor:** Carlos Bruno Oliveira Lopes
* **Alunos:** Iris Raiol, Rubem Mateus, Matheus Sasaki, Carlos Eduardo.

Sistema distribuído **Cliente-Servidor** que gerencia e transmite placares de campeonatos em tempo real, com suporte a múltiplas modalidades (Futebol, Basquete, Vôlei e Handebol).

- **Back-end:** Python + **Flask** e Pydantic (API RESTful em JSON).
- **Front-end:** HTML + CSS + JavaScript Vanilla, consumindo a API via *polling* HTTP.
- **Persistência:** Em memória (adequado para a demonstração e escopo acadêmico).

---

## 📁 Estrutura de diretórios

```text
placar-iot/
├── backend/
│   ├── main.py          # Servidor Flask (Rotas da API + entrega do estático)
│   ├── models.py        # Modelos Pydantic (Partida, Time, Evento...)
│   ├── store.py         # Repositório em memória + regras por modalidade
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Dashboard público — partidas em curso
│   ├── admin.html           # Área restrita — criar/excluir partidas
│   ├── partida.html         # Placar ao vivo (somente leitura)
│   ├── controlador.html     # Painel do mesário (+pontos, faltas, tempo)
│   └── static/
│       └── assets/
│           ├── styles.css
│           └── api.js       # Cliente HTTP que conversa com a API
└── README.md

--------------------- Como rodar localmente ---------------------

# 1. Pré-requisitos
Python 3.10+ instalado (python --version).
pip disponível.

# 2. Instalar dependências do backend

cd placar-iot/backend
python -m venv .venv

# Ativar o ambiente virtual:
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

# 3. Subir o servidor
A partir da pasta backend, execute o arquivo principal:

python main.py

-----Acesse diretamente no navegador-----
URL	| Função
http://127.0.0.1:8000/	Dashboard público com as partidas em curso
http://127.0.0.1:8000/admin	Área restrita — criar/excluir partidas
http://127.0.0.1:8000/partida/ID	Visualização do placar ao vivo
http://127.0.0.1:8000/controlador/ID	Painel do mesário (controla a partida)

# Endpoints da API

Método,Rota,Descrição
GET,/api/partidas,Lista todas as partidas
POST,/api/partidas,Cria uma nova partida
GET,/api/partidas/{id},Detalhe / placar ao vivo
DELETE,/api/partidas/{id},Remove uma partida
POST,/api/partidas/{id}/eventos,"Aplica evento (ponto, falta, tempo…)

Exemplo - Criar partida via  cURL

curl -X POST [http://127.0.0.1:8000/api/partidas](http://127.0.0.1:8000/api/partidas) \
  -H "Content-Type: application/json" \
  -d '{
    "modalidade": "basquete",
    "time_casa":      { "nome": "Leões",  "cor": "#1e88e5" },
    "time_visitante": { "nome": "Águias", "cor": "#e53935" },
    "local": "Ginásio Central"
  }'

# Tipos de evento aceitos (POST em /api/partidas/{id}/eventos)

tipo,Parâmetros,Efeito
iniciar,—,Inicia a partida e o cronômetro
pausar,—,Pausa o cronômetro
retomar,—,Retoma o cronômetro
finalizar,—,Encerra a partida
resetar,—,Zera placar/cronômetro
fim_periodo,—,Avança o período (tempo / set / quarto)
ponto,"time, valor?",Soma pontos para o time indicado
falta,time,Soma uma falta para o time indicado

# Regras por modalidade

Quando o evento ponto é enviado sem o campo numérico valor, o back-end aplica automaticamente a pontuação padrão da lógica de negócio:

Modalidade,Pontos por jogada padrão
Futebol,1
Basquete,"2 (envie valor:3 para 3 pontos, valor:1 para lance livre)"
Vôlei,1
Handebol,1