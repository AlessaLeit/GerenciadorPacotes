import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index.js'
import { clienteApi } from '../api/clientes.js'

export const useClientesStore = defineStore('clientes', () => {
  // Estado
  const clientes = ref([])
  const clienteAtual = ref(null)
  const loading = ref(false)
  const erro = ref(null)

  // Helper
  function getErrorMessage(err, fallback) {
    return err.response?.data?.detail || err.response?.data?.message || fallback
  }

  // Actions
  async function fetchClientes(params = {}) {
    loading.value = true
    erro.value = null
    try {
      const response = await clienteApi.listar(params)
      clientes.value = response.data
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao buscar clientes')
    } finally {
      loading.value = false
    }
  }

  async function fetchCliente(id) {
    erro.value = null
    loading.value = true
    try {
      const response = await clienteApi.obter(id)
      clienteAtual.value = response.data
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao buscar cliente')
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
      erro.value = getErrorMessage(err, 'Erro ao criar cliente')
      throw err
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
      erro.value = getErrorMessage(err, 'Erro ao atualizar cliente')
      throw err
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
      erro.value = getErrorMessage(err, 'Erro ao deletar cliente')
      throw err
    }
  }

  async function adicionarCachorro(clienteId, data) {
    try {
      await clienteApi.criarCachorro(clienteId, data)
      await fetchClientes()
      if (clienteAtual.value?.id === clienteId) {
        await fetchCliente(clienteId)
      }
      return true
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao adicionar cachorro')
      throw err
    }
  }

  async function atualizarCachorro(clienteId, cachorroId, data) {
    try {
      await clienteApi.atualizarCachorro(clienteId, cachorroId, data)
      // Refresh lists
      await fetchClientes()
      if (clienteAtual.value?.id === clienteId) {
        await fetchCliente(clienteId)
      }
      return true
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao atualizar pet')
      throw err
    }
  }

  async function deletarCachorro(clienteId, cachorroId) {
    try {
      await clienteApi.deletarCachorro(clienteId, cachorroId)
      await fetchClientes()
      if (clienteAtual.value?.id === clienteId) {
        await fetchCliente(clienteId)
      }
    } catch (err) {
      erro.value = getErrorMessage(err, 'Erro ao deletar pet')
      throw err
    }
  }

  // Getters
  const totalClientes = computed(() => clientes.value.length)
  const clientesComCachorros = computed(() => clientes.value.filter(cliente => cliente.cachorros && cliente.cachorros.length > 0))
  const clientesComTotalCachorros = computed(() => clientes.value.map(cliente => ({
    ...cliente,
    totalCachorros: cliente.cachorros ? cliente.cachorros.length : 0
  })))

  // Retorno
  return {
    clientes,
    clienteAtual,
    loading,
    erro,
    fetchClientes,
    fetchCliente,
    criarCliente,
    atualizarCliente,
    deletarCliente,
    adicionarCachorro,
    atualizarCachorro,
    deletarCachorro,
    totalClientes,
    clientesComCachorros,
    clientesComTotalCachorros,
    getErrorMessage
  }
})

