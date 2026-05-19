<template>
  <div class="pacote-detail">

    <!-- Header -->
    <div class="header">
      <button @click="voltar" class="btn-back">← Voltar</button>
      <div class="header-info">
        <h1>{{ pacote?.pet_nome || 'Pacote' }}</h1>
        <p class="subheader">{{ pacote?.cliente_nome }}</p>
      </div>
      <div class="status-pill" :class="pacote?.status_pagamento">
        {{ pacote?.status_pagamento?.toUpperCase() || 'EM ABERTO' }}
      </div>
    </div>

    <!-- Info Cards -->
    <div class="info-cards">
      <div class="info-card clickable" @click="abrirEditarPacote" title="Clique para editar plano">
        <span class="info-label">Plano</span>
        <span class="info-value">{{ pacote?.tipo_plano?.toUpperCase() }}</span>
        <span class="info-sub">{{ pacote?.limite_banhos_mes }} banhos/mês</span>
      </div>

      <div class="info-card clickable" @click="abrirEditarPacote" title="Clique para editar dia">
        <span class="info-label">Dia da Semana</span>
        <span class="info-value">{{ formatarDiaSemana(pacote?.dia_da_semana) }}</span>
        <span class="info-sub">Datas geradas automaticamente</span>
      </div>

      <div class="info-card clickable" @click="abrirEditarPacote" title="Clique para editar valores">
        <span class="info-label">Valor Base do Banho</span>
        <span class="info-value">R$ {{ formatarValor(pacote?.valor_banho_base || 0) }}</span>
      </div>

      <div class="info-card clickable" @click="abrirEditarPacote" title="Clique para editar valores">
        <span class="info-label">Valor Cobrado (Pacote)</span>
        <span class="info-value">R$ {{ formatarValor(pacote?.valor_cobrado) }}</span>
      </div>

      <div class="info-card clickable" @click="abrirEditarPacote" title="Clique para editar transporte">
        <span class="info-label">Transporte</span>
        <span class="info-value">R$ {{ formatarValor(pacote?.valor_transporte || 0) }}</span>
        <span class="info-sub">Clique para alterar</span>
      </div>

      <div class="info-card">
        <span class="info-label">Qtd. Agendamentos</span>
        <span class="info-value">{{ pacote?.total_agendamentos || 0 }}</span>
      </div>
    </div>

    <!-- Ações -->
    <div class="actions-bar">
      <button @click="showAddExtra = true" class="btn btn-primario">
        + Adicionar Banho Extra
      </button>
    </div>

    <!-- Tabela de Agendamentos -->
    <div class="agendamentos-section">
      <h3 class="section-title"><span class="section-title-bar"></span> Agendamentos do Pacote</h3>

      <table class="agendamentos-table" v-if="agendamentos.length">
        <thead>
          <tr>
            <th>Data</th>
            <th>Valor Banho</th>
            <th>Itens Extra</th>
            <th>Valor Extra</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ag in agendamentos" :key="ag.id" :class="ag.status_presenca">
            <td><strong>{{ formatarData(ag.data_banho) }}</strong></td>
            <td>R$ {{ formatarValor(pacote?.valor_banho_base || 0) }}</td>
            <td class="clickable-cell" @click="abrirEditarExtras(ag)">{{ ag.extras?.info || '-' }}</td>
            <td class="clickable-cell" @click="abrirEditarExtras(ag)">R$ {{ formatarValor(ag.extras?.valor_extra || 0) }}</td>
            <td class="clickable-cell" @click="abrirEditarExtras(ag)">
              <span class="status-badge" :class="ag.status_presenca">
                {{ ag.status_presenca?.toUpperCase() }}
              </span>
            </td>
            <td>
              <div class="acoes">
                <button @click="abrirEditarExtras(ag)" class="btn-acao btn-acao-verde" title="Adicionar Item Extra">+</button>
                <button @click="abrirEditarData(ag)" class="btn-acao btn-acao-ghost" title="Editar data">📅</button>
                <button @click="confirmarRemover(ag)" class="btn-acao btn-acao-perigo" title="Remover">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="total-row">
            <td colspan="3" style="text-align:right"><strong>Total do Pacote (Banhos + Extras):</strong></td>
            <td colspan="3"><strong>R$ {{ formatarValor(totalPacote) }}</strong></td>
          </tr>
        </tfoot>
      </table>

      <div v-else class="empty-state">
        Nenhum agendamento encontrado.
      </div>
    </div>

    <!-- ── MODAL: Editar Data ── -->
    <div class="modal" v-if="showEditData">
      <div class="modal-overlay" @click="showEditData = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Editar Data</h3>
          <p class="modal-sub">🐶 {{ pacote?.pet_nome }}</p>
        </div>
        <p class="modal-info">Agendamento atual: <strong>{{ formatarData(agEditando?.data_banho) }}</strong></p>
        <div class="form-group">
          <label>Selecione a Nova Data</label>
          <input type="date" v-model="novaData" required />
        </div>
        <div class="modal-actions">
          <button @click="showEditData = false" class="btn btn-cancelar">Cancelar</button>
          <button @click="salvarNovaData" class="btn btn-primario" :disabled="!novaData">Salvar</button>
        </div>
      </div>
    </div>

    <!-- ── MODAL: Editar Dados do Pacote ── -->
    <div class="modal" v-if="showModalEditPacote">
      <div class="modal-overlay" @click="showModalEditPacote = false"></div>
      <div class="modal-content modal-wide">
        <div class="modal-header">
          <h3>Configurações do Pacote</h3>
          <p class="modal-sub">⚙️ {{ pacote?.pet_nome }}</p>
        </div>

        <div class="grid-form">
          <div class="form-group">
            <label>Tipo de Plano</label>
            <select v-model="formPacote.tipo_plano" @change="recalcularSugerido">
              <option value="semanal">Semanal (4 banhos)</option>
              <option value="quinzenal">Quinzenal (2 banhos)</option>
              <option value="mensal">Mensal (1 banho)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Dia da Semana</label>
            <select v-model="formPacote.dia_da_semana">
              <option value="terca">Terça-feira</option>
              <option value="quarta">Quarta-feira</option>
              <option value="quinta">Quinta-feira</option>
              <option value="sexta">Sexta-feira</option>
              <option value="sabado">Sábado</option>
            </select>
          </div>
        </div>

        <div class="grid-form">
          <div class="form-group">
            <label>Valor Base Banho (R$)</label>
            <input type="number" step="0.01" v-model.number="formPacote.valor_banho_base" @input="recalcularSugerido" />
          </div>
          <div class="form-group">
            <label>Transporte Total (R$)</label>
            <input type="number" step="0.01" v-model.number="formPacote.valor_transporte" />
          </div>
        </div>

        <div class="form-group form-highlight">
          <label>Valor Total Cobrado (R$)</label>
          <input type="number" step="0.01" v-model.number="formPacote.valor_cobrado" />
          <small v-if="sugestaoVisivel" class="helper-text">
            Sugerido pelo plano: R$ {{ formatarValor(valorSugerido) }}
          </small>
        </div>

        <div class="modal-actions">
          <button @click="showModalEditPacote = false" class="btn btn-cancelar">Cancelar</button>
          <button @click="salvarDadosPacote" class="btn btn-primario">Salvar Alterações</button>
        </div>
      </div>
    </div>

    <!-- ── MODAL: Editar Extras ── -->
    <div class="modal" v-if="showModalExtras">
      <div class="modal-overlay" @click="showModalExtras = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Editar Agendamento</h3>
          <p class="modal-sub">✨ {{ pacote?.pet_nome }}</p>
        </div>
        <div class="form-group">
          <label>Status de Presença</label>
          <select v-model="formExtras.status_presenca">
            <option value="pendente">🟡 PENDENTE</option>
            <option value="concluido">🟢 CONCLUÍDO</option>
            <option value="faltou">🔴 FALTOU / CANCELADO</option>
          </select>
        </div>
        <div class="form-group">
          <label>Itens Extra / Descrição</label>
          <input v-model="formExtras.info" placeholder="Ex: Tosa higiênica, Shampoo especial..." />
        </div>
        <div class="form-group">
          <label>Valor Extra (R$)</label>
          <input type="number" step="0.01" v-model.number="formExtras.valor_extra" />
        </div>
        <div class="modal-actions">
          <button @click="showModalExtras = false" class="btn btn-cancelar">Cancelar</button>
          <button @click="salvarExtras" class="btn btn-primario">Salvar</button>
        </div>
      </div>
    </div>

    <!-- ── MODAL: Adicionar Extra ── -->
    <div class="modal" v-if="showAddExtra">
      <div class="modal-overlay" @click="showAddExtra = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Banho Extra</h3>
          <p class="modal-sub">➕ {{ pacote?.pet_nome }}</p>
        </div>
        <p class="modal-info">Adicione um banho avulso fora do cronograma do plano.</p>
        <div class="form-group">
          <label>Data do Banho</label>
          <input type="date" v-model="dataExtra" required />
        </div>
        <div class="modal-actions">
          <button @click="showAddExtra = false" class="btn btn-cancelar">Cancelar</button>
          <button @click="salvarExtra" class="btn btn-primario" :disabled="!dataExtra">Adicionar</button>
        </div>
      </div>
    </div>

    <!-- ── MODAL: Confirmar Remoção ── -->
    <div class="modal" v-if="showConfirmRemove">
      <div class="modal-overlay" @click="showConfirmRemove = false"></div>
      <div class="modal-content">
        <div class="modal-header modal-header-danger">
          <h3>⚠️ Confirmar Remoção</h3>
        </div>
        <p class="modal-info">Tem certeza que deseja remover o agendamento de <strong>{{ formatarData(agRemovendo?.data_banho) }}</strong>?</p>
        <p class="warning-text">Esta ação não pode ser desfeita.</p>
        <div class="modal-actions">
          <button @click="showConfirmRemove = false" class="btn btn-cancelar">Cancelar</button>
          <button @click="executarRemover" class="btn btn-perigo">Remover</button>
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
const showModalExtras = ref(false)
const showModalEditPacote = ref(false)

