import { defineStore } from 'pinia'
import agendamentosApi from '../api/agendamentos.js'

export const useAgendamentosStore = defineStore('agendamentos', {
  state: () => ({
    agendamentosDashboard: []
  }),
  
  actions: {
    async fetchDashboard(data = null) {
      try {
        const response = await agendamentosApi.listarDashboard(data)
        // Ensure array even if API returns unexpected data
        this.agendamentosDashboard = Array.isArray(response.data) ? response.data : []
        console.log('Dashboard agendamentos loaded:', this.agendamentosDashboard.length)
        return this.agendamentosDashboard
      } catch (error) {
        console.error('Erro ao carregar agendamentos:', error)
        this.agendamentosDashboard = []
        throw error
      }
    },
    
    async updateStatus(agendamentoId, dados) {
      try {
        const response = await agendamentosApi.atualizarStatus(agendamentoId, dados)
        // Atualizar localmente
        const index = this.agendamentosDashboard.findIndex(a => a.id === agendamentoId)
        if (index !== -1) {
          this.agendamentosDashboard[index] = Array.isArray(response.data) ? response.data[0] : response.data
        }
        return response.data
      } catch (error) {
        console.error('Erro ao atualizar agendamento:', error)
        throw error
      }
    }
  }
})

