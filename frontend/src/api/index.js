/**
 * Configuração central do Axios.
 * Cria instância com baseURL da API e interceptores.
 */
import axios from 'axios'


const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',

  timeout: 10000 // 10 segundos timeout
})

// Anexa token JWT automaticamente (para endpoints protegidos)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Logging opcional
  const fullPath = config.baseURL ? `${config.baseURL}${config.url}` : config.url
  console.log(`[API Request] ${config.method.toUpperCase()} ${fullPath}`)
  
  return config
}, (error) => Promise.reject(error))

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'Erro na requisição'
    if (!error.response) {
      message = 'Não foi possível conectar ao servidor. Verifique se o backend está rodando.'
    } else {
      // Só redireciona se NÃO estivermos na página de login
      if ((error.response.status === 401 || error.response.status === 403) && !window.location.pathname.includes('/login')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
      message = error.response?.data?.detail || message
    }
    console.error('[API Error]', message, error.config?.method?.toUpperCase(), error.config?.url)
    return Promise.reject(error)
  }
)

export default api