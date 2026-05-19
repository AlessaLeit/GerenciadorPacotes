<template>
  <div class="pacote-card" :class="{ inativo: !pacote.ativo }">
    <div class="card-header">
      <h3 class="plano-label">{{ tipoPlanoLabel }}</h3>
      <span class="badge" :class="statusClass">{{ statusPagamento }}</span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="info-label">Valor Cobrado</span>
        <span class="info-val">R$ {{ formatarValor(pacote.valor_cobrado) }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Valor Pago</span>
        <span class="info-val" :class="{ pendente: !pacote.valor_pago }">
          R$ {{ formatarValor(pacote.valor_pago || 0) }}
        </span>
      </div>
      <div class="info-row">
        <span class="info-label">Limite / Mês</span>
        <span class="info-val">{{ pacote.limite_banhos_mes }} banhos</span>
      </div>
      <div class="info-row" v-if="pacote.data_pagamento">
        <span class="info-label">Pago em</span>
        <span class="info-val">{{ formatarData(pacote.data_pagamento) }}</span>
      </div>
    </div>

    <div class="card-actions">
      <button
        v-if="pacote.status_pagamento === 'em_aberto'"
        @click="$emit('pagar', pacote)"
        class="btn btn-dourado"
      >💰 Registrar Pagamento</button>
      <button @click="$emit('detalhes', pacote)" class="btn btn-ghost">Ver Detalhes</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ pacote: { type: Object, required: true } })
defineEmits(['pagar', 'detalhes'])

const tipoPlanoLabel = computed(() => ({
  semanal: '📅 Semanal (4×/mês)',
  quinzenal: '📅 Quinzenal (2×/mês)',
  mensal: '📅 Mensal (1×/mês)'
}[props.pacote.tipo_plano] || props.pacote.tipo_plano))

const statusPagamento = computed(() => ({
  em_aberto: 'Em Aberto',
  pago: 'Pago',
  parcial: 'Parcial'
}[props.pacote.status_pagamento] || 'Desconhecido'))

const statusClass = computed(() => ({
  'badge-aberto':  props.pacote.status_pagamento === 'em_aberto',
  'badge-pago':    props.pacote.status_pagamento === 'pago',
  'badge-parcial': props.pacote.status_pagamento === 'parcial'
}))

function formatarValor(valor) { return Number(valor).toFixed(2).replace('.', ',') }
function formatarData(data) { return new Date(data).toLocaleDateString('pt-BR') }
</script>

<style scoped>
.pacote-card {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
  --dourado:       #d4a843;
  --dourado-claro: #f5e4a8;
  --verde:         #6b8f4e;
  --verde-bg:      #eef4e6;
  --creme:         #faf6ef;
  --creme-escuro:  #f0e8d8;
  --text:          #2e1e0f;
  --text-muted:    #7a6251;
  --white:         #ffffff;
  --radius:        10px;
  --shadow:        0 2px 12px rgba(59,42,26,0.1);

  background: var(--white);
  border-radius: var(--radius);
  border: 2px solid var(--creme-escuro);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.pacote-card:hover { border-color: var(--dourado); box-shadow: 0 4px 18px rgba(59,42,26,0.14); }
.pacote-card.inativo { opacity: 0.6; background: var(--creme); }

.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.2rem 0.8rem;
  border-bottom: 2px solid var(--creme-escuro);
}
.plano-label { font-size: 0.95rem; font-weight: 800; color: var(--marrom); margin: 0; }

.badge {
  padding: 3px 10px; border-radius: 5px;
  font-size: 0.75rem; font-weight: 800;
}
.badge-aberto  { background: var(--dourado-claro); color: #6b4c00; }
.badge-pago    { background: var(--verde-bg); color: var(--verde); }
.badge-parcial { background: #fef0e0; color: #8b5e00; }

.card-body { padding: 0.9rem 1.2rem; }
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.5rem 0; border-bottom: 1px solid var(--creme-escuro);
  font-size: 0.9rem;
}
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--text-muted); font-weight: 600; }
.info-val { font-weight: 800; color: var(--marrom); }
.info-val.pendente { color: #b94040; }

.card-actions {
  display: flex; gap: 0.5rem;
  padding: 0.9rem 1.2rem;
  border-top: 2px solid var(--creme-escuro);
  background: var(--creme);
}
.btn { flex: 1; padding: 0.55rem 0.75rem; border: none; border-radius: 7px; font-weight: 700; cursor: pointer; font-size: 0.88rem; transition: all 0.15s; }
.btn-dourado { background: var(--dourado); color: var(--marrom); }
.btn-dourado:hover { background: #c49838; }
.btn-ghost { background: var(--creme-escuro); color: var(--marrom); }
.btn-ghost:hover { background: var(--dourado-claro); }
</style>
