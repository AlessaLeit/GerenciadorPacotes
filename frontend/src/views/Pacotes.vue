<template>
  <div class="pacotes-view">
    <div class="header-actions">
      <h1 v-if="cachorroId">Pacotes de {{ cachorroSelecionado?.nome || 'Cachorro' }}</h1>
      <h1 v-else>Gerenciamento de Pacotes</h1>
      <button @click="showNovoPacote = true" class="btn btn-primary" v-if="!cachorroId || (cachorroId && cachorros.length)">
        + Novo Pacote
      </button>
      <button v-if="cachorroId" @click="voltarTodosPacotes" class="btn btn-secondary">
        Todos os Pacotes
      </button>
    </div>
    
    <div class="filters" v-if="!cachorroId">
      <select v-model="filtroStatus" class="filter-select">
        <option value="ativos">Pacotes Ativos</option>
        <option value="inativos">Pacotes Inativos</option>
        <option value="todos">Todos</option>
      </select>
      
      <select v-model="filtroPagamento" class="filter-select">
        <option value="todos">Todos os Status</option>
        <option value="em_aberto">Em Aberto</option>
        <option value="pago">Pago</option>
      </select>
    </div>
    
    <div class="grid grid-3">
      <PacoteCad 
        v-for="pacote in pacotesFiltrados" 
        :key="pacote.id"
        :pacote="pacote"
        @pagar="abrirPagamento"
        @detalhes="verDetalhes"
      />
      <div v-if="pacotesFiltrados.length === 0" class="empty-state">
        <p v-if="cachorroId">Nenhum pacote encontrado para este cachorro.</p>
        <p v-else>Nenhum pacote cadastrado.</p>
      </div>
    </div>
    
    <!-- Modal Novo Pacote -->
    <div class="modal" v-if="showNovoPacote">
      <div class="modal-overlay" @click="showNovoPacote = false"></div>
      <div class="modal-content">
        <h3 v-if="cachorroId">Novo Pacote para {{ cachorroSelecionado?.nome }}</h3>
        <h3 v-else>Novo Pacote</h3>
        <form @submit.prevent="criarPacote">
          <div class="form-group">
            <label>Cachorro</label>
            <select v-model="novoPacote.cachorro_id" required>
              <option v-if="cachorroId" :value="cachorroId" selected>{{ cachorroSelecionado?.nome }} (pré-selecionado)</option>
              <option v-else v-for="cachorro in cachorros" :key="cachorro.id" :value="cachorro.id">
                {{ cachorro.nome }} ({{ cachorro.cliente?.nome }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Tipo de Plano</label>
            <select v-model="novoPacote.tipo_plano" required>
              <option value="semanal">Semanal (4 banhos/mês)</option>
              <option value="quinzenal">Quinzenal (2 banhos/mês)</option>
              <option value="mensal">Mensal (1 banho/mês)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Valor Cobrado (R$)</label>
            <input v-model.number="novoPacote.valor_cobrado" type="number" step="0.01" required />
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showNovoPacote = false" class="btn">Cancelar</button>
            <button type="submit" class="btn btn-primary">Criar Pacote</button>
          </div>
        </form>
      </div>
    </div>
    
    <PagamentoForm 
      :show="showPagamento"
      :pacote="pacoteSelecionado"
      @close="showPagamento = false"
      @confirmar="confirmarPagamento"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePacotesStore } from '../stores/pacotes'
import { useClientesStore } from '../stores/clientes'
import PacoteCad from '../components/PacoteCad.vue'
import PagamentoForm from '../components/PagamentoForm.vue'

const route = useRoute()
const router = useRouter()
const pacotesStore = usePacotesStore()
const clientesStore = useClientesStore()

const showNovoPacote = ref(false)
const showPagamento = ref(false)
const pacoteSelecionado = ref(null)
const filtroStatus = ref('ativos')
const filtroPagamento = ref('todos')

const cachorroId = computed(() => parseInt(route.query.cachorro_id) || null)

const novoPacote = ref({
  cachorro_id: null,
  tipo_plano: 'semanal',
  valor_cobrado: 0
})

const cachorros = computed(() => {
  const lista = []
  clientesStore.clientes.forEach(c => {
    if (c.cachorros) {
      lista.push(...c.cachorros.map(dog => ({ ...dog, cliente: c })))
    }
  })
  return lista
})

const cachorroSelecionado = computed(() => cachorros.value.find(d => d.id === cachorroId.value))

const pacotesFiltrados = computed(() => {
  let lista = pacotesStore.pacotes
  
  if (filtroStatus.value === 'ativos') {
    lista = lista.filter(p => p.ativo)
  } else if (filtroStatus.value === 'inativos') {
    lista = lista.filter(p => !p.ativo)
  }
  
  if (filtroPagamento.value !== 'todos') {
    lista = lista.filter(p => p.status_pagamento === filtroPagamento.value)
  }
  
  return lista
})

function voltarTodosPacotes() {
  router.push('/pacotes')
}

function abrirPagamento(pacote) {
  pacoteSelecionado.value = pacote
  showPagamento.value = true
}

async function confirmarPagamento(dados) {
  try {
    await pacotesStore.registrarPagamento(
      dados.pacote_id,
      dados.valor_pago,
      dados.data_pagamento
    )
    showPagamento.value = false
    alert('Pagamento registrado com sucesso!')
  } catch (err) {
    alert('Erro: ' + err)
  }
}

async function criarPacote() {
  try {
    await pacotesStore.criarPacote(novoPacote.value)
    showNovoPacote.value = false
    novoPacote.value = { cachorro_id: null, tipo_plano: 'semanal', valor_cobrado: 0 }
    alert('Pacote criado com sucesso!')
  } catch (err) {
    alert('Erro ao criar pacote: ' + err)
  }
}

function verDetalhes(pacote) {
  router.push(`/pacotes/${pacote.id}`)
}

onMounted(async () => {
  try {
    if (cachorroId.value) {
      novoPacote.value.cachorro_id = cachorroId.value
      await pacotesStore.fetchPacotes({ cachorro_id: cachorroId.value, incluir_inativos: true })
    } else {
      await pacotesStore.fetchPacotes({ incluir_inativos: true })
    }
    await clientesStore.fetchClientes()
  } catch (err) {
    console.error("Erro ao inicializar dados:", err)
  }
})
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
}

.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-3 {
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  color: #718096;
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
.form-group select {
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

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-secondary {
  background: #a0aec0;
  color: #2d3748;
}

.btn:hover {
  transform: translateY(-1px);
}
</style>
