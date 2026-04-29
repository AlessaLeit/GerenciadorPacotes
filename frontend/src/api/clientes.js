/**
 * API endpoints para Clientes.
 */
import api from './index'

export const clienteApi = {
  listar: (params = {}) => api.get('/clientes', { params }),
  obter: (id) => api.get(`/clientes/${id}`),
  criar: (data) => api.post('/clientes', data),
  atualizar: (id, data) => api.put(`/clientes/${id}`, data),
  deletar: (id) => api.delete(`/clientes/${id}`)
}

export default clienteApi
