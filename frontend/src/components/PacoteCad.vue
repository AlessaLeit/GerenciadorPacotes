<template>
  <div class="pacote-card" :class="{ inativo: !pacote.ativo }">
    <header>
      <h3>{{ nomeCachorro }}</h3>
      <p v-if="clienteNome">Cliente: {{ clienteNome }}</p>
      <p v-if="observacoes" class="observacoes">{{ observacoes }}</p>
    </header>
    <div class="status-badge" :class="statusClass">{{ statusLabel }}</div>
    <div class="metrics-grid">
      <div><strong>Tipo do Plano:</strong> {{ tipoPlanoLabel }}</div>
      <div><strong>Valor Cobrado:</strong> {{ formatarValor(valorCobrado) }}</div>
      <div><strong>Valor Pago:</strong> {{ formatarValor(valorPago) }}</div>
      <div><strong>Agendamentos:</strong> {{ totalAgendamentos }}/{{ limiteMensal }}</div>
      <div v-if="dataPagamento"><strong>Data de Pagamento:</strong> {{ formatarData(dataPagamento) }}</div>
    </div>
    <div class="buttons">
      <button v-if="isAberto" @click="emit('pagar', pacote)" class="btn-pagar">Pagar</button>
      <button @click="emit('detalhes', pacote)" class="btn-detalhes">Detalhes</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  pacote: { type: Object, required: true }
})

const emit = defineEmits(['pagar', 'detalhes'])

const nomeCachorro = computed(() => props.pacote.cachorro?.nome || 'Pacote')
const clienteNome = computed(() => props.pacote.cachorro?.cliente?.nome)
const observacoes = computed(() => props.pacote.observacoes)
const tipoPlano = computed(() => props.pacote.tipo_plano)
const valorCobrado = computed(() => props.pacote.valor_cobrado)
const valorPago = computed(() => props.pacote.valor_pago)
const dataPagamento = computed(() => props.pacote.data_pagamento)

const tipoPlanoLabel = computed(() => {
  const map = { semanal: 'Semanal', quinzenal: 'Quinzenal', mensal: 'Mensal' }
  return map[tipoPlano.value] || tipoPlano.value?.toUpperCase() || 'Plano'
})

const limiteMensal = computed(() => {
  if (props.pacote.limite_banhos_mes != null) return props.pacote.limite_banhos_mes
  const map = { semanal: 4, quinzenal: 2, mensal: 1 }
  return map[tipoPlano.value] || 0
})

const totalAgendamentos = computed(() => {
  if (typeof props.pacote.total_agendamentos === 'number' && !isNaN(props.pacote.total_agendamentos)) return props.pacote.total_agendamentos
  return props.pacote.agendamentos?.length || 0
})

const statusLabel = computed(() => {
  if (!props.pacote.ativo) return 'Inativo'
  const status = props.pacote.status_pagamento
  if (status === 'em_aberto') return 'Em Aberto'
  if (status === 'pago') return 'Pago'
  if (status === 'parcial') return 'Parcial'
  return props.pacote.valor_pago > 0 ? 'Pago' : 'Em Aberto'
})

const statusClass = computed(() => {
  const label = statusLabel.value
  const map = { 'Inativo': 'status-inativo', 'Em Aberto': 'status-aberto', 'Pago': 'status-pago', 'Parcial': 'status-parcial' }
  return map[label]
})

const isAberto = computed(() => {
  if (!props.pacote.ativo) return false
  const status = props.pacote.status_pagamento
  if (status) return status === 'em_aberto'
  const pago = props.pacote.valor_pago
  return !pago || pago <= 0
})

const formatarValor = (valor) => {
  if (valor == null || valor === '') return '0,00'
  const num = typeof valor === 'string' ? parseFloat(valor.replace(',', '.')) : Number(valor)
  if (isNaN(num)) return '0,00'
  return num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatarData = (data) => {
  if (!data) return '-'
  try {
    return new Date(data).toLocaleDateString('pt-BR')
  } catch {
    return '-'
  }
}
</script>

<style scoped>
.pacote-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin: 8px;
  background: white;
  transition: box-shadow 0.2s, opacity 0.2s;
  opacity: 1;
}

.pacote-card.inativo {
  opacity: 0.6;
}

.pacote-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

header h3 {
  margin: 0 0 8px 0;
  font-size: 1.2em;
}

header p {
  margin: 4px 0;
  color: #666;
}

.observacoes {
  font-style: italic;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  font-weight: bold;
  margin-bottom: 16px;
}

.status-inativo {
  background: #ccc;
  color: #666;
}

.status-aberto {
  background: #ffcc00;
  color: #000;
}

.status-pago {
  background: #4caf50;
  color: white;
}

.status-parcial {
  background: #ff9800;
  color: white;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  margin: 16px 0;
}

.metrics-grid div {
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
}

.buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

.btn-pagar {
  background: #28a745;
  color: white;
}

.btn-pagar:hover {
  background: #218838;
}

.btn-detalhes {
  background: #007bff;
  color: white;
}

.btn-detalhes:hover {
  background: #0056b3;
}

@media (max-width: 600px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .buttons {
    flex-direction: column;
  }
}
</style>