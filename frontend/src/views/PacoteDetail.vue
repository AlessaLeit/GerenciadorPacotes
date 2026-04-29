<template>
  <div class="pacote-detail">
    <!-- Header -->
    <div class="header">
      <button @click="voltar" class="btn-back">← Voltar</button>
      <div class="header-info">
        <h1>{{ pacote?.pet_nome || 'Pacote' }}</h1>
        <p class="subheader">{{ pacote?.cliente_nome }}</p>
      </div>
      <div class="status" :class="pacote?.status_pagamento">
        {{ pacote?.status_pagamento?.toUpperCase() || 'EM ABERTO' }}
      </div>
    </div>

    <!-- Info Cards -->
    <div class="info-cards">
      <div class="info-card">
        <span class="label">Plano</span>
        <span class="value">{{ pacote?.tipo_plano?.toUpperCase() }}</span>
        <span class="sub">{{ pacote?.limite_banhos_mes }} banhos/mês</span>
      </div>
      <div class="info-card">
        <span class="label">Valor Base do Banho</span>
        <span class="value">R$ {{ formatarValor(pacote?.valor_banho_base) }}</span>
      </div>
      <div class="info-card">
        <span class="label">Valor Cobrado (Pacote)</span>
        <span class="value">R$ {{ formatarValor(pacote?.valor_cobrado) }}</span>
      </div>
      <div class="info-card">
        <span class="label">Total Agendamentos</span>
        <span class="value">{{ pacote?.total_agendamentos || 0 }}</span>
      </div>
    </div>

    <!-- Ações -->
    <div class="actions-bar">
      <button @click="showAddExtra = true" class="btn btn-primary">
        + Adicionar Banho Extra
      </button>
    </div>

    <!-- Tabela de Agendamentos -->
    <div class="agendamentos-section">
      <h3>Agendamentos do Pacote</h3>
      <table class="agendamentos-table" v-if="agendamentos.length">
        <thead>
          <tr>
            <th>Data</th>
            <th>Valor Banho</th>
            <th>Total Dia</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ag in agendamentos" :key="ag.id" :class="ag.status_presenca">
            <td><strong>{{ formatarData(ag.data_banho) }}</strong></td>
            <td>R$ {{ formatarValor(ag.valor_banho) }}</td>
            <td><strong>R$ {{ formatarValor(ag.total_dia) }}</strong></td>
            <td>
              <span class="status-badge" :class="ag.status_presenca">
                {{ ag.status_presenca?.toUpperCase() }}
              </span>
            </td>
            <td class="acoes">
              <button @click="abrirEditarData(ag)" class="btn-edit" title="Editar data">
                📅
              </button>
              <button @click="confirmarRemover(ag)" class="btn-delete" title="Remover">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="total-row">
            <td colspan="2"><strong>Total Pacote:</strong></td>
            <td><strong>R$ {{ formatarValor(totalPacote) }}</strong></td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      </table>
      <div v-else class="empty">
        Nenhum agendamento encontrado.
      </div>
    </div>

    <!-- Modal: Editar Data -->
    <div class="modal" v-if="showEditData">
      <div class="modal-overlay" @click="showEditData = false"></div>
      <div class="modal-content">
        <h3>Editar Data do Agendamento</h3>
        <p>Agendamento atual: {{ formatarData(agEditando?.data_banho) }}</p>
        <div class="form-group">
          <label>Nova Data</label>
          <input 
            type="date" 
            v-model="novaData" 
            required
          />
        </div>
        <div class="form-actions">
          <button @click="showEditData = false" class="btn btn-secondary">Cancelar</button>
          <button @click="salvarNovaData" class="btn btn-primary" :disabled="!novaData">
            Salvar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Adicionar Extra -->
    <div class="modal" v-if="showAddExtra">
      <div class="modal-overlay" @click="showAddExtra = false"></div>
      <div class="modal-content">
        <h3>Adicionar Banho Extra</h3>
        <p>Adicione um banho além do limite do plano.</p>
        <div class="form-group">
          <label>Data do Banho Extra</label>
          <input 
            type="date" 
            v-model="dataExtra" 
            required
          />
        </div>
        <div class="form-actions">
          <button @click="showAddExtra = false" class="btn btn-secondary">Cancelar</button>
          <button @click="salvarExtra" class="btn btn-primary" :disabled="!dataExtra">
            Adicionar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Confirmação Remover -->
    <div class="modal" v-if="showConfirmRemove">
      <div class="modal-overlay" @click="showConfirmRemove = false"></div>
      <div class="modal-content modal-confirm">
        <h3>⚠️ Confirmar Remoção</h3>
        <p>Tem certeza que deseja remover o agendamento de <strong>{{ formatarData(agRemovendo?.data_banho) }}</strong>?</p>
        <p class="warning">Esta ação não pode ser desfeita.</p>
        <div class="form-actions">
          <button @click="showConfirmRemove = false" class="btn btn-secondary">Cancelar</button>
          <button @click="executarRemover" class="btn btn-danger">
            Remover
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePacotesStore } from '../stores/pacotes.js'

const route = useRoute()
const router = useRouter()
const pacotesStore = usePacotesStore()

const pacote = ref(null)
const agendamentos = ref([])
const loading = ref(false)

// Modais
const showEditData = ref(false)
const showAddExtra = ref(false)
const showConfirmRemove = ref(false)

