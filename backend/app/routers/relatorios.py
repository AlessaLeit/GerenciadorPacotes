"""
Router Relatórios - Endpoints para geração de relatórios mensais.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.services.relatorio_service import RelatorioService

router = APIRouter(redirect_slashes=True)


@router.get("/mensal")
def relatorio_mensal(
    ano: int = Query(..., ge=2020, le=2030, description="Ano do relatório"),
    mes: int = Query(..., ge=1, le=12, description="Mês do relatório (1-12)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Gera relatório mensal completo com:
    - Total de banhos realizados
    - Receita prevista vs recebida
    - Pacotes em aberto (para cobrança)
    - Banhos com observações especiais
    """
    service = RelatorioService(db)
    return service.gerar_relatorio_mensal(ano, mes)


@router.get("/mensal/resumo")
def resumo_mensal(
    ano: int = Query(..., ge=2020, le=2030),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retorna apenas o resumo numérico do mês (para dashboards).
    """
    service = RelatorioService(db)
    relatorio = service.gerar_relatorio_mensal(ano, mes)
    return relatorio["resumo"]