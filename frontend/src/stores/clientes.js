/**
 * Store Pinia para gerenciamento de estado de Clientes.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index.js'
import { clienteApi } from '../api/clientes'

export const useClientesStore = defineStore('clientes', () => {
  // State
  const clientes = ref([])
  const clienteAtual = ref(null)
  const loading = ref(false)
  const erro = ref(null)

  // Getters
  const totalClientes = computed(() => clientes.value.length)
  const clientesComCachorros = computed(() => 
    clientes.value.map(c => ({
      ...c,
      totalCachorros: c.cachorros?.length || 0
    }))
  )

  // Actions
  async function fetchClientes(params = {}) {
    loading.value = true
    erro.value = null
    try {
      const response = await clienteApi.listar(params)

  clientes.value = Array.isArray(response.data) ? response.data : []

    } catch (err) {
      erro.value = err.response?.data?.detail || 'Erro ao carregar clientes'
      console.error('Clientes fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchCliente(id) {
    loading.value = true
    try {
      const response = await clienteApi.obter(id)
      clienteAtual.value = response.data
      return response.data
    } catch (err) {
      erro.value = err.response?.data?.detail || 'Erro ao carregar cliente'
      console.error('Cliente fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  async function criarCliente(data) {
    try {
      const response = await clienteApi.criar(data)
      clientes.value.unshift(response.data)
      return response.data
    } catch (err) {
      throw err.response?.data?.detail || 'Erro ao criar cliente'
    }
  }

  async function atualizarCliente(id, data) {
    try {
      const response = await clienteApi.atualizar(id, data)
      const index = clientes.value.findIndex(c => c.id === id)
      if (index !== -1) {
        clientes.value[index] = response.data
      }
      if (clienteAtual.value?.id === id) {
        clienteAtual.value = response.data
      }
      return response.data
    } catch (err) {
      throw err.response?.data?.detail || 'Erro ao atualizar cliente'
    }
  }

  async function deletarCliente(id) {
    try {
      await clienteApi.deletar(id)
      clientes.value = clientes.value.filter(c => c.id !== id)
      if (clienteAtual.value?.id === id) {
        clienteAtual.value = null
      }
    } catch (err) {
      throw err.response?.data?.detail || 'Erro ao deletar cliente'
    }
  }

  // Nova ação: adicionar cachorro e refresh cliente específico
  async function adicionarCachorro(clienteId, data) {
    try {
      await api.post('/cachorros/', data)
      // Refresh lista completa (backend agora inclui cachorros)
      await fetchClientes()
      return true
    } catch (err) {
      throw err.response?.data?.detail || 'Erro ao adicionar cachorro'
    }
  }

  return {
    clientes,
    clienteAtual,
    loading,
    erro,
    totalClientes,
    clientesComCachorros,
    fetchClientes,
    fetchCliente,
    criarCliente,
    atualizarCliente,
    deletarCliente,
    adicionarCachorro
  }
})

