<template>
  <div class="pacotes-view">
    <div class="page-header">
      <div>
        <h1 class="page-title" v-if="cachorroId">Pacotes de {{ cachorroSelecionado?.nome || 'Cachorro' }}</h1>
        <h1 class="page-title" v-else>Gerenciamento de Pacotes</h1>
      </div>
      <div class="header-btns">
        <button @click="showNovoPacote = true" class="btn btn-primario" v-if="!cachorroId || (cachorroId && cachorros.length)">
          + Novo Pacote
        </button>
        <button v-if="cachorroId" @click="voltarTodosPacotes" class="btn btn-ghost">
          ← Todos os Pacotes
        </button>
      </div>
    </div>

    <div class="filters-bar" v-if="!cachorroId">
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

    <div class="grid-3">
      <PacoteCard
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
    <div class="modal-wrap" v-if="showNovoPacote">
      <div class="modal-overlay" @click="showNovoPacote = false"></div>
      <div class="modal-content">
        <h3 class="modal-title" v-if="cachorroId">Novo Pacote — {{ cachorroSelecionado?.nome }}</h3>
        <h3 class="modal-title" v-else>Novo Pacote</h3>
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
            <button type="button" @click="showNovoPacote = false" class="btn btn-cancelar">Cancelar</button>
            <button type="submit" class="btn btn-primario">Criar Pacote</button>
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
import PacoteCard from '../components/PacoteCard.vue'
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
const novoPacote = ref({ cachorro_id: null, tipo_plano: 'semanal', valor_cobrado: 0 })

const cachorros = computed(() => {
  const lista = []
  clientesStore.clientes.forEach(c => {
    if (c.cachorros) lista.push(...c.cachorros.map(dog => ({ ...dog, cliente: c })))
  })
  return lista
})
const cachorroSelecionado = computed(() => cachorros.value.find(d => d.id === cachorroId.value))
const pacotesFiltrados = computed(() => {
  let lista = pacotesStore.pacotes
  if (filtroStatus.value === 'ativos') lista = lista.filter(p => p.ativo)
  else if (filtroStatus.value === 'inativos') lista = lista.filter(p => !p.ativo)
  if (filtroPagamento.value !== 'todos') lista = lista.filter(p => p.status_pagamento === filtroPagamento.value)
  return lista
})

function voltarTodosPacotes() { router.push('/pacotes') }
function abrirPagamento(pacote) { pacoteSelecionado.value = pacote; showPagamento.value = true }
async function confirmarPagamento(dados) {
  try {
    await pacotesStore.registrarPagamento(dados.pacote_id, dados.valor_pago, dados.data_pagamento)
    showPagamento.value = false
    alert('Pagamento registrado com sucesso!')
  } catch (err) { alert('Erro: ' + err) }
}
async function criarPacote() {
  try {
    await pacotesStore.criarPacote(novoPacote.value)
    showNovoPacote.value = false
    novoPacote.value = { cachorro_id: null, tipo_plano: 'semanal', valor_cobrado: 0 }
    alert('Pacote criado com sucesso!')
  } catch (err) { alert('Erro ao criar pacote: ' + err) }
}
function verDetalhes(pacote) { router.push(`/pacotes/${pacote.id}`) }

onMounted(async () => {
  if (cachorroId.value) {
    await pacotesStore.fetchPacotes({ cachorro_id: cachorroId.value, incluir_inativos: true })
  } else {
    await pacotesStore.fetchPacotes({ incluir_inativos: true })
  }
  await clientesStore.fetchClientes()
})
</script>

<style scoped>
.pacotes-view {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
  --dourado:       #d4a843;
  --dourado-claro: #f5e4a8;
  --verde:         #6b8f4e;
  --creme:         #faf6ef;
  --creme-escuro:  #f0e8d8;
  --text:          #2e1e0f;
  --text-muted:    #7a6251;
  --white:         #ffffff;
  --radius:        10px;
  --shadow:        0 2px 12px rgba(59,42,26,0.1);
}

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.2rem;
}
.page-title {
  font-size: 1.6rem; font-weight: 800; color: var(--marrom);
  border-left: 5px solid var(--dourado); padding-left: 0.75rem;
}
.header-btns { display: flex; gap: 0.6rem; }

/* FILTROS */
.filters-bar { display: flex; gap: 0.75rem; margin-bottom: 1.2rem; }
.filter-select {
  padding: 0.6rem 0.9rem;
  border: 2px solid var(--creme-escuro); border-radius: 8px;
  background: var(--creme); color: var(--text); font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: border-color 0.15s;
}
.filter-select:focus { border-color: var(--dourado); outline: none; }

/* GRID */
.grid-3 { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.2rem; }

.empty-state {
  grid-column: 1 / -1; text-align: center;
  padding: 3rem; color: var(--text-muted); font-style: italic;
}

/* BOTÕES */
.btn {
  padding: 0.6rem 1.1rem; border: none; border-radius: 8px;
  font-weight: 700; cursor: pointer; font-size: 0.9rem; transition: all 0.15s;
}
.btn-primario { background: var(--marrom); color: var(--dourado); }
.btn-primario:hover { background: var(--marrom-medio); }
.btn-ghost { background: var(--creme-escuro); color: var(--marrom); }
.btn-ghost:hover { background: var(--dourado-claro); }
.btn-cancelar { background: var(--creme-escuro); color: var(--marrom); }
.btn-cancelar:hover { background: #e0d5c2; }

/* MODAL */
.modal-wrap { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.45); }
.modal-content {
  background: var(--white); padding: 2rem; border-radius: var(--radius);
  width: 90%; max-width: 480px; position: relative; z-index: 1001;
  border-top: 5px solid var(--dourado);
  box-shadow: 0 8px 32px rgba(59,42,26,0.2);
}
.modal-title { font-size: 1.1rem; font-weight: 800; color: var(--marrom); margin-bottom: 1.2rem; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.3rem; font-weight: 700; font-size: 0.9rem; color: var(--marrom); }
.form-group input,
.form-group select {
  width: 100%; padding: 0.6rem 0.75rem;
  border: 2px solid var(--creme-escuro); border-radius: 7px;
  font-size: 0.95rem; color: var(--text); background: var(--creme);
  transition: border-color 0.15s; box-sizing: border-box;
}
.form-group input:focus,
.form-group select:focus { border-color: var(--dourado); outline: none; }
.form-actions { display: flex; gap: 0.75rem; margin-top: 1.5rem; }
.form-actions .btn { flex: 1; }
</style>
