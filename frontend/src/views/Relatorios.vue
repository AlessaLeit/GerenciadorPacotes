<template>
  <div class="relatorios-view">
    <div class="page-header">
      <h1 class="page-title">Relatórios Mensais</h1>
    </div>

    <div class="filtros-card">
      <div class="form-group">
        <label>Mês</label>
        <select v-model="mes">
          <option v-for="(nome, index) in meses" :key="index" :value="index + 1">{{ nome }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>Ano</label>
        <input v-model.number="ano" type="number" min="2020" max="2030" />
      </div>
      <button @click="gerarRelatorio" class="btn btn-primario" :disabled="loading">
        {{ loading ? 'Gerando...' : '📊 Gerar Relatório' }}
      </button>
    </div>

    <div v-if="relatorio" class="relatorio-resultado">
      <div class="resultado-titulo">
        Resumo de {{ relatorio.periodo.nome_mes }} / {{ relatorio.periodo.ano }}
      </div>

      <div class="resumo-grid">
        <div class="resumo-card banhos">
          <div class="resumo-icone">🛁</div>
          <div class="resumo-valor">{{ relatorio.resumo.total_banhos_realizados }}</div>
          <div class="resumo-label">Banhos Realizados</div>
        </div>
        <div class="resumo-card prevista">
          <div class="resumo-icone">📋</div>
          <div class="resumo-valor">R$ {{ formatarValor(relatorio.resumo.receita_prevista) }}</div>
          <div class="resumo-label">Receita Prevista</div>
        </div>
        <div class="resumo-card recebida">
          <div class="resumo-icone">✅</div>
          <div class="resumo-valor">R$ {{ formatarValor(relatorio.resumo.receita_recebida) }}</div>
          <div class="resumo-label">Receita Recebida</div>
        </div>
        <div class="resumo-card pendente">
          <div class="resumo-icone">⏳</div>
          <div class="resumo-valor">R$ {{ formatarValor(relatorio.resumo.receita_pendente) }}</div>
          <div class="resumo-label">Pendente</div>
        </div>
      </div>

      <div class="taxa-bar">
        Taxa de Recebimento: <strong>{{ relatorio.resumo.taxa_recebimento }}%</strong>
      </div>

      <div class="detalhes-grid">
        <div class="card" v-if="relatorio.detalhes.pacotes_em_aberto.length">
          <div class="card-title"><span class="card-title-bar"></span>📋 Pacotes em Aberto ({{ relatorio.detalhes.pacotes_em_aberto.length }})</div>
          <div class="lista-scroll">
            <div
              v-for="item in relatorio.detalhes.pacotes_em_aberto"
              :key="item.pacote_id"
              class="lista-item"
            >
              <div class="item-titulo">{{ item.cachorro.nome }} — {{ item.cliente.nome }}</div>
              <div class="item-sub">{{ item.tipo_plano }} · R$ {{ formatarValor(item.valor_cobrado) }}</div>
              <div class="item-contato" v-if="item.cliente.telefone">📞 {{ item.cliente.telefone }}</div>
            </div>
          </div>
        </div>

        <div class="card" v-if="relatorio.detalhes.banhos_com_observacoes.length">
          <div class="card-title"><span class="card-title-bar"></span>📝 Banhos com Observações</div>
          <div class="lista-scroll">
            <div
              v-for="item in relatorio.detalhes.banhos_com_observacoes"
              :key="item.banho_id"
              class="lista-item"
            >
              <div class="item-titulo">{{ item.cachorro.nome }} — {{ formatarData(item.data_banho) }}</div>
              <div class="item-obs">{{ item.observacao }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
const hoje = new Date()
const mes = ref(hoje.getMonth() + 1)
const ano = ref(hoje.getFullYear())
const loading = ref(false)
const relatorio = ref(null)

async function gerarRelatorio() {
  loading.value = true
  try {
    const response = await api.get('/relatorios/mensal', { params: { ano: ano.value, mes: mes.value } })
    relatorio.value = response.data
  } catch (err) { alert('Erro ao gerar relatório: ' + (err.response?.data?.detail || err)) }
  finally { loading.value = false }
}
function formatarValor(valor) { return Number(valor || 0).toFixed(2).replace('.', ',') }
function formatarData(data) { return new Date(data).toLocaleDateString('pt-BR') }
</script>

<style scoped>
.relatorios-view {
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
}

.page-header { margin-bottom: 1.2rem; }
.page-title {
  font-size: 1.6rem; font-weight: 800; color: var(--marrom);
  border-left: 5px solid var(--dourado); padding-left: 0.75rem;
}

/* FILTROS */
.filtros-card {
  background: var(--white); border-radius: var(--radius);
  padding: 1.2rem 1.4rem; box-shadow: var(--shadow);
  display: flex; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem; border-left: 5px solid var(--marrom);
}
.form-group { flex: 1; margin-bottom: 0; }
.form-group label { display: block; margin-bottom: 0.3rem; font-weight: 700; font-size: 0.88rem; color: var(--marrom); }
.form-group select,
.form-group input {
  width: 100%; padding: 0.6rem 0.75rem;
  border: 2px solid var(--creme-escuro); border-radius: 7px;
  font-size: 0.95rem; color: var(--text); background: var(--creme);
  transition: border-color 0.15s; box-sizing: border-box;
}
.form-group select:focus, .form-group input:focus { border-color: var(--dourado); outline: none; }

/* BOTÃO */
.btn { padding: 0.65rem 1.4rem; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 0.95rem; transition: all 0.15s; }
.btn-primario { background: var(--marrom); color: var(--dourado); }
.btn-primario:hover { background: var(--marrom-medio); }
.btn-primario:disabled { opacity: 0.6; cursor: not-allowed; }

/* RESULTADO */
.resultado-titulo {
  font-size: 1.15rem; font-weight: 800; color: var(--marrom);
  margin-bottom: 1.2rem; padding-left: 0.75rem;
  border-left: 5px solid var(--dourado);
}

/* RESUMO CARDS */
.resumo-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.2rem; }
.resumo-card {
  border-radius: var(--radius); padding: 1.3rem 1rem; text-align: center;
  color: var(--white); box-shadow: var(--shadow);
}
.resumo-card.banhos   { background: var(--marrom); }
.resumo-card.prevista { background: var(--marrom-claro); }
.resumo-card.recebida { background: var(--verde); }
.resumo-card.pendente { background: #9b6b3a; }
.resumo-icone { font-size: 1.6rem; margin-bottom: 0.4rem; }
.resumo-valor { font-size: 1.6rem; font-weight: 800; line-height: 1.1; }
.resumo-label { font-size: 0.78rem; opacity: 0.85; margin-top: 4px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

/* TAXA */
.taxa-bar {
  text-align: center; padding: 0.9rem;
  background: var(--dourado-bg); border-radius: var(--radius);
  border: 2px solid var(--dourado-claro);
  margin-bottom: 1.5rem; font-size: 1rem; color: var(--marrom);
  font-weight: 700;
}
.taxa-bar strong { font-size: 1.2rem; color: var(--marrom); }

/* DETALHES */
.detalhes-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
.card {
  background: var(--white); border-radius: var(--radius);
  padding: 1.3rem; box-shadow: var(--shadow);
}
.card-title {
  font-size: 0.95rem; font-weight: 800; color: var(--marrom);
  display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;
  padding-bottom: 0.7rem; border-bottom: 2px solid var(--creme-escuro);
}
.card-title-bar { display: inline-block; width: 4px; height: 15px; background: var(--dourado); border-radius: 2px; }

.lista-scroll { max-height: 380px; overflow-y: auto; }
.lista-item {
  padding: 0.9rem 0.6rem; border-bottom: 1px solid var(--creme-escuro);
}
.lista-item:last-child { border-bottom: none; }
.item-titulo { font-weight: 800; color: var(--marrom); font-size: 0.95rem; }
.item-sub { font-size: 0.83rem; color: var(--text-muted); margin-top: 2px; font-weight: 600; }
.item-contato { font-size: 0.83rem; color: var(--verde); margin-top: 3px; font-weight: 700; }
.item-obs {
  font-size: 0.85rem; color: var(--text-muted); margin-top: 6px;
  font-style: italic; background: var(--creme);
  padding: 0.4rem 0.6rem; border-radius: 5px;
}
</style>
