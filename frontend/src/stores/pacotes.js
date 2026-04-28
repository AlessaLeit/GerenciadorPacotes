/**
 * Store Pinia para gerenciamento de estado de Pacotes.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import pacoteApi from '../api/pacotes.js'

export const usePacotesStore = defineStore('pacotes', () => {
  const pacotes = ref([])
  const pacoteAtual = ref(null)
  const loading = ref(false)
  const erro = ref(null)

  const totalPacotes = computed(() => pacotes.value.length)
  const pacotesAtivos = computed(() => pacotes.value.filter(p => p.ativo))
  const pacotesAbertos = computed(() => pacotes.value.filter(p => p.status_pagamento === 'em_aberto'))
  const totalReceitaPrevista = computed(() => pacotes.value.reduce((sum, p) => sum + (p.valor_cobrado * p.limite_banhos_mes || 0), 0))

  async function fetchPacotes(params = {}) {
    loading.value = true
    erro.value = null
    try {
      const response = await pacoteApi.listar(params)
      pacotes.value = response.data
    } catch (err) {
      erro.value = err.response?.data?.detail || 'Erro ao carregar pacotes'
      console.error(erro.value)
    } finally {
      loading.value = false
    }
  }

  async function fetchPacote(id) {
    loading.value = true
    try {
      const response = await pacoteApi.obter(id)
      // ✅ ATUALIZADO: Usa novo endpoint /pacotes/{id}/agendamentos com valores computados
      const agsResp = await pacoteApi.listarAgendamentosPacote(id)
      pacoteAtual.value = {
        ...response.data,
        agendamentos: agsResp.data || [],
        total_agendamentos: agsResp.data?.length || 0
      }
      return pacoteAtual.value
    } catch (err) {
      erro.value = err.response?.data?.detail || 'Erro ao carregar pacote'
      console.error(erro.value)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function criarPacote(data) {
    try {
      const response = await pacoteApi.criar(data)
      pacotes.value.unshift(response.data)
      return response.data
    } catch (err) {
      console.error(err.response?.data?.detail || 'Erro ao criar pacote')
      throw err
    }
  }

  async function atualizarPacote(id, data) {
    try {
      const response = await pacoteApi.atualizar(id, data)
      const index = pacotes.value.findIndex(p => p.id === id)
      if (index !== -1) {
        pacotes.value[index] = response.data
      }
      if (pacoteAtual.value?.id === id) {
        pacoteAtual.value = response.data
      }
      return response.data
    } catch (err) {
      console.error(err.response?.data?.detail || 'Erro ao atualizar pacote')
      throw err
    }
  }

  async function deletarPacote(id) {
    try {
      await pacoteApi.deletar(id)
      pacotes.value = pacotes.value.filter(p => p.id !== id)
      if (pacoteAtual.value?.id === id) {
        pacoteAtual.value = null
      }
    } catch (err) {
      console.error(err.response?.data?.detail || 'Erro ao deletar pacote')
      throw err
    }
  }

  async function registrarPagamento(id, valor_pago, data_pagamento) {
    try {
      await pacoteApi.registrarPagamento(id, valor_pago, data_pagamento)
      await fetchPacotes()
      await fetchPacote(id)  // Refresh current
    } catch (err) {
      console.error(err.response?.data?.detail || 'Erro ao registrar pagamento')
      throw err
    }
  }

  async function updateAgendamento(id, data) {
    try {
      const response = await pacoteApi.atualizarAgendamento(id, data)
      if (pacoteAtual.value && pacoteAtual.value.agendamentos) {
        const idx = pacoteAtual.value.agendamentos.findIndex(a => a.id === id)
        if (idx > -1) {
          // Update com novos totais se vierem da API
          pacoteAtual.value.agendamentos[idx] = { ...response.data }
        }
      }
      return response.data
    } catch (err) {
      console.error(err.response?.data?.detail || 'Erro ao atualizar agendamento')
      throw err
    }
  }

  return {
    pacotes,
    pacoteAtual,
    loading,
    erro,
    totalPacotes,
    pacotesAtivos,
    pacotesAbertos,
    totalReceitaPrevista,
    fetchPacotes,
    fetchPacote,
    criarPacote,
    atualizarPacote,
    deletarPacote,
    registrarPagamento,
    updateAgendamento
  }
})

