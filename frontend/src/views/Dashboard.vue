<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-value">{{ clientesStore.totalClientes }}</div>
        <div class="stat-label">Clientes</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🐕</div>
        <div class="stat-value">{{ totalCachorros }}</div>
        <div class="stat-label">Cachorros</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-value">{{ pacotesStore.pacotesAtivos.length }}</div>
        <div class="stat-label">Pacotes Ativos</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-value">R$ {{ formatarValor(pacotesStore.totalReceitaPrevista) }}</div>
        <div class="stat-label">Receita Prevista</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title"><span class="card-title-bar"></span>📅 Calendário de Banhos</div>
        <CalendarioMes :banhos="agendamentosStore.agendamentosDashboard" @data-selecionada="onDataSelecionada" />
      </div>

      <div class="card">
        <div class="card-title"><span class="card-title-bar"></span>🛁 Últimos Banhos</div>
        <div v-if="banhosRecentes.length === 0" class="empty-state">
          Nenhum banho registrado recentemente
        </div>
        <BanhoItem
          v-for="banho in banhosRecentes"
          :key="banho.id"
          :banho="banho"
          show-pacote
        />
      </div>
    </div>

    <div class="card">
      <div class="card-header-row">
        <div class="card-title" style="margin-bottom:0"><span class="card-title-bar"></span>📋 Agendamentos — {{ formatarData(dataSelecionada) }}</div>
        <button @click="carregarAgendamentos()" class="btn-refresh">↻ Atualizar</button>
      </div>
      <div v-if="agendamentosStore.agendamentosDashboard.length === 0" class="empty-state">
        Nenhum agendamento nesta data. Clique no calendário para ver outros dias.
      </div>
      <div v-else class="agendamentos-list">
        <div
          v-for="ag in agendamentosStore.agendamentosDashboard"
          :key="ag.id"
          class="ag-card"
          :class="ag.status_presenca"
        >
          <div class="ag-header">
            <div>
              <h4 class="ag-pet">{{ ag.pet_nome }}</h4>
              <p class="ag-cliente">{{ ag.cliente_nome }}</p>
            </div>
            <span class="status-badge" :class="`status-${ag.status_presenca}`">
              {{ ag.status_presenca.toUpperCase() }}
            </span>
          </div>
          <div class="ag-details">
            <p>Pacote #{{ ag.pacote_id }} | {{ formatarData(ag.data_banho) }}</p>
            <div v-if="ag.extras && Object.keys(ag.extras).length" class="extras">
              <strong>Extras:</strong> {{ Object.entries(ag.extras).map(([k,v]) => `${k}: ${v}`).join(', ') }}
            </div>
          </div>
          <button @click="editarAgendamento(ag)" class="btn-editar">Editar</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title"><span class="card-title-bar"></span>📦 Pacotes em Aberto</div>
      <div v-if="pacotesEmAberto.length === 0" class="empty-state">
        Nenhum pacote em aberto
      </div>
      <div class="grid-3" v-else>
        <PacoteCard
          v-for="pacote in pacotesEmAberto.slice(0, 6)"
          :key="pacote.id"
          :pacote="pacote"
          @pagar="abrirPagamento"
        />
      </div>
    </div>

    <PagamentoForm
      :show="showPagamento"
      :pacote="pacoteSelecionado"
      @close="showPagamento = false"
      @confirmar="confirmarPagamento"
    />

    <!-- Modal Editar Agendamento -->
    <div v-if="showModalEdit" class="modal-overlay" @click="showModalEdit = false">
      <div class="modal" @click.stop>
        <h3 class="modal-title">Editar Status — {{ agEdit.pet_nome }}</h3>
        <div class="form-group">
          <label>Status</label>
          <select v-model="agEdit.status_presenca">
            <option value="pendente">🟡 Pendente</option>
            <option value="concluido">🟢 Concluído</option>
            <option value="faltou">🔴 Faltou</option>
          </select>
        </div>
        <div class="form-group">
          <label>Extras (JSON)</label>
          <textarea v-model="agEdit.extras_str" rows="3" placeholder='{"observacao": "Banho extra"}'></textarea>
          <small class="field-hint">Formato JSON simples</small>
        </div>
        <div class="modal-actions">
          <button @click="showModalEdit = false" class="btn btn-cancelar">Cancelar</button>
          <button @click="salvarAgendamento" class="btn btn-primario">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useClientesStore } from '../stores/clientes'
