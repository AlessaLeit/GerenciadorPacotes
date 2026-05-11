<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    
    <div class="grid grid-4 stats-grid">
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
    
    <div class="grid grid-2 dashboard-sections">
      <div class="card">
        <h2>📅 Calendário de Banhos</h2>
        <CalendarioMes :banhos="agendamentosStore.agendamentosDashboard" @data-selecionada="onDataSelecionada" />
      </div>
      
      <div class="card">
        <h2>🛁 Últimos Banhos</h2>
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
    
    <!-- Agendamentos do Dia -->
    <div class="card">
      <div class="card-header flex space-between">
        <h2>📋 Agendamentos - {{ formatarData(dataSelecionada) }}</h2>
        <button @click="carregarAgendamentos()" class="btn-small">↻</button>
      </div>
      <div v-if="agendamentosStore.agendamentosDashboard.length === 0" class="empty-state">
        Nenhum agendamento nesta data. Clique no calendário para ver outros dias.
      </div>
      <div v-else class="agendamentos-list">
        <div v-for="ag in agendamentosStore.agendamentosDashboard" :key="ag.id" class="ag-card" :class="ag.status_presenca || 'pendente'">
          <div class="ag-header">
            <div>
              <h4>{{ ag.pet_nome || 'Pet' }}</h4>
              <p class="cliente">{{ ag.cliente_nome || 'Cliente' }}</p>
            </div>
            <span class="status-badge" :class="`status-${ag.status_presenca || 'pendente'}`">{{ (ag.status_presenca || 'PENDENTE').toUpperCase() }}</span>
          </div>
          <div class="ag-details">
            <p>Pacote #{{ ag.pacote_id }} | {{ formatarData(ag.data_banho) }}</p>
            <div v-if="ag.extras && Object.keys(ag.extras).length" class="extras">
              <strong>Extras:</strong> {{ Object.entries(ag.extras).map(([k,v]) => `${k}: ${v}`).join(', ') }}
            </div>
          </div>
          <div class="ag-actions">
            <button @click="confirmarRemoverAgendamento(ag)" class="btn-excluir">Excluir</button>
          </div>

        </div>
      </div>
    </div>

    
    <div class="card">
      <h2>📦 Pacotes em Aberto</h2>
      <div v-if="pacotesEmAberto.length === 0" class="empty-state">
        Nenhum pacote em aberto
      </div>
      <div class="grid grid-3" v-else>
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


const showPagamento = ref(false)
const pacoteSelecionado = ref(null)

// Computed
const totalCachorros = computed(() => {
  return clientesStore.clientes.reduce((sum, c) => sum + (c.cachorros?.length || 0), 0)
})

const pacotesEmAberto = computed(() => 
  pacotesStore.pacotes.filter(p => p.status_pagamento === 'em_aberto')
)

const banhosRecentes = computed(() => {
  const banhos = []
  pacotesStore.pacotes.forEach(p => {
    if (p.banhos) {
      banhos.push(...p.banhos.map(b => ({ ...b, pacote_id: p.id })))
    }
  })
  return banhos
    .sort((a, b) => new Date(b.data_banho) - new Date(a.data_banho))
    .slice(0, 5)
})

// Methods
function formatarValor(valor) {
  return Number(valor || 0).toFixed(2).replace('.', ',')
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

  } catch (err) {

  }
}

async function carregarAgendamentos() {
  try {
    await agendamentosStore.fetchDashboard(dataSelecionada.value)
  } catch (err) {

  }
}

function onDataSelecionada(data) {
  dataSelecionada.value = data
  carregarAgendamentos()
}

function formatarData(dataStr) {
  return new Date(dataStr).toLocaleDateString('pt-BR')
}



    async function confirmarRemoverAgendamento(ag) {

      try {
        await agendamentosStore.deletarAgendamento(ag.id)
        await carregarAgendamentos()
      } catch (err) {
      }


    }

    async function salvarAgendamento() {
      try {
        const extras = JSON.parse(agEdit.value.extras_str || '{}')
        await agendamentosStore.updateStatus(agEdit.value.id, {
          status_presenca: agEdit.value.status_presenca,
          extras: extras
        })
        showModalEdit.value = false

      } catch (err) {

      }
    }


onMounted(async () => {
  clientesStore.fetchClientes()
  pacotesStore.fetchPacotes({ incluir_inativos: true })
  await carregarAgendamentos()
})
</script>

<style scoped>
/* Style same as before */
.stats-grid { margin-bottom: 2rem; }
.stat-card { background: white; border-radius: 8px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.stat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.stat-value { font-size: 2rem; font-weight: bold; color: #2d3748; }
.stat-label { color: #718096; font-size: 0.9rem; }
.dashboard-sections { margin-bottom: 2rem; }
.empty-state { text-align: center; color: #a0aec0; padding: 2rem; font-style: italic; }
.agendamentos-list { display: flex; flex-direction: column; gap: 1rem; }
.ag-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
.ag-card.pendente { border-left: 4px solid #fbbf24; }
.ag-card.concluido { border-left: 4px solid #10b981; }
.ag-card.faltou { border-left: 4px solid #ef4444; }
.ag-header { display: flex; justify-content: space-between; align-items: flex-start; }
.status-badge { padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
.status-pendente { background: #fef3c7; color: #92400e; }
.status-concluido { background: #d1fae5; color: #065f46; }
.status-faltou { background: #fee2e2; color: #991b1b; }
.btn-editar, .btn-small { background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
.btn-small { padding: 0.25rem 0.5rem; font-size: 0.8rem; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: white; padding: 2rem; border-radius: 8px; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-group select, .form-group textarea { width: 100%; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 4px; }
.modal-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem; }
.btn-primary { background: #10b981; color: white; }
.btn-secondary { background: #6b7280; color: white; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
</style>
