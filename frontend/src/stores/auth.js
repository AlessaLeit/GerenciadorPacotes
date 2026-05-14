import { defineStore } from 'pinia'
import api from '../api/index'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: (() => {
      try {
        const savedUser = localStorage.getItem('user')
        return savedUser ? JSON.parse(savedUser) : null
      } catch (e) {
        console.error('Erro ao recuperar usuário do localStorage:', e)
        return null
      }
    })()
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  actions: {
    async login(email, password) {
      try {
        const response = await api.post('/auth/login', {
          username: email,
          password: password
        })
        this.token = response.data.access_token
        this.user = response.data.user
        
        // Persistência
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        // O interceptor em api/index.js usará o novo token automaticamente
        return true
      } catch (error) {
        console.error('Falha no login:', error)
        throw error.response?.data?.detail || 'Erro ao entrar'
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Limpa o estado e força o redirecionamento
      // window.location.href é preferível ao router.push no logout para limpar estados residuais de memória
      window.location.href = '/login'
    }
  }
})