import { usePacotesStore } from '../stores/pacotes'
import PacoteCard from '../components/PacoteCard.vue'
import BanhoItem from '../components/BanhoItem.vue'
import CalendarioMes from '../components/CalendarioMes.vue'
import PagamentoForm from '../components/PagamentoForm.vue'
import { useAgendamentosStore } from '../stores/agendamentos.js'

const clientesStore = useClientesStore()
const pacotesStore = usePacotesStore()
const agendamentosStore = useAgendamentosStore()
const dataSelecionada = ref(new Date().toISOString().split('T')[0])
const showModalEdit = ref(false)
const agEdit = ref(null)
const showPagamento = ref(false)
const pacoteSelecionado = ref(null)

const totalCachorros = computed(() =>
  clientesStore.clientes.reduce((sum, c) => sum + (c.cachorros?.length || 0), 0)
)
const pacotesEmAberto = computed(() =>
  pacotesStore.pacotes.filter(p => p.status_pagamento === 'em_aberto')
)
const banhosRecentes = computed(() => {
  const banhos = []
  pacotesStore.pacotes.forEach(p => {
    if (p.banhos) banhos.push(...p.banhos.map(b => ({ ...b, pacote_id: p.id })))
  })
  return banhos.sort((a, b) => new Date(b.data_banho) - new Date(a.data_banho)).slice(0, 5)
})

function formatarValor(valor) {
  return Number(valor || 0).toFixed(2).replace('.', ',')
}
function abrirPagamento(pacote) {
  pacoteSelecionado.value = pacote
  showPagamento.value = true
}
async function confirmarPagamento(dados) {
  try {
    await pacotesStore.registrarPagamento(dados.pacote_id, dados.valor_pago, dados.data_pagamento)
    showPagamento.value = false
    alert('Pagamento registrado com sucesso!')
  } catch (err) {
    alert('Erro ao registrar pagamento: ' + err)
  }
}
async function carregarAgendamentos() {
  try {
    await agendamentosStore.fetchDashboard(dataSelecionada.value)
  } catch (err) {
    alert('Erro ao carregar agendamentos: ' + err.message)
  }
}
function onDataSelecionada(data) {
  dataSelecionada.value = data
  carregarAgendamentos()
}
function formatarData(dataStr) {
  return new Date(dataStr).toLocaleDateString('pt-BR')
}
function editarAgendamento(ag) {
  agEdit.value = { ...ag, extras_str: JSON.stringify(ag.extras || {}, null, 2) }
  showModalEdit.value = true
}
async function salvarAgendamento() {
  try {
    const extras = JSON.parse(agEdit.value.extras_str || '{}')
    await agendamentosStore.updateStatus(agEdit.value.id, {
      status_presenca: agEdit.value.status_presenca,
      extras
    })
    showModalEdit.value = false
    alert('Agendamento atualizado!')
  } catch (err) {
    alert('Erro ao salvar: ' + err.response?.data?.detail || err.message)
  }
}
onMounted(async () => {
  clientesStore.fetchClientes()
  pacotesStore.fetchPacotes({ incluir_inativos: true })
  await carregarAgendamentos()
})
</script>

<style scoped>
/* ── VARIÁVEIS DO TEMA RECANTO ── */
.dashboard {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
  --marrom-claro:  #8b6340;
  --dourado:       #d4a843;
  --dourado-claro: #f5e4a8;
  --dourado-bg:    #fdf6e3;
  --verde:         #6b8f4e;
  --verde-claro:   #a8c47a;
  --verde-bg:      #eef4e6;
  --creme:         #faf6ef;
  --creme-escuro:  #f0e8d8;
  --text:          #2e1e0f;
  --text-muted:    #7a6251;
  --white:         #ffffff;
  --radius:        10px;
  --shadow:        0 2px 12px rgba(59,42,26,0.1);
}

.page-header { margin-bottom: 1.5rem; }

.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--marrom);
  border-left: 5px solid var(--dourado);
  padding-left: 0.75rem;
}

