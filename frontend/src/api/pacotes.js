/**
 * API endpoints para Pacotes.
 */
import api from './index'

export const pacoteApi = {
  // CRUD básico
  listar: (params = {}) => api.get('/pacotes', { params }),
  obter: (id) => api.get(`/pacotes/${id}`),
  criar: (data) => api.post('/pacotes', data),
  atualizar: (id, data) => api.put(`/pacotes/${id}`, data),
  deletar: (id) => api.delete(`/pacotes/${id}`),
  
  // Ações específicas
  registrarPagamento: (id, valor_pago, data_pagamento) => 
    api.post(`/pacotes/${id}/pagar`, null, {
      params: { valor_pago, data_pagamento }
    }),

  // Agendamentos - NOVO ENDPOINT conforme task
  listarAgendamentosPacote: (pacoteId) => api.get(`/pacotes/${pacoteId}/agendamentos`),
  
  // ✅ NOVO: Endpoint otimizado para página de detalhes
  detalhesComAgendamentos: (pacoteId) => api.get(`/pacotes/${pacoteId}/detalhes-com-agendamentos`),
  
  // ✅ NOVO: Adicionar agendamento extra (além do limite)
  adicionarAgendamentoExtra: (pacoteId, data_banho) => 
    api.post(`/pacotes/${pacoteId}/agendamento-extra`, null, {
      params: { data_banho }
    }),
  
  // ✅ NOVO: Atualizar data do agendamento
  atualizarDataAgendamento: (id, data_banho) => 
    api.put(`/agendamentos/${id}/data`, null, {
      params: { data_banho }
    }),
  
  // ✅ NOVO: Deletar agendamento
  deletarAgendamento: (id) => api.delete(`/agendamentos/${id}`),
  
  // Legacy (mantém para compatibilidade)
  listarAgendamentos: (pacoteId) => api.get('/agendamentos', { params: { pacote_id: pacoteId } }),
  atualizarAgendamento: (id, data) => api.put(`/agendamentos/${id}`, data)
}

export default pacoteApi

