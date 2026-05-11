"""Schemas Pydantic v2 para Pacote.

Obs.: mantém compatibilidade com o restante do código já existente.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TipoPlano(str, Enum):
    MENSAL = "mensal"
    QUINZENAL = "quinzenal"
    SEMANAL = "semanal"


class DiaSemana(str, Enum):
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"


class StatusPagamento(str, Enum):
    EM_ABERTO = "em_aberto"
    PAGO = "pago"
    ATRASADO = "atrasado"


class PacoteBase(BaseModel):
    tipo_plano: TipoPlano
    valor_cobrado: float = Field(gt=0)
    limite_banhos_mes: int = Field(ge=1)
    ativo: bool = True

    model_config = ConfigDict(from_attributes=True)


class PacoteCreate(BaseModel):
    cachorro_id: int = Field(..., gt=0)
    tipo_plano: TipoPlano

    # Novo: usado para gerar automaticamente agendamentos
    dia_da_semana: Optional[DiaSemana] = None

    valor_banho_base: float = Field(gt=0)
    valor_cobrado: float = Field(gt=0)
    limite_banhos_mes: Optional[int] = None
    ativo: bool = True


class PacoteUpdate(BaseModel):
    tipo_plano: Optional[TipoPlano] = None
    dia_da_semana: Optional[DiaSemana] = None

    valor_cobrado: Optional[float] = None
    limite_banhos_mes: Optional[int] = None
    ativo: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class PacoteResponse(BaseModel):
    id: int
    cachorro_id: int
    tipo_plano: str

    # Novo: exibido no detalhe do pacote
    dia_da_semana: Optional[DiaSemana] = None

    valor_banho_base: float
    valor_cobrado: float
    valor_pago: Optional[float] = None
    data_pagamento: Optional[date] = None
    ativo: bool
    criado_em: datetime

    pet_nome: Optional[str] = None
    cliente_nome: Optional[str] = None
    status_pagamento: str

    limite_banhos_mes: int
    total_agendamentos: int
    agendamentos: List[Any] = []

    model_config = ConfigDict(from_attributes=True)


class PacoteWithBanhos(PacoteResponse):
    banhos: List[Any] = []


class PacoteWithAgendamentos(PacoteResponse):
    agendamentos: List[Any] = []

