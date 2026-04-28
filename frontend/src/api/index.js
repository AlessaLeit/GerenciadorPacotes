/**
 * Configuração central do Axios.
 * Cria instância com baseURL da API e interceptores.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000 // 10 segundos timeout
})

// Interceptor para logging em desenvolvimento
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 'Erro na requisição'
    console.error('[API Error]', message)
    return Promise.reject(error)
  }
)

export default api