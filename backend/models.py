"""
Modelos de dados (Pydantic) do Sistema de Placar Eletrônico IoT.
Equipe 1 - Sistema de Placar Eletrônico IoT e API Esportiva.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class Modalidade(str, Enum):
    """Modalidades esportivas suportadas pelo sistema."""
    FUTEBOL = "futebol"
    BASQUETE = "basquete"
    VOLEI = "volei"
    HANDEBOL = "handebol"
class StatusPartida(str, Enum):
    AGENDADA = "agendada"
    EM_ANDAMENTO = "em_andamento"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"

# ---------------------------------------------------------------------------
# Entidades
# ---------------------------------------------------------------------------
class Time(BaseModel):
    """Representa uma equipe participante de uma partida."""
    nome: str = Field(..., min_length=1, max_length=60)
    cor: str = Field("#1e88e5", description="Cor hex usada na UI, ex: #ff0000")
class TimeStats(BaseModel):
    """Estatísticas (pontuação e faltas) de um time em uma partida."""
    pontos: int = 0
    faltas: int = 0
    sets: int = 0  # usado em vôlei
    time: Time
class PartidaCreate(BaseModel):
    """Payload de criação de partida (entrada da API)."""
    modalidade: Modalidade
    time_casa: Time
    time_visitante: Time
    local: Optional[str] = None
class EventoPlacar(BaseModel):
    """Ação executada pelo mesário sobre a partida."""
    tipo: Literal[
        "ponto",
        "falta",
        "fim_periodo",
        "iniciar",
        "pausar",
        "retomar",
        "finalizar",
        "resetar",
    ]
    time: Optional[Literal["casa", "visitante"]] = None
    valor: Optional[int] = Field(None, description="Quantos pontos somar (1, 2 ou 3)")
class Partida(BaseModel):
    """Estado completo de uma partida em memória."""
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    modalidade: Modalidade
    status: StatusPartida = StatusPartida.AGENDADA
    casa: TimeStats
    visitante: TimeStats
    periodo: int = 1
    local: Optional[str] = None
    criada_em: datetime = Field(default_factory=datetime.utcnow)
    iniciada_em: Optional[datetime] = None
    finalizada_em: Optional[datetime] = None
    cronometro_segundos: int = 0  # tempo decorrido (acumulado)
    cronometro_rodando_desde: Optional[datetime] = None
    # ----------------------- helpers de cronômetro ------------------------
    def tempo_atual(self) -> int:
        """Tempo total decorrido em segundos (inclui período corrente)."""
        base = self.cronometro_segundos
        if self.cronometro_rodando_desde is not None:
            delta = (datetime.utcnow() - self.cronometro_rodando_desde).total_seconds()
            base += int(delta)
        return base