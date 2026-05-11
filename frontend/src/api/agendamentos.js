/**
 * API endpoints para Agendamentos (Dashboard).
 */
import api from './index'

export const agendamentosApi = {
  // Dashboard: listar por data específica
  listarDashboard: (data = null) => {
    // Garante que sempre envie uma data no formato YYYY-MM-DD para evitar 404
    const dateParam = data || new Date().toISOString().split('T')[0]
    const endpoint = `/agendamentos/dashboard/${dateParam}`
    return api.get(endpoint)
  },
  
  // Editar status/extras
  atualizarStatus: (id, dados) => api.put(`/agendamentos/${id}`, dados),

  // Excluir agendamento do dia
  deletarAgendamento: (id) => api.delete(`/agendamentos/${id}`)
}


export default agendamentosApi
