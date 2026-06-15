"""
Repositório em memória + regras de pontuação por modalidade.
Para um projeto acadêmico mantemos os dados em memória (dict),
o que é suficiente para demonstrar a arquitetura cliente-servidor.
Em produção bastaria trocar este módulo por uma camada de persistência
(SQLite, Postgres, Redis...) preservando a mesma interface pública.
"""
from __future__ import annotations
from datetime import datetime
from threading import Lock
from typing import Dict, List
from models import (
    EventoPlacar,
    Modalidade,
    Partida,
    PartidaCreate,
    StatusPartida,
    TimeStats,
)
class PartidaNaoEncontrada(Exception):
    pass
class OperacaoInvalida(Exception):
    pass
class PartidaStore:
    """Armazenamento thread-safe das partidas em andamento."""
    def __init__(self) -> None:
        self._partidas: Dict[str, Partida] = {}
        self._lock = Lock()
    # ------------------------------- CRUD ------------------------------- #
    def listar(self) -> List[Partida]:
        with self._lock:
            return list(self._partidas.values())
    def obter(self, partida_id: str) -> Partida:
        with self._lock:
            partida = self._partidas.get(partida_id)
            if partida is None:
                raise PartidaNaoEncontrada(partida_id)
            return partida
    def criar(self, payload: PartidaCreate) -> Partida:
        partida = Partida(
            modalidade=payload.modalidade,
            casa=TimeStats(time=payload.time_casa),
            visitante=TimeStats(time=payload.time_visitante),
            local=payload.local,
        )
        with self._lock:
            self._partidas[partida.id] = partida
        return partida
    def remover(self, partida_id: str) -> None:
        with self._lock:
            if partida_id not in self._partidas:
                raise PartidaNaoEncontrada(partida_id)
            del self._partidas[partida_id]
    # --------------------------- regras de jogo ------------------------- #
    def aplicar_evento(self, partida_id: str, evento: EventoPlacar) -> Partida:
        """Aplica um evento (ponto, falta, controle de tempo)."""
        with self._lock:
            partida = self._partidas.get(partida_id)
            if partida is None:
                raise PartidaNaoEncontrada(partida_id)
            tipo = evento.tipo
            # ----- controles de cronômetro / fluxo ----- #
            if tipo == "iniciar":
                if partida.status != StatusPartida.AGENDADA:
                    raise OperacaoInvalida("Partida já foi iniciada")
                partida.status = StatusPartida.EM_ANDAMENTO
                partida.iniciada_em = datetime.utcnow()
                partida.cronometro_rodando_desde = datetime.utcnow()
                return partida
            if tipo == "pausar":
                if partida.status != StatusPartida.EM_ANDAMENTO:
                    raise OperacaoInvalida("Só é possível pausar partidas em andamento")
                if partida.cronometro_rodando_desde:
                    delta = (
                        datetime.utcnow() - partida.cronometro_rodando_desde
                    ).total_seconds()
                    partida.cronometro_segundos += int(delta)
                    partida.cronometro_rodando_desde = None
                partida.status = StatusPartida.PAUSADA
                return partida
            if tipo == "retomar":
                if partida.status != StatusPartida.PAUSADA:
                    raise OperacaoInvalida("A partida não está pausada")
                partida.status = StatusPartida.EM_ANDAMENTO
                partida.cronometro_rodando_desde = datetime.utcnow()
                return partida
            if tipo == "finalizar":
                if partida.cronometro_rodando_desde:
                    delta = (
                        datetime.utcnow() - partida.cronometro_rodando_desde
                    ).total_seconds()
                    partida.cronometro_segundos += int(delta)
                    partida.cronometro_rodando_desde = None
                partida.status = StatusPartida.FINALIZADA
                partida.finalizada_em = datetime.utcnow()
                return partida
            if tipo == "resetar":
                partida.casa.pontos = 0
                partida.casa.faltas = 0
                partida.casa.sets = 0
                partida.visitante.pontos = 0
                partida.visitante.faltas = 0
                partida.visitante.sets = 0
                partida.periodo = 1
                partida.cronometro_segundos = 0
                partida.cronometro_rodando_desde = None
                partida.status = StatusPartida.AGENDADA
                partida.iniciada_em = None
                partida.finalizada_em = None
                return partida
            if tipo == "fim_periodo":
                partida.periodo += 1
                return partida
            # ----- eventos que exigem identificação do time ----- #
            if evento.time not in ("casa", "visitante"):
                raise OperacaoInvalida("Campo 'time' obrigatório para este evento")
            stats: TimeStats = getattr(partida, evento.time)
            if tipo == "falta":
                stats.faltas += 1
                return partida
            if tipo == "ponto":
                valor = _pontos_padrao(partida.modalidade, evento.valor)
                stats.pontos += valor
                return partida
            raise OperacaoInvalida(f"Evento desconhecido: {tipo}")
def _pontos_padrao(modalidade: Modalidade, valor: int | None) -> int:
    """Define quantos pontos somar de acordo com a modalidade."""
    if valor is not None and valor > 0:
        return valor
    # valores padrão por modalidade quando o cliente não envia 'valor'
    return {
        Modalidade.FUTEBOL: 1,
        Modalidade.BASQUETE: 2,
        Modalidade.VOLEI: 1,
        Modalidade.HANDEBOL: 1,
    }[modalidade]
# instância global utilizada pela API
store = PartidaStore()