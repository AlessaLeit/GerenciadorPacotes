/**
 * API endpoints para Clientes e Cachorros nested.
 */
import api from './index.js'

export const clienteApi = {
  // Client CRUD
  listar: (params = {}) => api.get('/clientes', { params }),
  obter: (id) => api.get(`/clientes/${id}`),
  criar: (data) => api.post('/clientes', data),
  atualizar: (id, data) => api.put(`/clientes/${id}`, data),
  deletar: (id) => api.delete(`/clientes/${id}`),
  // Nested Cachorros CRUD
  listarCachorros: (clienteId, params = {}) => api.get(`/clientes/${clienteId}/cachorros`, { params }),
  criarCachorro: (clienteId, data) => api.post(`/clientes/${clienteId}/cachorros`, data),
  obterCachorro: (clienteId, cachorroId) => api.get(`/clientes/${clienteId}/cachorros/${cachorroId}`),
  atualizarCachorro: (clienteId, cachorroId, data) => api.put(`/clientes/${clienteId}/cachorros/${cachorroId}`, data),
  deletarCachorro: (clienteId, cachorroId) => api.delete(`/clientes/${clienteId}/cachorros/${cachorroId}`)
}

export default clienteApi

