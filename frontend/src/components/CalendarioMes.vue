<template>
  <div class="calendario">
    <div class="cal-header">
      <button @click="mesAnterior" class="cal-nav-btn">‹</button>
      <h4 class="cal-titulo">{{ nomeMes }} {{ anoAtual }}</h4>
      <button @click="mesProximo" class="cal-nav-btn">›</button>
    </div>

    <div class="dias-semana">
      <span v-for="dia in diasSemana" :key="dia">{{ dia }}</span>
    </div>

    <div class="dias-grid">
      <span
        v-for="(dia, index) in diasCalendario"
        :key="index"
        :class="{
          'outro-mes': !dia.atual,
          'hoje': dia.hoje,
          'tem-banho': dia.temBanho,
          'selecionado': props.dataSelecionada === getDataDia(dia)
        }"
        @click="dia.atual && selecionarData(dia)"
      >{{ dia.numero }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  banhos: { type: Array, default: () => [] },
  dataSelecionada: { type: String, default: '' }
})
const emit = defineEmits(['data-selecionada'])

const dataAtual = ref(new Date())
const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
const anoAtual = computed(() => dataAtual.value.getFullYear())
const mesAtual = computed(() => dataAtual.value.getMonth())
const nomeMes = computed(() => ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'][mesAtual.value])

const diasCalendario = computed(() => {
  const ano = anoAtual.value, mes = mesAtual.value
  const primeiroDia = new Date(ano, mes, 1)
  const ultimoDia = new Date(ano, mes + 1, 0)
  const dias = []
  const hoje = new Date()

  for (let i = primeiroDia.getDay() - 1; i >= 0; i--) {
    const data = new Date(ano, mes, -i)
    dias.push({ numero: data.getDate(), atual: false, hoje: false, temBanho: false })
  }
  for (let i = 1; i <= ultimoDia.getDate(); i++) {
    const data = new Date(ano, mes, i)
    const dataStr = data.toISOString().split('T')[0]
    dias.push({
      numero: i, atual: true,
      hoje: data.toDateString() === hoje.toDateString(),
      temBanho: props.banhos.some(b => b.data_banho === dataStr)
    })
  }
  const restante = 42 - dias.length
  for (let i = 1; i <= restante; i++)
    dias.push({ numero: i, atual: false, hoje: false, temBanho: false })

  return dias
})

function getDataDia(dia) {
  return new Date(anoAtual.value, mesAtual.value, dia.numero).toISOString().split('T')[0]
}
function selecionarData(dia) { emit('data-selecionada', getDataDia(dia)) }
function mesAnterior() { dataAtual.value = new Date(anoAtual.value, mesAtual.value - 1, 1) }
function mesProximo() { dataAtual.value = new Date(anoAtual.value, mesAtual.value + 1, 1) }
</script>

<style scoped>
.calendario {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
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
}

.cal-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.9rem;
}
.cal-nav-btn {
  width: 32px; height: 32px; border-radius: 7px;
  background: var(--creme-escuro); border: none;
  color: var(--marrom); font-size: 1.1rem; font-weight: 800;
  cursor: pointer; transition: background 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.cal-nav-btn:hover { background: var(--dourado-claro); }
.cal-titulo { font-size: 0.95rem; font-weight: 800; color: var(--marrom); margin: 0; }

.dias-semana {
  display: grid; grid-template-columns: repeat(7, 1fr);
  text-align: center; margin-bottom: 0.4rem;
}
.dias-semana span {
  font-size: 0.7rem; font-weight: 800;
  color: var(--text-muted); text-transform: uppercase;
  padding: 0.25rem 0;
}

.dias-grid {
  display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px;
}
.dias-grid span {
  text-align: center; padding: 6px 2px; border-radius: 6px;
  font-size: 0.85rem; font-weight: 600; color: var(--text);
  cursor: pointer; transition: all 0.15s; position: relative;
}
.dias-grid span:hover { background: var(--dourado-claro); color: var(--marrom); }

.dias-grid .outro-mes { color: var(--creme-escuro); pointer-events: none; }

.dias-grid .hoje {
  background: var(--marrom); color: var(--dourado); font-weight: 800;
}
.dias-grid .hoje:hover { background: var(--marrom-medio); }

.dias-grid .tem-banho {
  background: var(--verde-bg); color: var(--verde); font-weight: 700;
}
.dias-grid .tem-banho::after {
  content: '';
  position: absolute; bottom: 2px; left: 50%;
  transform: translateX(-50%);
  width: 4px; height: 4px;
  background: var(--verde); border-radius: 50%;
}

.dias-grid .selecionado {
  background: var(--dourado); color: var(--marrom); font-weight: 800;
  box-shadow: 0 2px 8px rgba(212,168,67,0.4);
}
</style>
