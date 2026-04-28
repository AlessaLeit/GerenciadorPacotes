"""
Serviço de Pacote - Contém regras de negócio específicas.
Validação de limites de banhos por plano.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, and_
from fastapi import HTTPException
from typing import List, Optional
from datetime import date
from app.models import Pacote, Banho, Agendamento, Cachorro, Cliente, TipoPlano


class PacoteService:    
    """
    Serviço para gerenciar lógica de negócios de pacotes.
    Principal responsabilidade: validar limites de banhos por plano.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def contar_banhos_no_mes(self, pacote_id: int, ano: int, mes: int) -> int:
        """
        Conta quantos banhos foram realizados no mês/ano especificado.
        """
        return self.db.query(Banho).filter(
            and_(
                Banho.pacote_id == pacote_id,
                extract('year', Banho.data_banho) == ano,
                extract('month', Banho.data_banho) == mes
            )
        ).count()
    
    def validar_limite_banhos(
        self, 
        pacote_id: int, 
        data_banho: date
    ) -> None:
        """
        Valida se ainda é possível registrar um banho no pacote para a data especificada.
        """
        pacote = self.db.query(Pacote).filter(Pacote.id == pacote_id).first()
        if not pacote:
            raise HTTPException(status_code=404, detail="Pacote não encontrado")
        
        if not pacote.ativo:
            raise HTTPException(status_code=400, detail="Nao e possivel adicionar banho a um pacote inativo")
        
        limite = pacote.limite_banhos_mes
        
        total_banhos = self.contar_banhos_no_mes(
            pacote_id, 
            data_banho.year, 
            data_banho.month
        )
        
        if total_banhos >= limite:
            raise HTTPException(
                status_code=400,
                detail=f"Limite de banhos excedido para o plano {pacote.tipo_plano.value}. Maximo permitido: {limite} banhos/mes. Ja realizados: {total_banhos} banhos em {data_banho.month:02d}/{data_banho.year}."
            )
    
    def validar_limite_agendamentos(
        self, 
        pacote_id: int, 
        data_banho: date
    ) -> None:
        """
        Valida limites para agendamentos (conta agendamentos no mes).
        """
        pacote = self.db.query(Pacote).filter(Pacote.id == pacote_id).first()
        if not pacote:
            raise HTTPException(status_code=404, detail="Pacote nao encontrado")
        
        if not pacote.ativo:
            raise HTTPException(status_code=400, detail="Pacote inativo")
        
        total_agendamentos = self.db.query(Agendamento).filter(
            and_(
                Agendamento.pacote_id == pacote_id,
                extract('year', Agendamento.data_banho) == data_banho.year,
                extract('month', Agendamento.data_banho) == data_banho.month
            )
        ).count()
        
        limite = pacote.limite_banhos_mes
        
        if total_agendamentos >= limite:
            raise HTTPException(
                status_code=400,
                detail=f"Limite de agendamentos excedido ({limite}). Ja existem {total_agendamentos} no mes."
            )
    
    def registrar_pagamento(
        self, 
        pacote_id: int, 
        valor_pago: float, 
        data_pagamento: date
    ) -> dict:
        pacote = self.db.query(Pacote).options(
            joinedload(Pacote.cachorro).joinedload(Cachorro.cliente)
        ).filter(Pacote.id == pacote_id).first()
        
        if not pacote:
            raise HTTPException(status_code=404, detail="Pacote nao encontrado")
        
        pacote.valor_pago = valor_pago
        pacote.data_pagamento = data_pagamento
        
        self.db.commit()
        self.db.refresh(pacote)
        
        # ... (restante do código de retorno omitido por brevidade)
        return {"id": pacote.id, "status": "pago"}