// Dados dos modais
const agEditando = ref(null)
const novaData = ref('')
const dataExtra = ref('')
const agRemovendo = ref(null)
const agExtras = ref(null)
const formExtras = ref({ info: '', valor_extra: 0, status_presenca: 'pendente' })
const formPacote = ref({ tipo_plano: '', dia_da_semana: '', valor_banho_base: 0, valor_cobrado: 0, valor_transporte: 0 })
const valorSugerido = ref(0)
const sugestaoVisivel = ref(false)

const pacoteId = computed(() => parseInt(route.params.id))

const totalPacote = computed(() => {
  if (!pacote.value) return 0
  const valorBase = pacote.value.valor_banho_base || 0
  const transporte = pacote.value.valor_transporte || 0
  const agendamentosTotal = agendamentos.value.reduce((sum, ag) => {
    const valorExtra = ag.extras?.valor_extra || 0
    return sum + valorBase + valorExtra
  }, 0)
  return agendamentosTotal + transporte
})

async function carregarPacote() {
  loading.value = true
  try {
    const data = await pacotesStore.fetchPacote(pacoteId.value)
    pacote.value = data
    agendamentos.value = data.agendamentos || []
  } catch (err) {
  } finally {
    loading.value = false
  }
}

function voltar() { router.push('/pacotes') }