// Dados dos modais
const agEditando = ref(null)
const novaData = ref('')
const dataExtra = ref('')
const agRemovendo = ref(null)

const pacoteId = computed(() => parseInt(route.params.id))

// Computed: total do pacote (soma total_dia)
const totalPacote = computed(() => {
  return agendamentos.value.reduce((sum, ag) => sum + (ag.total_dia || 0), 0)
})

async function carregarPacote() {
  loading.value = true
  try {
    const data = await pacotesStore.fetchPacote(pacoteId.value)
    pacote.value = data
    agendamentos.value = data.agendamentos || []
  } catch (err) {
    alert('Erro ao carregar pacote: ' + (err.message || err))
  } finally {
    loading.value = false
  }
}

function voltar() {
  router.push('/pacotes')
}

function formatarData(isoDate) {
  if (!isoDate) return '-'
  return new Date(isoDate + 'T00:00:00').toLocaleDateString('pt-BR')
}

function formatarValor(valor) {
  return Number(valor || 0).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// Editar Data
function abrirEditarData(ag) {
  agEditando.value = ag
  novaData.value = ag.data_banho
  showEditData.value = true
}

async function salvarNovaData() {
  if (!novaData.value || !agEditando.value) return
  try {
    await pacotesStore.updateAgendamentoData(agEditando.value.id, novaData.value)
    showEditData.value = false
    agEditando.value = null
    novaData.value = ''
    alert('✅ Data atualizada com sucesso!')
  } catch (err) {
    alert('Erro ao atualizar data: ' + (err.response?.data?.detail || err.message || err))
  }
}

// Adicionar Extra
async function salvarExtra() {
  if (!dataExtra.value) return
  try {
    await pacotesStore.adicionarExtra(pacoteId.value, dataExtra.value)
    showAddExtra.value = false
    dataExtra.value = ''
    alert('✅ Banho extra adicionado com sucesso!')
  } catch (err) {
    alert('Erro ao adicionar extra: ' + (err.response?.data?.detail || err.message || err))
  }
}

// Remover
function confirmarRemover(ag) {
  agRemovendo.value = ag
  showConfirmRemove.value = true
}

async function executarRemover() {
  if (!agRemovendo.value) return
  try {
    await pacotesStore.removerAgendamento(agRemovendo.value.id)
    showConfirmRemove.value = false
    agRemovendo.value = null
    alert('✅ Agendamento removido com sucesso!')
  } catch (err) {
    alert('Erro ao remover: ' + (err.response?.data?.detail || err.message || err))
  }
}

onMounted(carregarPacote)
</script>

<style scoped>
.pacote-detail {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.btn-back:hover {
  background: #f7fafc;
}

.header-info {
  flex: 1;
}

.header-info h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #2d3748;
}

.subheader {
  margin: 0.25rem 0 0 0;
  color: #718096;
  font-size: 0.9rem;
}

.status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
}

.status.em_aberto { background: #fed7d7; color: #c53030; }
.status.pago { background: #c6f6d5; color: #22543d; }
.status.parcial { background: #feebc8; color: #744210; }

/* Info Cards */
.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-card {
  background: white;
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
}

.info-card .label {
  font-size: 0.8rem;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.info-card .value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d3748;
}

.info-card .sub {
  font-size: 0.85rem;
  color: #a0aec0;
  margin-top: 0.25rem;
}

/* Actions Bar */
.actions-bar {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

/* Agendamentos Section */
.agendamentos-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.agendamentos-section h3 {
  margin: 0 0 1.25rem 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.agendamentos-table {
  width: 100%;
  border-collapse: collapse;
}

.agendamentos-table th,
.agendamentos-table td {
  padding: 1rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.agendamentos-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.agendamentos-table tr:hover {
  background: #f7fafc;
}

.agendamentos-table tr.pendente { opacity: 0.85; }
.agendamentos-table tr.concluido { background: #f0fff4; }
.agendamentos-table tr.faltou { background: #fff5f5; }

.status-badge {
  padding: 0.3rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pendente { background: #fef3c7; color: #92400e; }
.status-badge.concluido { background: #d1fae5; color: #065f46; }
.status-badge.faltou { background: #fee2e2; color: #991b1b; }

.acoes {
  display: flex;
  gap: 0.5rem;
}

.btn-edit, .btn-delete {
  background: none;
  border: 1px solid #e2e8f0;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #ebf8ff;
  border-color: #4299e1;
}

.btn-delete:hover {
  background: #fff5f5;
  border-color: #f56565;
}

/* Total Row */
.total-row {
  background: #e6fffa !important;
  font-size: 1.1rem;
}

.total-row td {
  padding: 1rem 0.75rem;
  border-top: 2px solid #38b2ac;
}

.total-row strong {
  color: #22543d;
}

/* Empty State */
.empty {
  text-align: center;
  padding: 3rem;
  color: #718096;
  font-style: italic;
}

/* Buttons */
.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover {
  background: #3182ce;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal */
.modal {
  position: fixed;
  inset: 0;
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
  border-radius: 12px;
  width: 90%;
  max-width: 450px;
  position: relative;
  z-index: 1001;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-content h3 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
}

.modal-content p {
  color: #718096;
  margin-bottom: 1.5rem;
}

.modal-confirm .warning {
  color: #c53030;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #4a5568;
}

.form-group input[type="date"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.form-actions .btn {
  flex: 1;
}
</style>

