"""
Router Pacotes - CRUD, pagamento, geração automática agend
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Any, Optional

from app.database import get_db
from app import models, schemas
from app.services.pacote_service import PacoteService

router = APIRouter(
    tags=["Pacotes"],
    redirect_slashes=True,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Pacote não encontrado"}}
)

@router.get("/", response_model=List[schemas.PacoteResponse])
def listar_pacotes(
    incluir_inativos: bool = Query(False, description="Incluir pacotes inativos?"),
    db: Session = Depends(get_db)
):
    """Lista pacotes (ativos por padrão; usa incluir_inativos=true para todos)."""
    query = db.query(models.Pacote)\
        .options(
            joinedload(models.Pacote.cachorro).joinedload(models.Cachorro.cliente)
        )\
        .order_by(models.Pacote.criado_em.desc())
    
    if not incluir_inativos:
        query = query.filter(models.Pacote.ativo == True)
    
    pacotes = query.all()
    return pacotes

@router.post("/", response_model=schemas.PacoteResponse, status_code=status.HTTP_201_CREATED)
def criar_pacote(pacote_criar: schemas.PacoteCreate, db: Session = Depends(get_db)):
    """Cria um novo pacote para um cachorro específico."""
    # Verifica se o cachorro existe e é ativo
    cachorro = db.query(models.Cachorro).filter(
        models.Cachorro.id == pacote_criar.cachorro_id,
        models.Cachorro.ativo == True
    ).first()
    if not cachorro:
        raise HTTPException(status_code=404, detail="Cachorro não encontrado ou inativo")
    
    # Cria o pacote
    dados_pacote = pacote_criar.model_dump()
    dados_pacote.pop('limite_banhos_mes', None)
    dados_pacote.pop('status_pagamento', None)
    
    db_pacote = models.Pacote(**dados_pacote)
    db.add(db_pacote)
    db.commit()
    db.refresh(db_pacote)

    # ==============================================================
    # Geração automática de agendamentos para o mês atual.
    # Regra:
    # - Semanal: 4 datas no mesmo dia da semana (dia_da_semana)
    # - Quinzenal: 2 datas com intervalo de 15 dias a partir da 1ª ocorrência no mês
    # - Mensal: 1 data (primeira ocorrência no mês)
    # ==============================================================
    from datetime import date, timedelta
    import calendar


    hoje = date.today()
    primeiro_dia_mes = date(hoje.year, hoje.month, 1)
    ultimo_dia_mes = date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])

    mapa_dow = {
        "terca": 1,   # Segunda=0
        "quarta": 2,
        "quinta": 3,
        "sexta": 4,
        "sabado": 5,
    }

    alvo_dow = mapa_dow.get(db_pacote.dia_da_semana.value)
    if alvo_dow is None:
        raise HTTPException(status_code=400, detail="Dia da semana inválido")

    def primeira_ocorrencia_no_mes() -> Optional[date]:
        d = primeiro_dia_mes
        while d <= ultimo_dia_mes:
            if d.weekday() == alvo_dow:
                return d
            d += timedelta(days=1)
        return None

    primeira = primeira_ocorrencia_no_mes()
    datas: List[date] = []

    if db_pacote.tipo_plano.value == "semanal" and primeira:
        datas = [primeira + timedelta(days=7 * i) for i in range(4)]
    elif db_pacote.tipo_plano.value == "quinzenal" and primeira:
        datas = [primeira + timedelta(days=15 * i) for i in range(2)]
    elif db_pacote.tipo_plano.value == "mensal" and primeira:
        datas = [primeira]

    # Garante que todas datas estão dentro do mês (caso 'primeira' caia no fim do mês)
    datas_validas = [d for d in datas if primeiro_dia_mes <= d <= ultimo_dia_mes]

    # Import aqui para evitar dependência circular no carregamento.
    from app.models import Agendamento

    for d in datas_validas:
        db_ag = Agendamento(

            pacote_id=db_pacote.id,
            data_banho=d,
            status_presenca="pendente",
            extras={},
        )
        db.add(db_ag)

    db.commit()
    db.refresh(db_pacote)

    # Retorna pacote com agendamentos carregados (para a resposta do endpoint)
    db_pacote = (

        db.query(models.Pacote)
        .options(joinedload(models.Pacote.agendamentos))
        .filter(models.Pacote.id == db_pacote.id)
        .first()
    )

    # Em alguns cenários o FastAPI/Pydantic não consegue serializar diretamente o
    # modelo SQLAlchemy quando há tipos não-mapeados (ex.: relacionamento Agendamento).
    # Então, retornamos explicitamente via dict compatível com PacoteResponse.
    # Para o detalhe, a UI usa PacoteDetail.vue que espera agendamentos no payload.
    # Para compatibilidade com a serialização Pydantic, retornamos somente campos escalares + agendamentos.
    # (PacoteResponse.agendamentos é List[Any], então aceitamos dicts).
    pacote_dict = db_pacote.to_dict()
    pacotes_agendamentos = getattr(db_pacote, 'agendamentos', None) or []
    pacote_dict['agendamentos'] = [ag.to_dict() for ag in pacotes_agendamentos]

    return pacote_dict






@router.get("/{pacote_id}", response_model=schemas.PacoteResponse)

def obter_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """Obtém detalhes de um pacote específico com agendamentos."""
    pacote = db.query(models.Pacote)\
        .options(
            joinedload(models.Pacote.cachorro).joinedload(models.Cachorro.cliente),
            joinedload(models.Pacote.agendamentos)
        )\
        .filter(models.Pacote.id == pacote_id)\
        .first()
    if not pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")

    # Evita erro de serialização do relacionamento Agendamento.
    pacote_dict = pacote.to_dict()
    agendamentos = getattr(pacote, 'agendamentos', None) or []
    pacote_dict['agendamentos'] = [ag.to_dict() for ag in agendamentos]
    return pacote_dict


@router.put("/{pacote_id}", response_model=schemas.PacoteResponse)
def atualizar_pacote(pacote_id: int, pacote_atualizar: schemas.PacoteUpdate, db: Session = Depends(get_db)):
    """Atualiza dados do pacote."""
    pacote = db.query(models.Pacote).filter(models.Pacote.id == pacote_id).first()
    if not pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    
    update_data = pacote_atualizar.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pacote, field, value)
    
    db.commit()
    db.refresh(pacote)
    return pacote

@router.delete("/{pacote_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """Remove pacote (soft-delete: seta ativo=False)."""
    pacote = db.query(models.Pacote).filter(models.Pacote.id == pacote_id).first()
    if not pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    pacote.ativo = False
    db.commit()
    return None

@router.patch("/{pacote_id}/pagar", response_model=dict)
def registrar_pagamento(
    pacote_id: int,
    valor_pago: float,
    data_pagamento: str,  # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """Registra pagamento de um pacote usando o serviço."""
    service = PacoteService(db)
    from datetime import date
    data = date.fromisoformat(data_pagamento)
    result = service.registrar_pagamento(pacote_id, valor_pago, data)
    return result

@router.get("/{pacote_id}/agendamentos", response_model=List[schemas.AgendamentoResponse])
def listar_agendamentos_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """Lista agendamentos vinculados a um pacote específico."""
    agendamentos = db.query(models.Agendamento).filter(
        models.Agendamento.pacote_id == pacote_id
    ).order_by(models.Agendamento.data_banho).all()
    return agendamentos

@router.post("/{pacote_id}/agendamento-extra", response_model=schemas.AgendamentoResponse)
def adicionar_agendamento_extra(
    pacote_id: int, 
    data_banho: str, 
    db: Session = Depends(get_db)
):
    """Cria um agendamento extra sem validar o limite do plano."""
    from datetime import date
    db_ag = models.Agendamento(
        pacote_id=pacote_id,
        data_banho=date.fromisoformat(data_banho),
        status_presenca="pendente"
    )
    db.add(db_ag)
    db.commit()
    db.refresh(db_ag)
    return db_ag
