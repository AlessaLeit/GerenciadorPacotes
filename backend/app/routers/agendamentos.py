"""
Router Agendamentos - CRUD básico e edição status/extras.
Integra com pacote_service para validações.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Agendamento
from app.schemas import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse
from app.services.pacote_service import PacoteService
from app.models import Pacote, Cachorro, Cliente
from datetime import date
from app.models import Pacote, Cachorro

router = APIRouter(tags=["Agendamentos"], redirect_slashes=True)

@router.post("/", response_model=AgendamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_agendamento(agendamento: AgendamentoCreate, db: Session = Depends(get_db)):
    """
    Cria novo agendamento para pacote (valida limite).
    """
    service = PacoteService(db)
    service.validar_limite_agendamentos(agendamento.pacote_id, agendamento.data_banho)
    
    db_ag = Agendamento(**agendamento.model_dump())
    db.add(db_ag)
    db.commit()
    db.refresh(db_ag)
    return db_ag

@router.get("/", response_model=List[AgendamentoResponse])
def listar_agendamentos(pacote_id: int, db: Session = Depends(get_db)):
    """
    Lista agendamentos de um pacote (ordenados por data_banho).
    """
    agendamentos = db.query(Agendamento).filter(
        Agendamento.pacote_id == pacote_id
    ).order_by(Agendamento.data_banho).all()
    return agendamentos

@router.get("/dashboard/{data}")
def listar_agendamentos_data(data: str, db: Session = Depends(get_db)):
        """
        Lista agendamentos de data específica (YYYY-MM-DD) para dashboard.
        Default: hoje se inválida. Inclui pet.nome, cliente.nome, pacote.id.
        """
        try:
            target_date = date.fromisoformat(data)
        except ValueError:
            target_date = date.today()

        agendamentos = (db.query(Agendamento)
            .join(Pacote)
            .outerjoin(Cachorro)
            .filter(Agendamento.data_banho == target_date)
            .order_by(Agendamento.registrado_em.desc())
            .all()
        )

        result = []
        for ag in agendamentos:
            ag_dict = ag.to_dict()
            ag_dict["pet_nome"] = ag.pacote.cachorro.nome if ag.pacote and ag.pacote.cachorro else "Pet não encontrado"
            ag_dict["cliente_nome"] = (ag.pacote.cachorro.cliente.nome if ag.pacote 
                                     and ag.pacote.cachorro 
                                     and ag.pacote.cachorro.cliente 
                                     else "Cliente não encontrado")
            result.append(ag_dict)
        
        return result


@router.put("/{agendamento_id}", response_model=AgendamentoResponse)
def atualizar_agendamento(
    agendamento_id: int,
    update_data: AgendamentoUpdate,
    db: Session = Depends(get_db)
):
    """
    Edita status_presenca e extras (retroativo permitido, sem trava de data).
    """
    db_ag = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not db_ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(db_ag, field, value)
    
    db.commit()
    db.refresh(db_ag)
    return db_ag


@router.put("/{agendamento_id}/data", response_model=AgendamentoResponse)
def atualizar_data_agendamento(
    agendamento_id: int,
    data_banho: date,
    db: Session = Depends(get_db)
):
    """
    Edita APENAS a data_banho de um agendamento.
    Permite qualquer dia (retroativo ou futuro).
    """
    db_ag = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not db_ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    db_ag.data_banho = data_banho
    
    db.commit()
    db.refresh(db_ag)
    return db_ag


@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    """
    Remove agendamento.
    """
    db_ag = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not db_ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    db.delete(db_ag)
    db.commit()
    return None

