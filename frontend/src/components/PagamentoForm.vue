<template>
  <div class="pagamento-modal" v-if="show">
    <div class="modal-overlay" @click="$emit('close')"></div>
    <div class="modal-content">
      <div class="modal-icon">💰</div>
      <h3 class="modal-title">Registrar Pagamento</h3>
      <p class="pacote-info">
        Pacote <strong>{{ pacote?.tipo_plano }}</strong> —
        Valor cobrado: <strong>R$ {{ formatarValor(pacote?.valor_cobrado) }}</strong>
      </p>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Valor Pago (R$)</label>
          <input
            v-model.number="form.valor_pago"
            type="number"
            step="0.01"
            min="0"
            required
          />
        </div>
        <div class="form-group">
          <label>Data do Pagamento</label>
          <input
            v-model="form.data_pagamento"
            type="date"
            required
          />
        </div>
        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn btn-cancelar">Cancelar</button>
          <button type="submit" class="btn btn-confirmar">✅ Confirmar Pagamento</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ show: Boolean, pacote: Object })
const emit = defineEmits(['close', 'confirmar'])

const form = ref({
  valor_pago: 0,
  data_pagamento: new Date().toISOString().split('T')[0]
})

watch(() => props.pacote, (novo) => { if (novo) form.value.valor_pago = novo.valor_cobrado })

function handleSubmit() { emit('confirmar', { pacote_id: props.pacote.id, ...form.value }) }
function formatarValor(valor) { return Number(valor || 0).toFixed(2).replace('.', ',') }
</script>

<style scoped>
.pagamento-modal {
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

  position: fixed; inset: 0;
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.45);
}

.modal-content {
  background: var(--white);
  padding: 2rem; border-radius: var(--radius);
  width: 90%; max-width: 400px;
  position: relative; z-index: 1001;
  border-top: 5px solid var(--dourado);
  box-shadow: 0 8px 32px rgba(59,42,26,0.2);
  text-align: center;
}

.modal-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.modal-title { font-size: 1.15rem; font-weight: 800; color: var(--marrom); margin-bottom: 0.5rem; }

.pacote-info {
  color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.3rem;
  background: var(--creme); padding: 0.6rem 0.9rem;
  border-radius: 7px; text-align: left;
}
.pacote-info strong { color: var(--marrom); }

.form-group { margin-bottom: 1rem; text-align: left; }
.form-group label { display: block; margin-bottom: 0.3rem; font-weight: 700; font-size: 0.9rem; color: var(--marrom); }
.form-group input {
  width: 100%; padding: 0.65rem 0.75rem;
  border: 2px solid var(--creme-escuro); border-radius: 7px;
  font-size: 0.95rem; color: var(--text); background: var(--creme);
  transition: border-color 0.15s; box-sizing: border-box;
}
.form-group input:focus { border-color: var(--dourado); outline: none; }

.form-actions { display: flex; gap: 0.75rem; margin-top: 1.5rem; }
.btn { flex: 1; padding: 0.7rem 1rem; border: none; border-radius: 7px; font-weight: 700; cursor: pointer; font-size: 0.9rem; transition: all 0.15s; }
.btn-confirmar { background: var(--marrom); color: var(--dourado); }
.btn-confirmar:hover { background: var(--marrom-medio); }
.btn-cancelar { background: var(--creme-escuro); color: var(--marrom); }
.btn-cancelar:hover { background: #e0d5c2; }
</style>
