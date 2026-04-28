"""
Serviço de Relatórios - Gera métricas mensais do negócio.
Calcula receitas, banhos realizados e pacotes em aberto.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, func, and_
from typing import List, Dict, Any, Optional
from datetime import date
from app.models import Pacote, Banho, Cachorro, Cliente, TipoPlano


class RelatorioService:
    """
    Serviço para geração de relatórios mensais.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def gerar_relatorio_mensal(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Gera relatório completo para um mês/ano específico.
        """
        # 1. Total de banhos realizados no mês
        total_banhos = self._contar_banhos_mes(ano, mes)
        
        # 2. Receita prevista (soma de valor_cobrado de pacotes ativos)
        receita_prevista = self._calcular_receita_prevista(ano, mes)
        
        # 3. Receita recebida (soma de valor_pago de pacotes pagos no mês)
        receita_recebida = self._calcular_receita_recebida(ano, mes)
        
        # 4. Pacotes em aberto (sem valor_pago)
        pacotes_em_aberto = self._listar_pacotes_em_aberto()
        
        # 5. Banhos com observações no período
        banhos_com_observacoes = self._listar_banhos_com_observacoes(ano, mes)
        
        return {
            "periodo": {
                "ano": ano,
                "mes": mes,
                "nome_mes": self._nome_mes(mes)
            },
            "resumo": {
                "total_banhos_realizados": total_banhos,
                "receita_prevista": round(receita_prevista, 2),
                "receita_recebida": round(receita_recebida, 2),
                "receita_pendente": round(receita_prevista - receita_recebida, 2),
                "taxa_recebimento": round(
                    (receita_recebida / receita_prevista * 100) if receita_prevista > 0 else 0, 
                    2
                ),
                "total_pacotes_em_aberto": len(pacotes_em_aberto)
            },
            "detalhes": {
                "pacotes_em_aberto": pacotes_em_aberto,
                "banhos_com_observacoes": banhos_com_observacoes
            }
        }
    
    def _contar_banhos_mes(self, ano: int, mes: int) -> int:
        """Conta total de banhos realizados no mês."""
        return self.db.query(Banho).filter(
            and_(
                extract('year', Banho.data_banho) == ano,
                extract('month', Banho.data_banho) == mes
            )
        ).count()
    
    def _calcular_receita_prevista(self, ano: int, mes: int) -> float:
        """Calcula receita prevista baseada em pacotes ativos criados até o mês."""
        pacotes = self.db.query(Pacote).filter(
            and_(
                Pacote.ativo == True,
                extract('year', Pacote.criado_em) <= ano,
                extract('month', Pacote.criado_em) <= mes
            )
        ).all()
        
        return sum(p.valor_cobrado for p in pacotes)
    
    def _calcular_receita_recebida(self, ano: int, mes: int) -> float:
        """Calcula receita efetivamente recebida no mês."""
        resultado = self.db.query(
            func.coalesce(func.sum(Pacote.valor_pago), 0.0)
        ).filter(
            and_(
                Pacote.valor_pago != None,
                extract('year', Pacote.data_pagamento) == ano,
                extract('month', Pacote.data_pagamento) == mes
            )
        ).scalar()
        
        return float(resultado) if resultado else 0.0
    
    def _listar_pacotes_em_aberto(self) -> List[Dict[str, Any]]:
        """Lista todos os pacotes sem pagamento registrado."""
        pacotes = self.db.query(Pacote).options(
            joinedload(Pacote.cachorro).joinedload(Cachorro.cliente)
        ).filter(
            Pacote.valor_pago == None
        ).order_by(Pacote.criado_em.desc()).all()
        
        resultado = []
        for p in pacotes:
            resultado.append({
                "pacote_id": p.id,
                "tipo_plano": p.tipo_plano.value,
                "valor_cobrado": p.valor_cobrado,
                "criado_em": p.criado_em.isoformat(),
                "cachorro": {
                    "id": p.cachorro.id,
                    "nome": p.cachorro.nome,
                    "porte": p.cachorro.porte.value
                },
                "cliente": {
                    "id": p.cachorro.cliente.id,
                    "nome": p.cachorro.cliente.nome,
                    "telefone": p.cachorro.cliente.telefone
                }
            })
        
        return resultado
    
    def _listar_banhos_com_observacoes(self, ano: int, mes: int) -> List[Dict[str, Any]]:
        """Lista banhos que possuem observações registradas."""
        banhos = self.db.query(Banho).options(
            joinedload(Banho.pacote).joinedload(Pacote.cachorro)
        ).filter(
            and_(
                extract('year', Banho.data_banho) == ano,
                extract('month', Banho.data_banho) == mes,
                Banho.observacao != None,
                Banho.observacao != ""
            )
        ).order_by(Banho.data_banho.desc()).all()
        
        resultado = []
        for b in banhos:
            resultado.append({
                "banho_id": b.id,
                "data_banho": b.data_banho.isoformat(),
                "observacao": b.observacao,
                "cachorro": {
                    "id": b.pacote.cachorro.id,
                    "nome": b.pacote.cachorro.nome
                },
                "pacote": {
                    "id": b.pacote.id,
                    "tipo_plano": b.pacote.tipo_plano.value
                }
            })
        
        return resultado
    
    def _nome_mes(self, mes: int) -> str:
        """Retorna nome do mês em português."""
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return meses[mes - 1] if 1 <= mes <= 12 else "Desconhecido"