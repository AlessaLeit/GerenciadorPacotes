<template>
  <div class="banho-item">
    <div class="banho-icone">🛁</div>
    <div class="banho-content">
      <div class="banho-date">{{ formatarData(banho.data_banho) }}</div>
      <div class="banho-obs" v-if="banho.observacao">{{ banho.observacao }}</div>
      <div class="banho-meta" v-if="showPacote">Pacote #{{ banho.pacote_id }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  banho: { type: Object, required: true },
  showPacote: { type: Boolean, default: false }
})

function formatarData(data) {
  return new Date(data).toLocaleDateString('pt-BR', { weekday: 'short', day: 'numeric', month: 'short' })
}
</script>

<style scoped>
.banho-item {
  --marrom:       #3b2a1a;
  --dourado:      #d4a843;
  --dourado-claro:#f5e4a8;
  --verde:        #6b8f4e;
  --creme:        #faf6ef;
  --creme-escuro: #f0e8d8;
  --text:         #2e1e0f;
  --text-muted:   #7a6251;

  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--creme);
  border-radius: 8px;
  border-left: 4px solid var(--dourado);
  margin-bottom: 0.5rem;
  transition: background 0.15s;
}
.banho-item:hover { background: var(--dourado-claro); }

.banho-icone { font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }

.banho-content { flex: 1; }
.banho-date { font-weight: 800; color: var(--marrom); font-size: 0.9rem; }
.banho-obs { font-size: 0.82rem; color: var(--text-muted); margin-top: 2px; font-style: italic; }
.banho-meta { font-size: 0.75rem; color: var(--verde); margin-top: 2px; font-weight: 700; }
</style>
