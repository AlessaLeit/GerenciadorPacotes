"""
Router Pacotes - CRUD, pagamento, geração automática agendamentos e listagem.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, timedelta, datetime
from app.database import get_db
from app.models import Pacote, Cachorro, Agendamento
from app.schemas import PacoteCreate, PacoteUpdate, PacoteResponse, PacoteWithBanhos
from app.services.pacote_service import PacoteService  # Import serviço

router = APIRouter(redirect_slashes=True)


@router.post("/", response_model=PacoteResponse, status_code=status.HTTP_201_CREATED)
def criar_pacote(pacote: PacoteCreate, db: Session = Depends(get_db)):
    """
    Cria um novo pacote de banhos para um cachorro.
    GERA AUTOMATICAMENTE agendamentos baseado no tipo_plano.
    """
    # Verifica se cachorro existe
    cachorro = db.query(Cachorro).filter(Cachorro.id == pacote.cachorro_id).first()
    if not cachorro:
        raise HTTPException(status_code=404, detail="Cachorro não encontrado")
    
    db_pacote = Pacote(**pacote.model_dump(exclude={'limite_banhos_mes'}))
    db.add(db_pacote)
    db.commit()
    db.refresh(db_pacote)
    
    # ✅ PASSO 1: Gerar agendamentos automáticos
    service = PacoteService(db)
    start_date = db_pacote.criado_em.date()
    meses = 3  # Gerar para 3 meses à frente
    
    limites = {
        "semanal": 4,
        "quinzenal": 2,
        "mensal": 1
    }
    num_por_mes = limites.get(db_pacote.tipo_plano.value, 1)
    
    current_date = start_date
    for mes in range(meses):
        mes_start = (start_date.replace(day=1) + timedelta(days=30*mes))
        generated = 0
        
        while generated < num_por_mes:
            candidate_date = None
            
            if db_pacote.tipo_plano.value == "semanal":
                # Segunda e Quinta da semana (ajustar para ~4/mês)
                weekday = mes_start.weekday()
                candidate_date = mes_start + timedelta(days=(0 if weekday <=1 else 4-weekday) + generated*3)
            elif db_pacote.tipo_plano.value == "quinzenal":
                candidate_date = mes_start.replace(day=1 if generated==0 else 15)
            else:  # mensal
                candidate_date = mes_start.replace(day=1)
            
            if candidate_date and candidate_date.month == mes_start.month:
                # Validar único e limite
                if db.query(Agendamento).filter(
                    Agendamento.pacote_id == db_pacote.id,
                    Agendamento.data_banho == candidate_date
                ).first():
                    continue  # Já existe, pular
                
                try:
                    service.validar_limite_agendamentos(db_pacote.id, candidate_date)
                    # Criar
                    db_ag = Agendamento(
                        pacote_id=db_pacote.id,
                        data_banho=candidate_date,
                        status_presenca="pendente",
                        extras={}
                    )
                    db.add(db_ag)
                    generated += 1
                except HTTPException:
                    break  # Limite atingido
        
        current_date = mes_start + timedelta(days=30)
    
    db.commit()
    
    return db_pacote.to_dict()


@router.get("/{pacote_id}/agendamentos", response_model=List[dict])
def listar_agendamentos_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """
    Lista TODOS agendamentos do pacote ordenados por data_banho.
    Inclui valor_banho (do pet) e total_dia computado.
    """
    pacote = db.query(Pacote).options(
        joinedload(Pacote.cachorro),
        joinedload(Pacote.agendamentos)
    ).filter(Pacote.id == pacote_id).first()
    
    if not pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    
    agendamentos = []
    valor_banho_base = pacote.cachorro.valor_banho or 0
    
    for ag in pacote.agendamentos:
        extras_total = sum(float(e.get('preco', 0)) for e in (ag.extras or {}).values())
        total_dia = valor_banho_base + extras_total
        
        agendamentos.append({
            **ag.to_dict(),
            "valor_banho": valor_banho_base,
            "total_dia": total_dia
        })
    
    return sorted(agendamentos, key=lambda x: x['data_banho'])


@router.get("/", response_model=List[PacoteResponse])
def listar_pacotes(
    cachorro_id: Optional[int] = Query(None, description="Filtrar por cachorro"),
    ativo: Optional[bool] = Query(True, description="Filtrar por status ativo"),
    incluir_inativos: bool = Query(False, description="Incluir pacotes inativos"),
    db: Session = Depends(get_db)
):
    """
    Lista pacotes com filtros.
    Por padrão retorna apenas ativos, a menos que incluir_inativos=true.
    """
    service = PacoteService(db)
    
    if cachorro_id:
        pacotes = service.listar_pacotes_ativos_por_cachorro(cachorro_id, incluir_inativos)
        return [p.to_dict() for p in pacotes]
    
    query = db.query(Pacote).options(joinedload(Pacote.cachorro))
    if not incluir_inativos:
        query = query.filter(Pacote.ativo == True)
    
    pacotes = query.all()
    return [p.to_dict() for p in pacotes]


@router.get("/{pacote_id}", response_model=PacoteWithBanhos)
def obter_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """
    Obtém detalhes do pacote incluindo banhos realizados.
    """
    service = PacoteService(db)
    pacote = service.get_pacote_com_relacionamentos(pacote_id)
    
    if not pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    
    # Adiciona contagem total de banhos
    pacote.total_banhos_realizados = len(pacote.banhos)
    return pacote.to_dict()


@router.put("/{pacote_id}", response_model=PacoteResponse)
def atualizar_pacote(
    pacote_id: int,
    pacote_update: PacoteUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do pacote (plano, valores, status).
    """
    db_pacote = db.query(Pacote).filter(Pacote.id == pacote_id).first()
    if not db_pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    
    update_data = pacote_update.model_dump(exclude_unset=True, exclude={'limite_banhos_mes'})
    for field, value in update_data.items():
        setattr(db_pacote, field, value)
    
    db.commit()
    db.refresh(db_pacote)
    return db_pacote


@router.post("/{pacote_id}/pagar", response_model=PacoteResponse)
def registrar_pagamento(
    pacote_id: int,
    valor_pago: float,
    data_pagamento: date,
    db: Session = Depends(get_db)
):
    """
    Endpoint específico para registrar pagamento de um pacote.
    """
    service = PacoteService(db)
    return service.registrar_pagamento(pacote_id, valor_pago, data_pagamento)


@router.delete("/{pacote_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """
    Remove um pacote e todos os seus banhos.
    """
    db_pacote = db.query(Pacote).filter(Pacote.id == pacote_id).first()
    if not db_pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    
    db.delete(db_pacote)
    db.commit()
    return None