function formatarData(isoDate) {
  if (!isoDate) return '-'
  return new Date(isoDate + 'T00:00:00').toLocaleDateString('pt-BR')
}

function formatarValor(valor) {
  return Number(valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatarDiaSemana(dia) {
  const map = { terca: 'Terça', quarta: 'Quarta', quinta: 'Quinta', sexta: 'Sexta', sabado: 'Sábado' }
  return map[dia] || '-'
}

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
  } catch (err) {}
}

function abrirEditarPacote() {
  formPacote.value = {
    tipo_plano: pacote.value.tipo_plano,
    dia_da_semana: pacote.value.dia_da_semana,
    valor_banho_base: pacote.value.valor_banho_base,
    valor_cobrado: pacote.value.valor_cobrado,
    valor_transporte: pacote.value.valor_transporte || 0
  }
  recalcularSugerido()
  sugestaoVisivel.value = false
  showModalEditPacote.value = true
}

function recalcularSugerido() {
  const qtd = formPacote.value.tipo_plano === 'semanal' ? 4 : formPacote.value.tipo_plano === 'quinzenal' ? 2 : 1
  valorSugerido.value = (formPacote.value.valor_banho_base || 0) * qtd
  formPacote.value.valor_cobrado = valorSugerido.value
  sugestaoVisivel.value = true
}

async function salvarDadosPacote() {
  try {
    await pacotesStore.atualizarPacote(pacoteId.value, { ...formPacote.value })
    showModalEditPacote.value = false
    await carregarPacote()
  } catch (err) {
    console.error('Erro ao atualizar pacote:', err)
    alert('Erro ao salvar as alterações do pacote.')
  }
}