/* STATS */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.stat-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.4rem 1rem;
  text-align: center;
  box-shadow: var(--shadow);
  border-top: 4px solid var(--dourado);
  transition: transform 0.2s;
}
.stat-card:nth-child(2) { border-top-color: var(--verde); }
.stat-card:nth-child(3) { border-top-color: var(--marrom-claro); }
.stat-card:nth-child(4) { border-top-color: var(--verde-claro); }
.stat-card:hover { transform: translateY(-3px); }
.stat-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.stat-value { font-size: 1.9rem; font-weight: 800; color: var(--marrom); line-height: 1.1; }
.stat-label { color: var(--text-muted); font-size: 0.82rem; font-weight: 700; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

/* GRID */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; margin-bottom: 1.2rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }

/* CARD */
.card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.4rem;
  box-shadow: var(--shadow);
  margin-bottom: 1.2rem;
}
.card-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--marrom);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-title-bar {
  display: inline-block;
  width: 4px; height: 16px;
  background: var(--dourado);
  border-radius: 2px;
  flex-shrink: 0;
}
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

/* BOTÃO REFRESH */
.btn-refresh {
  background: var(--creme-escuro);
  border: 1px solid var(--creme-escuro);
  color: var(--marrom);
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-refresh:hover { background: var(--dourado-claro); }

/* EMPTY */
.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
  font-style: italic;
  font-size: 0.95rem;
}

/* AGENDAMENTOS */
.agendamentos-list { display: flex; flex-direction: column; gap: 0.75rem; }
.ag-card {
  background: var(--creme);
  border: 1px solid var(--creme-escuro);
  border-radius: var(--radius);
  padding: 1rem 1.2rem;
  border-left: 4px solid var(--dourado);
}
.ag-card.pendente  { border-left-color: #d4a843; }
.ag-card.concluido { border-left-color: var(--verde); background: var(--verde-bg); }
.ag-card.faltou    { border-left-color: #b94040; background: #fdf0f0; }
.ag-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
.ag-pet { font-size: 1rem; font-weight: 800; color: var(--marrom); margin: 0; }
.ag-cliente { color: var(--text-muted); font-size: 0.85rem; margin: 2px 0 0; }
.ag-details { font-size: 0.85rem; color: var(--text-muted); }

.status-badge {
  padding: 3px 10px;
  border-radius: 5px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.status-pendente  { background: var(--dourado-claro); color: #6b4c00; }
.status-concluido { background: var(--verde-bg); color: var(--verde); }
.status-faltou    { background: #fdeaea; color: #b94040; }

.btn-editar {
  background: var(--marrom);
  color: var(--dourado);
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 700;
  margin-top: 0.5rem;
  transition: background 0.15s;
}
.btn-editar:hover { background: var(--marrom-medio); }

/* MODAL */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--white);
  padding: 2rem;
  border-radius: var(--radius);
  max-width: 480px; width: 90%;
  max-height: 80vh; overflow-y: auto;
  border-top: 5px solid var(--dourado);
  box-shadow: 0 8px 32px rgba(59,42,26,0.2);
}
.modal-title { font-size: 1.1rem; font-weight: 800; color: var(--marrom); margin-bottom: 1.2rem; }

.form-group { margin-bottom: 1rem; }
.form-group label {
  display: block; margin-bottom: 0.3rem;
  font-weight: 700; font-size: 0.9rem; color: var(--marrom);
}
.form-group select,
.form-group textarea {
  width: 100%; padding: 0.6rem 0.75rem;
  border: 2px solid var(--creme-escuro);
  border-radius: 7px; font-size: 0.95rem;
  color: var(--text); background: var(--creme);
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.form-group select:focus,
.form-group textarea:focus { border-color: var(--dourado); outline: none; }
.field-hint { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; display: block; }

.modal-actions { display: flex; gap: 0.75rem; margin-top: 1.5rem; }
.btn { padding: 0.65rem 1.2rem; border: none; border-radius: 7px; font-weight: 700; cursor: pointer; font-size: 0.95rem; transition: all 0.15s; }
.btn-primario { background: var(--marrom); color: var(--dourado); flex: 1; }
.btn-primario:hover { background: var(--marrom-medio); }
.btn-cancelar { background: var(--creme-escuro); color: var(--marrom); flex: 1; }
.btn-cancelar:hover { background: #e0d5c2; }
</style>
