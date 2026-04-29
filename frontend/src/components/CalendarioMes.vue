<template>
  <div class="calendario">
    <div class="calendario-header">
      <button @click="mesAnterior">‹</button>
      <h4>{{ nomeMes }} {{ anoAtual }}</h4>
      <button @click="mesProximo">›</button>
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
        >
          {{ dia.numero }}
        </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  banhos: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['data-selecionada'])

const dataAtual = ref(new Date())
const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

const anoAtual = computed(() => dataAtual.value.getFullYear())
const mesAtual = computed(() => dataAtual.value.getMonth())

const nomeMes = computed(() => {
  const meses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]
  return meses[mesAtual.value]
})

const diasCalendario = computed(() => {
  const ano = anoAtual.value
  const mes = mesAtual.value
  
  const primeiroDia = new Date(ano, mes, 1)
  const ultimoDia = new Date(ano, mes + 1, 0)
  
  const dias = []
  const hoje = new Date()
  
  const diaSemanaPrimeiro = primeiroDia.getDay()
  for (let i = diaSemanaPrimeiro - 1; i >= 0; i--) {
    const data = new Date(ano, mes, -i)
    dias.push({
      numero: data.getDate(),
      atual: false,
      hoje: false,
      temBanho: false
    })
  }
  
  for (let i = 1; i <= ultimoDia.getDate(); i++) {
    const data = new Date(ano, mes, i)
    const dataStr = data.toISOString().split('T')[0]
    
    dias.push({
      numero: i,
      atual: true,
      hoje: data.toDateString() === hoje.toDateString(),
      temBanho: Array.isArray(props.banhos) ? props.banhos.some(b => b.data_banho === dataStr) : false
    })
  }
  
  const restante = 42 - dias.length
  for (let i = 1; i <= restante; i++) {
    dias.push({
      numero: i,
      atual: false,
      hoje: false,
      temBanho: false
    })
  }
  
  return dias
})

function getDataDia(dia) {
  const ano = anoAtual.value
  const mes = mesAtual.value + 1 // JS months 0-indexed
  const data = new Date(ano, mesAtual.value, dia.numero)
  return data.toISOString().split('T')[0]
}

function selecionarData(dia) {
  const dataStr = getDataDia(dia)
  emit('data-selecionada', dataStr)
}

function mesAnterior() {
  dataAtual.value = new Date(anoAtual.value, mesAtual.value - 1, 1)
}

function mesProximo() {
  dataAtual.value = new Date(anoAtual.value, mesAtual.value + 1, 1)
}
</script>

<style scoped>
.calendario {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.calendario-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.calendario-header button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #667eea;
}

.calendario-header h4 {
  margin: 0;
  color: #2d3748;
}

.dias-semana {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 0.75rem;
  color: #718096;
  margin-bottom: 0.5rem;
}

.dias-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.dias-grid span {
  text-align: center;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.dias-grid span:hover {
  background: #f7fafc;
}

.dias-grid .outro-mes {
  color: #cbd5e0;
}

.dias-grid .hoje {
  background: #667eea;
  color: white;
  font-weight: bold;
}

.dias-grid .tem-banho {
  position: relative;
}

.dias-grid .tem-banho::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #48bb78;
  border-radius: 50%;
}
</style>