function abrirEditarExtras(ag) {
  agExtras.value = ag
  const info = ag.extras?.info || (typeof ag.extras === 'string' ? ag.extras : '')
  const valor = ag.extras?.valor_extra || 0
  formExtras.value = { info, valor_extra: valor, status_presenca: ag.status_presenca || 'pendente' }
  showModalExtras.value = true
}

async function salvarExtras() {
  try {
    await pacotesStore.updateAgendamento(agExtras.value.id, {
      status_presenca: formExtras.value.status_presenca,
      extras: { info: formExtras.value.info, valor_extra: formExtras.value.valor_extra }
    })
    showModalExtras.value = false
    await carregarPacote()
  } catch (err) {}
}

async function salvarExtra() {
  if (!dataExtra.value) return
  try {
    await pacotesStore.adicionarExtra(pacoteId.value, dataExtra.value)
    showAddExtra.value = false
    dataExtra.value = ''
  } catch (err) {}
}

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
  } catch (err) {}
}

onMounted(carregarPacote)
</script>

<style scoped>
/* ── VARIÁVEIS ── */
.pacote-detail {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
  --marrom-claro:  #8b6340;
  --dourado:       #d4a843;
  --dourado-claro: #f5e4a8;
  --dourado-bg:    #fdf6e3;
  --verde:         #6b8f4e;
  --verde-bg:      #eef4e6;
  --creme:         #faf6ef;
  --creme-escuro:  #f0e8d8;
  --text:          #2e1e0f;
  --text-muted:    #7a6251;
  --white:         #ffffff;
  --radius:        10px;
  --shadow:        0 2px 12px rgba(59,42,26,0.1);
  --shadow-md:     0 4px 20px rgba(59,42,26,0.15);

  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* ── HEADER ── */
.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.75rem;
  padding-bottom: 1.25rem;
  border-bottom: 2px solid var(--creme-escuro);
}

.btn-back {
  background: var(--creme-escuro);
  border: none;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--marrom);
  cursor: pointer;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  transition: background 0.15s;
  white-space: nowrap;
}
.btn-back:hover { background: var(--dourado-claro); }

.header-info { flex: 1; }
.header-info h1 { margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--marrom); }
.subheader { margin: 0.2rem 0 0; color: var(--text-muted); font-size: 0.9rem; font-weight: 600; }

.status-pill {
  padding: 0.45rem 1.1rem;
  border-radius: 20px;
  font-weight: 800;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.status-pill.em_aberto { background: var(--dourado-claro); color: #6b4c00; }
.status-pill.pago      { background: var(--verde-bg);      color: var(--verde); }
.status-pill.parcial   { background: #fef0e0;              color: #8b5e00; }

/* ── INFO CARDS ── */
.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.2rem 1.1rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 3px;
  border-bottom: 4px solid var(--marrom);
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.info-card:nth-child(2) { border-bottom-color: var(--dourado); }
.info-card:nth-child(3) { border-bottom-color: var(--verde); }
.info-card:nth-child(4) { border-bottom-color: var(--marrom-claro); }
.info-card:nth-child(5) { border-bottom-color: var(--verde); }

.info-card.clickable { cursor: pointer; }
.info-card.clickable:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  background: var(--dourado-bg);
  border-bottom-color: var(--dourado);
}

.info-label {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}
.info-value {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--marrom);
  line-height: 1.2;
}
.info-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 2px;
}

/* ── ACTIONS BAR ── */
.actions-bar {
  margin-bottom: 1.4rem;
  display: flex;
  justify-content: flex-end;
}

/* ── AGENDAMENTOS SECTION ── */
.agendamentos-section {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow);
}

