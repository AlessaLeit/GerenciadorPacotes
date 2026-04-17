<template>
  <div class="clientes-view">
    <div class="header-actions">
      <h1>Clientes e Pets</h1>
      <br>
      <button @click="showNovoCliente = true" class="btn btn-primary">
        + Novo Cliente
      </button>
    </div>
    <br>
    
    <div class="card">
      <input 
        v-model="busca" 
        type="text" 
        placeholder="Buscar por nome..."
        class="search-input"
      />
    </div>
    
    <div class="clientes-lista">
      <div v-for="cliente in clientesFiltrados" :key="cliente.id" class="cliente-card">
        <div class="cliente-header">
          <h3>{{ cliente.nome }}</h3>
          <div class="cliente-actions">
            <button @click="editarCliente(cliente)" class="btn btn-sm">Editar</button>
            <button @click="adicionarCachorro(cliente)" class="btn btn-primary btn-sm">+ Pet</button>
            <button @click="confirmarExclusao(cliente)" class="btn btn-danger btn-sm">🗑️ Excluir</button>
          </div>
        </div>
        
        <div class="cliente-info">
          <span v-if="cliente.telefone">📞 {{ cliente.telefone }}</span>
          <span v-if="cliente.endereco">📍 {{ cliente.endereco }}</span>
        </div>
        
        <div class="cachorros-lista" v-if="cliente.cachorros?.length">
          <h4>Pets:</h4>
          <div v-for="dog in cliente.cachorros" :key="dog.id" class="cachorro-item">
            <div class="dog-header">
              <span class="dog-nome">{{ dog.nome }}</span>
              <span class="dog-info">{{ dog.raca }} • {{ dog.porte }}</span>
              <div class="dog-actions">
                <button @click="verPacotesCachorro(dog)" class="btn btn-sm btn-pacotes" title="Ver Pacotes">📦 Pacotes</button>
              </div>
            </div>
            <span v-if="dog.observacoes" class="dog-obs">{{ dog.observacoes }}</span>
          </div>
        </div>
        <div v-else class="no-pets">
          <small>Nenhum pet cadastrado.</small>
        </div>
      </div>
    </div>
    
    <!-- Modal Novo Cliente -->
    <div class="modal" v-if="showNovoCliente">
      <div class="modal-overlay" @click="showNovoCliente = false"></div>
      <div class="modal-content">
        <h3>{{ editando ? 'Editar' : 'Novo' }} Cliente</h3>
        <form @submit.prevent="salvarCliente">
          <div class="form-group">
            <label>Nome *</label>
            <input v-model="formCliente.nome" required />
          </div>
          <div class="form-group">
            <label>Telefone</label>
            <input v-model="formCliente.telefone" />
          </div>
          <div class="form-group">
            <label>Endereço</label>
            <input v-model="formCliente.endereco" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showNovoCliente = false" class="btn">Cancelar</button>
            <button type="submit" class="btn btn-primary">Salvar</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Modal Novo Cachorro -->
    <div class="modal" v-if="showNovoCachorro">
      <div class="modal-overlay" @click="showNovoCachorro = false"></div>
      <div class="modal-content">
        <h3>Novo Pet - {{ clienteAtual?.nome }}</h3>
        <form @submit.prevent="salvarCachorro">
          <div class="form-group">
            <label>Nome *</label>
            <input v-model="formCachorro.nome" required />
          </div>
          <div class="form-group">
            <label>Raça</label>
            <input v-model="formCachorro.raca" />
          </div>
          <div class="form-group">
            <label>Porte *</label>
            <select v-model="formCachorro.porte" required>
              <option value="pequeno">Pequeno</option>
              <option value="medio">Médio</option>
              <option value="grande">Grande</option>
            </select>
          </div>
          <div class="form-group">
            <label>Observações</label>
            <textarea v-model="formCachorro.observacoes" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showNovoCachorro = false" class="btn">Cancelar</button>
            <button type="submit" class="btn btn-primary">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useClientesStore } from '../stores/clientes'

const router = useRouter()
const clientesStore = useClientesStore()

const busca = ref('')
const showNovoCliente = ref(false)
const showNovoCachorro = ref(false)
const editando = ref(false)
const clienteAtual = ref(null)

const formCliente = ref({ nome: '', telefone: '', endereco: '' })
const formCachorro = ref({ nome: '', raca: '', porte: 'medio', observacoes: '', cliente_id: null })

const clientesFiltrados = computed(() => {
  if (!busca.value) return clientesStore.clientes
  const termo = busca.value.toLowerCase()
  return clientesStore.clientes.filter(c => 
    c.nome.toLowerCase().includes(termo)
  )
})

function editarCliente(cliente) {
  editando.value = true
  clienteAtual.value = cliente
  formCliente.value = { ...cliente }
  showNovoCliente.value = true
}

function adicionarCachorro(cliente) {
  clienteAtual.value = cliente
  formCachorro.value = { nome: '', raca: '', porte: 'medio', observacoes: '', cliente_id: cliente.id }
  showNovoCachorro.value = true
}

function verPacotesCachorro(dog) {
  router.push(`/pacotes?cachorro_id=${dog.id}`)
}

async function salvarCliente() {
  try {
    if (editando.value) {
      await clientesStore.atualizarCliente(clienteAtual.value.id, formCliente.value)
    } else {
      await clientesStore.criarCliente(formCliente.value)
    }
    showNovoCliente.value = false
    formCliente.value = { nome: '', telefone: '', endereco: '' }
    editando.value = false
  } catch (err) {
    alert('Erro: ' + err)
  }
}

async function salvarCachorro() {
  try {
    await clientesStore.adicionarCachorro(clienteAtual.value.id, formCachorro.value)
    showNovoCachorro.value = false
    formCachorro.value = { nome: '', raca: '', porte: 'medio', observacoes: '', cliente_id: null }
    alert('Pet adicionado com sucesso!')
  } catch (err) {
    alert('Erro ao adicionar pet: ' + err)
  }
}

async function confirmarExclusao(cliente) {
  if (!confirm(`Tem certeza que deseja excluir o cliente \"${cliente.nome}\" e todos os seus pets? Essa ação não pode ser desfeita.`)) {
    return
  }
  try {
    await clientesStore.deletarCliente(cliente.id)
    alert('Cliente excluído com sucesso!')
  } catch (err) {
    alert('Erro ao excluir cliente: ' + err)
  }
}

onMounted(() => {
  clientesStore.fetchClientes()
})
</script>

<style scoped>
.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 1rem;
}

.clientes-lista {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cliente-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.cliente-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.cliente-header h3 {
  margin: 0;
  color: #2d3748;
}

.cliente-actions {
  display: flex;
  gap: 0.5rem;
}

.cliente-info {
  display: flex;
  gap: 1rem;
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.cachorros-lista h4 {
  color: #4a5568;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.cachorro-item {
  background: #f7fafc;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.dog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.dog-nome {
  font-weight: 600;
  color: #2d3748;
}

.dog-info {
  font-size: 0.85rem;
  color: #718096;
}

.dog-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-pacotes {
  background: #48bb78;
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.btn-pacotes:hover {
  background: #38a169;
}

.dog-obs {
  font-size: 0.8rem;
  color: #a0aec0;
  font-style: italic;
  display: block;
  margin-top: 0.25rem;
}

.no-pets {
  padding: 1rem;
  color: #a0aec0;
  text-align: center;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  position: relative;
  z-index: 1001;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.form-actions .btn {
  flex: 1;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}
</style>
