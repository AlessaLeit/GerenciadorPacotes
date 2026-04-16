"""
Router Clientes - CRUD completo e listagem com cachorros.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models import Cliente, Cachorro
from app.schemas import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteWithCachorros
from app.schemas.cachorro import CachorroCreate, CachorroResponse, CachorroUpdate

router = APIRouter(redirect_slashes=True)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Cria um novo cliente.
    """
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@router.get("", response_model=List[ClienteWithCachorros])
def listar_clientes(
    skip: int = Query(0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    busca: Optional[str] = Query(None, description="Buscar por nome"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os clientes com paginação e busca opcional por nome.
    """
    query = db.query(Cliente).options(
        joinedload(Cliente.cachorros)
    )
    
    if busca:
        query = query.filter(Cliente.nome.ilike(f"%{busca}%"))
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes


@router.get("/{cliente_id}", response_model=ClienteWithCachorros)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Obtém detalhes de um cliente específico incluindo seus cachorros.
    """
    cliente = db.query(Cliente).options(
        joinedload(Cliente.cachorros)
    ).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: int, 
    cliente_update: ClienteUpdate, 
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de um cliente (atualização parcial suportada).
    """
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Atualiza apenas campos fornecidos
    update_data = cliente_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cliente, field, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Remove um cliente e todos os seus cachorros (cascade).
    """
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(db_cliente)
    db.commit()
    return None


@router.get("/{cliente_id}/cachorros", response_model=List[CachorroResponse])
def listar_cachorros_cliente(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Lista cachorros de um cliente específico.
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cachorros = db.query(Cachorro).filter(Cachorro.cliente_id == cliente_id).offset(skip).limit(limit).all()
    return cachorros


@router.post("/{cliente_id}/cachorros", response_model=CachorroResponse, status_code=status.HTTP_201_CREATED)
def criar_cachorro_cliente(
    cliente_id: int,
    cachorro: CachorroCreate,
    db: Session = Depends(get_db)
):
    """
    Cria cachorro para cliente específico.
    """
    if cachorro.cliente_id and cachorro.cliente_id != cliente_id:
        raise HTTPException(status_code=400, detail="cliente_id no body deve coincidir com path")
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    data = cachorro.model_dump()
    data['cliente_id'] = cliente_id
    db_cachorro = Cachorro(**data)
    db.add(db_cachorro)
    db.commit()
    db.refresh(db_cachorro)
    return db_cachorro


@router.get("/{cliente_id}/cachorros/{cachorro_id}", response_model=CachorroResponse)
def obter_cachorro_cliente(cliente_id: int, cachorro_id: int, db: Session = Depends(get_db)):
    """
    Obtém cachorro específico de um cliente.
    """
    cachorro = db.query(Cachorro).filter(
        Cachorro.id == cachorro_id,
        Cachorro.cliente_id == cliente_id
    ).first()
    if not cachorro:
        raise HTTPException(status_code=404, detail="Cachorro não encontrado para este cliente")
    return cachorro


@router.put("/{cliente_id}/cachorros/{cachorro_id}", response_model=CachorroResponse)
def atualizar_cachorro_cliente(
    cliente_id: int,
    cachorro_id: int,
    cachorro_update: CachorroUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza cachorro específico de um cliente.
    """
    db_cachorro = db.query(Cachorro).filter(
        Cachorro.id == cachorro_id,
        Cachorro.cliente_id == cliente_id
    ).first()
    if not db_cachorro:
        raise HTTPException(status_code=404, detail="Cachorro não encontrado para este cliente")
    
    update_data = cachorro_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cachorro, field, value)
    db.commit()
    db.refresh(db_cachorro)
    return db_cachorro


@router.delete("/{cliente_id}/cachorros/{cachorro_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cachorro_cliente(cliente_id: int, cachorro_id: int, db: Session = Depends(get_db)):
    """
    Deleta cachorro específico de um cliente.
    """
    db_cachorro = db.query(Cachorro).filter(
        Cachorro.id == cachorro_id,
        Cachorro.cliente_id == cliente_id
    ).first()
    if not db_cachorro:
        raise HTTPException(status_code=404, detail="Cachorro não encontrado para este cliente")
    
    db.delete(db_cachorro)
    db.commit()
    return None