.section-title {
  margin: 0 0 1.2rem;
  color: var(--marrom);
  font-size: 1.05rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-title-bar {
  display: inline-block;
  width: 4px; height: 18px;
  background: var(--dourado);
  border-radius: 2px;
  flex-shrink: 0;
}

/* ── TABELA ── */
.agendamentos-table {
  width: 100%;
  border-collapse: collapse;
}

.agendamentos-table th {
  padding: 0.85rem 0.9rem;
  text-align: left;
  background: var(--creme);
  font-weight: 800;
  color: var(--text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--creme-escuro);
}

.agendamentos-table td {
  padding: 0.85rem 0.9rem;
  border-bottom: 1px solid var(--creme-escuro);
  font-size: 0.9rem;
  color: var(--text);
}

.agendamentos-table tbody tr:last-child td { border-bottom: none; }
.agendamentos-table tbody tr:hover td { background: var(--creme); }

.agendamentos-table tr.pendente  td { opacity: 0.85; }
.agendamentos-table tr.concluido td { background: var(--verde-bg); }
.agendamentos-table tr.faltou    td { background: #fdf0f0; }

.clickable-cell {
  cursor: pointer;
  text-decoration: underline dotted var(--creme-escuro);
  transition: color 0.15s;
}
.clickable-cell:hover { color: var(--marrom); text-decoration-color: var(--dourado); }

/* STATUS BADGE */
.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 5px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.4px;
}
.status-badge.pendente  { background: var(--dourado-claro); color: #6b4c00; }
.status-badge.concluido { background: var(--verde-bg);      color: var(--verde); }
.status-badge.faltou    { background: #fdeaea;              color: #b94040; }

/* AÇÕES DA TABELA */
.acoes { display: flex; gap: 0.4rem; }

.btn-acao {
  border: none;
  padding: 0.38rem 0.7rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
  transition: all 0.15s;
  line-height: 1;
}
.btn-acao-verde  { background: var(--verde);      color: white; }
.btn-acao-verde:hover  { background: #588040; }
.btn-acao-ghost  { background: var(--creme-escuro); color: var(--marrom); border: 1px solid var(--creme-escuro); }
.btn-acao-ghost:hover  { background: var(--dourado-claro); border-color: var(--dourado); }
.btn-acao-perigo { background: #fdeaea; color: #b94040; border: 1px solid #f5c0c0; }
.btn-acao-perigo:hover { background: #f8c8c8; }

/* TOTAL ROW */
.total-row td {
  padding: 1rem 0.9rem;
  background: var(--dourado-bg);
  border-top: 2px solid var(--dourado);
  font-size: 1rem;
}
.total-row strong { color: var(--marrom); }

/* EMPTY */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
  font-style: italic;
}

/* ── BOTÕES GERAIS ── */
.btn {
  padding: 0.65rem 1.3rem;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.15s;
}
.btn-primario { background: var(--marrom); color: var(--dourado); }
.btn-primario:hover { background: var(--marrom-medio); }
.btn-primario:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-cancelar { background: var(--creme-escuro); color: var(--marrom); }
.btn-cancelar:hover { background: #e0d5c2; }

.btn-perigo { background: #fdeaea; color: #b94040; border: 1px solid #f5c0c0; }
.btn-perigo:hover { background: #f8c8c8; }

/* ── MODAIS ── */
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
  background: rgba(0,0,0,0.45);
}

.modal-content {
  background: var(--white);
  padding: 2rem;
  border-radius: var(--radius);
  width: 90%;
  max-width: 440px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  z-index: 1001;
  border-top: 5px solid var(--dourado);
  box-shadow: 0 8px 32px rgba(59,42,26,0.2);
}

.modal-wide { max-width: 560px; }

.modal-header { margin-bottom: 1.2rem; }
.modal-header h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--marrom);
}
.modal-header-danger h3 { color: #b94040; }
.modal-sub {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.88rem;
  font-weight: 600;
}
.modal-info {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.2rem;
  background: var(--creme);
  padding: 0.6rem 0.85rem;
  border-radius: 7px;
  border-left: 3px solid var(--dourado);
}
.modal-info strong { color: var(--marrom); }

.warning-text {
  color: #b94040;
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: -0.5rem;
  margin-bottom: 1.2rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
.modal-actions .btn { flex: 1; }

/* ── FORMULÁRIOS ── */
.form-group { margin-bottom: 1.1rem; }

.form-group label {
  display: block;
  margin-bottom: 0.35rem;
  font-weight: 700;
  color: var(--marrom);
  font-size: 0.88rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 2px solid var(--creme-escuro);
  border-radius: 7px;
  font-size: 0.95rem;
  color: var(--text);
  background: var(--creme);
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
}
.form-group input:focus,
.form-group select:focus {
  border-color: var(--dourado);
  box-shadow: 0 0 0 3px rgba(212,168,67,0.12);
  background: var(--white);
}

.grid-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.form-highlight input {
  border-color: var(--dourado);
  background: var(--dourado-bg);
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--marrom);
}

.helper-text {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: 0.3rem;
  display: block;
  font-style: italic;
}
</style>