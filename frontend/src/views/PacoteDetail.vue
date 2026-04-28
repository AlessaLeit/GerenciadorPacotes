<template>
  <div class="pacote-detail">
    <div class="header">
      <button @click="voltar" class="btn-back">← Voltar</button>
      <h1>Pacote {{ pacote?.id }} - {{ pacote?.pet_nome }}</h1>
      <div class="status" :class="pacote?.status_pagamento">
        {{ pacote?.status_pagamento?.toUpperCase() || 'EM ABERTO' }}
      </div>
    </div>

    <div class="metrics">
      <span>Tipo: {{ pacote?.tipo_plano?.toUpperCase() }} ({{ pacote?.limite_banhos_mes }} banhos/mês)</span>
      <span>Total agendamentos: {{ pacote?.total_agendamentos || 0 }}</span>
      <span v-if="pacote?.cachorro">Valor Banho Base: R$ {{ pacote.cachorro.valor_banho?.toFixed(2) || '0,00' }}</span>
      <button @click="gerarAgendamentos" class="btn-gerar" v-if="podeGerar">
        🔄 Regenerar Agendamentos Pendentes
      </button>
    </div>

    <!-- ✅ Tabela Banhos do Pacote com NOVAS COLUNAS + TOTAL PACOTE -->
    <div class="banhos-section">
      <h3>Banhos do Pacote ({{ agendamentos.length }})</h3>
      <table class="banhos-table" v-if="agendamentos.length">
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
            <td><strong>{{ formatDate(ag.data_banho) }}</strong></td>
            <td>R$ {{ ag.valor_banho?.toFixed(2) || '0,00' }}</td>
            <td><strong>R$ {{ ag.total_dia?.toFixed(2) || '0,00' }}</strong></td>
            <td>
              <span class="status-badge">{{ ag.status_presenca?.toUpperCase() }}</span>
            </td>
            <td>
              <button @click="editarAgendamento(ag)" class="btn-edit-small">Editar</button>
            </td>
          </tr>
        </tbody>
        <!-- ✅ TOTAL PACOTE -->
        <tfoot>
          <tr class="total-row">
            <td colspan="2"><strong>Total Pacote:</strong></td>
            <td><strong>R$ {{ totalPacote.toFixed(2) }}</strong></td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      </table>
      <div v-else class="empty">
        Nenhum agendamento. O pacote foi criado com agendamentos automáticos.
      </div>
    </div>

    <!-- Modal Editar (mantido) -->
    <div class="modal" v-if="showModal">
      <div class="modal-overlay" @click="showModal = false"></div>
      <div class="modal-content">
        <h3>Editar Agendamento - {{ formatDate(editAg?.data_banho) }}</h3>
        <form @submit.prevent="salvarEdicao">
          <div class="form-group">
            <label>Status</label>
            <select v-model="editForm.status_presenca" required>
              <option value="pendente">Pendente</option>
              <option value="concluido">Concluído</option>
              <option value="faltou">Faltou</option>
            </select>
          </div>
          <div class="form-group">
            <label>Extras (JSON)</label>
            <textarea v-model="editForm.extrasJson" rows="4" placeholder='{"remedio": "nome", "obs": "texto", "preco_extra": 20}'></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showModal = false" class="btn-cancel">Cancelar</button>
            <button type="submit" class="btn-save">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePacotesStore } from '../stores/pacotes.js'

const route = useRoute()
const router = useRouter()
const pacotesStore = usePacotesStore()

const pacote = ref(null)
const agendamentos = ref([])
const showModal = ref(false)
const editAg = ref(null)
const editForm = ref({ status_presenca: 'pendente', extrasJson: '{}' })
const loading = ref(false)

const pacoteId = computed(() => parseInt(route.params.id))

// ✅ NOVO: Total pacote computado
const totalPacote = computed(() => {
  return agendamentos.value.reduce((sum, ag) => sum + (ag.total_dia || 0), 0)
})

async function carregarPacote() {
  loading.value = true
  try {
    await pacotesStore.fetchPacote(pacoteId.value)
    pacote.value = pacotesStore.pacoteAtual
    agendamentos.value = pacote.value?.agendamentos || []
  } catch (err) {
    alert('Erro ao carregar: ' + err.message || err)
  } finally {
    loading.value = false
  }
}

function voltar() {
  router.push('/pacotes')
}

const podeGerar = computed(() => agendamentos.value.length === 0 || agendamentos.value.some(ag => ag.status_presenca === 'pendente'))

async function gerarAgendamentos() {
  if (!confirm(`Regenerar agendamentos para pacote ${pacoteId.value}? (apenas pendentes)`)) return
  try {
    // TODO: Endpoint futuro /pacotes/{id}/regenerar
    alert('Funcionalidade completa via criação automática. Teste criando novo pacote!')
    await carregarPacote()
  } catch (err) {
    alert('Erro: ' + err)
  }
}

function editarAgendamento(ag) {
  editAg.value = ag
  editForm.value.status_presenca = ag.status_presenca
  editForm.value.extrasJson = JSON.stringify(ag.extras || {}, null, 2)
  showModal.value = true
}

async function salvarEdicao() {
  try {
    let extras = {}
    try {
      extras = JSON.parse(editForm.value.extrasJson)
    } catch {
      alert('JSON inválido nos extras')
      return
    }
    
    await pacotesStore.updateAgendamento(editAg.value.id, {
      status_presenca: editForm.value.status_presenca,
      extras
    })
    
    showModal.value = false
    await carregarPacote()
    alert('✅ Agendamento atualizado! Totais recalculados.')
  } catch (err) {
    alert('Erro: ' + (err.message || err))
  }
}

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString('pt-BR')
}

onMounted(carregarPacote)
</script>

<style scoped>
.pacote-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

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
  font-size: 1.5rem;
  cursor: pointer;
}

.status {
  margin-left: auto;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
}

.status.em_aberto { background: #fed7d7; color: #c53030; }
.status.pago { background: #c6f6d5; color: #22543d; }
.status.parcial { background: #feebc8; color: #744210; }

.metrics {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.btn-gerar {
  background: #4299e1;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.banhos-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.banhos-section h3 {
  margin-bottom: 1rem;
  color: #2d3748;
}

.banhos-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.banhos-table th,
.banhos-table td {
  padding: 1rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.banhos-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
}

.banhos-table tr:hover {
  background: #f7fafc;
}

.banhos-table tr.pendente { opacity: 0.7; }
.banhos-table tr.concluido { background: #f0fff4; }
.banhos-table tr.faltou { background: #fff5f5; }

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.total-row {
  background: #e6fffa;
  font-size: 1.1rem;
}

.total-row strong {
  color: #22543d;
}

.btn-edit-small {
  background: #ed8936;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.empty {
  text-align: center;
  padding: 3rem;
  color: #718096;
  font-style: italic;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  inset: 0;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

select, textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-family: monospace;
  box-sizing: border-box;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  flex: 1;
  background: #a0aec0;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-save {
  flex: 1;
  background: #48bb78;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
}

/* Loading */
.pacote-detail:deep(.loading) {
  opacity: 0.6;
  pointer-events: none;
}
</style>

