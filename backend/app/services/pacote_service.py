# Imports obrigatórios
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from app.models import Pacote

# Classe do serviço para gerenciar pacotes
class PacoteService:
    # Construtor que recebe a sessão do banco de dados
    def __init__(self, db):
        self.db = db

    # Método para listar pacotes ativos de um cachorro, com opção de incluir inativos
    def listar_pacotes_ativos_por_cachorro(self, cachorro_id, incluir_inativos=False):
        query = self.db.query(Pacote).filter(Pacote.cachorro_id == cachorro_id)
        if not incluir_inativos:
            query = query.filter(Pacote.ativo == True)
        return query.order_by(Pacote.id.desc()).all()

    # Método para obter um pacote com seus relacionamentos (cachorro e banhos)
    def get_pacote_com_relacionamentos(self, pacote_id):
        return self.db.query(Pacote).options(joinedload(Pacote.cachorro), joinedload(Pacote.banhos)).filter(Pacote.id == pacote_id).first()

    # Método para registrar um pagamento em um pacote
    def registrar_pagamento(self, pacote_id, valor_pago, data_pagamento):
        pacote = self.db.query(Pacote).filter(Pacote.id == pacote_id).first()
        if not pacote:
            raise HTTPException(status_code=404, detail='Pacote não encontrado')
        pacote.valor_pago = (pacote.valor_pago or 0) + valor_pago
        pacote.data_pagamento = data_pagamento
        valor_referencia = pacote.valor_cobrado or getattr(pacote, 'valor', 0) or 0
        if pacote.valor_pago <= 0:
            pacote.status_pagamento = 'em_aberto'
        elif pacote.valor_pago < valor_referencia:
            pacote.status_pagamento = 'parcial'
        else:
            pacote.status_pagamento = 'pago'
        self.db.commit()
        self.db.refresh(pacote)
        return pacote