import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import pacoteApi from '../api/pacotes.js'

export const usePacotesStore = defineStore('pacotes', () => {
  // Helper para mensagens de erro
  function getErrorMessage(err, fallback) {
    return err.response?.data?.detail || err.response?.data?.message || fallback
  }

  // State
  const pacotes = ref([])
  const pacoteAtual = ref(null)
  const loading = ref(false)
  const erro = ref(null)

  // Getters/Computed
  const totalPacotes = computed(() => pacotes.value.length)
  const pacotesAtivos = computed(() => pacotes.value.filter(p => p.ativo))
  const pacotesAbertos = computed(() => pacotes.value.filter(p => p.status_pagamento === 'em_aberto'))
  const totalReceitaPrevista = computed(() => {
    const mapaTipo = { semanal: 4, quinzenal: 2, mensal: 1 }
    return pacotes.value.reduce((total, p) => {
      const valor = Number(p.valor_cobrado ?? p.valor ?? 0)
      const quantidade = Number(p.limite_banhos_mes ?? mapaTipo[p.tipo_plano] ?? 0)
      return total + (valor * quantidade)
    }, 0)
  })

  // Actions
  async function fetchPacotes(params = {}) {
    loading.value = true
    erro.value = null
    try {
      const response = await pacoteApi.listar(params)
      pacotes.value = response.data
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao buscar pacotes')
      console.error('Erro ao buscar pacotes:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchPacote(id) {
    loading.value = true
    erro.value = null
    try {
      const response = await pacoteApi.obter(id)
      pacoteAtual.value = response.data
      if (!pacoteAtual.value.agendamentos || pacoteAtual.value.agendamentos.length === 0) {
        const agsResp = await pacoteApi.listarAgendamentos(id)
        pacoteAtual.value.agendamentos = agsResp.data
        pacoteAtual.value.total_agendamentos = agsResp.data.length
      } else if (pacoteAtual.value.agendamentos && !pacoteAtual.value.total_agendamentos) {
        pacoteAtual.value.total_agendamentos = pacoteAtual.value.agendamentos.length
      }
      return response.data
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao buscar pacote')
      console.error('Erro ao buscar pacote:', err)
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
      erro.value = getErrorMessage(err, 'Erro ao criar pacote')
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
      erro.value = getErrorMessage(err, 'Erro ao atualizar pacote')
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
      erro.value = getErrorMessage(err, 'Erro ao deletar pacote')
      throw err
    }
  }

  async function registrarPagamento(id, valor_pago, data_pagamento) {
    try {
      await pacoteApi.registrarPagamento(id, valor_pago, data_pagamento)
      await fetchPacotes()
      if (pacoteAtual.value?.id === id) {
        await fetchPacote(id)
      }
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao registrar pagamento')
      throw err
    }
  }

  async function updateAgendamento(id, data) {
    try {
      const response = await pacoteApi.atualizarAgendamento(id, data)
      if (pacoteAtual.value?.agendamentos) {
        const index = pacoteAtual.value.agendamentos.findIndex(a => a.id === id)
        if (index !== -1) {
          pacoteAtual.value.agendamentos[index] = response.data
          pacoteAtual.value.total_agendamentos = pacoteAtual.value.agendamentos.length
        }
      }
      return response.data
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao atualizar agendamento')
      throw err
    }
  }

  return {
    // State
    pacotes,
    pacoteAtual,
    loading,
    erro,
    // Getters
    totalPacotes,
    pacotesAtivos,
    pacotesAbertos,
    totalReceitaPrevista,
    // Actions
    fetchPacotes,
    fetchPacote,
    criarPacote,
    atualizarPacote,
    deletarPacote,
    registrarPagamento,
    updateAgendamento
  }
})