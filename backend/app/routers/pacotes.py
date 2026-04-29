"""
Router Pacotes - CRUD, pagamento, geração automática agend
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.pacote_service import PacoteService

router = APIRouter(
    prefix="/pacotes",
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
    db_pacote = models.Pacote(**pacote_criar.dict())
    db.add(db_pacote)
    db.commit()
    db.refresh(db_pacote)
    return db_pacote

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
    return pacote

@router.put("/{pacote_id}", response_model=schemas.PacoteResponse)
def atualizar_pacote(pacote_id: int, pacote_atualizar: schemas.PacoteUpdate, db: Session = Depends(get_db)):
    """Atualiza dados do pacote."""
    pacote = db.query(models.Pacote).filter(models.Pacote.id == pacote_id).first()
    if not pacote:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")
    
    update_data = pacote_atualizar.dict(exclude_unset=True)
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
