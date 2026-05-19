<template>
  <div class="clientes-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Clientes e Pets</h1>
      </div>
      <button @click="showNovoCliente = true" class="btn btn-primario">+ Novo Cliente</button>
    </div>

    <div class="search-card">
      <input
        v-model="busca"
        type="text"
        placeholder="🔍  Buscar por nome do cliente ou pet..."
        class="search-input"
      />
    </div>

    <div class="clientes-lista">
      <div v-for="cliente in clientesFiltrados" :key="cliente.id" class="cliente-card">
        <div class="cliente-header">
          <div>
            <h3 class="cliente-nome">{{ cliente.nome }}</h3>
            <div class="cliente-info">
              <span v-if="cliente.telefone">📞 {{ cliente.telefone }}</span>
              <span v-if="cliente.endereco">📍 {{ cliente.endereco }}</span>
            </div>
          </div>
          <div class="cliente-actions">
            <button @click="editarCliente(cliente)" class="btn btn-ghost btn-sm">✏️ Editar</button>
            <button @click="adicionarCachorro(cliente)" class="btn btn-dourado btn-sm">+ Pet</button>
            <button @click="confirmarExclusao(cliente)" class="btn btn-danger btn-sm">🗑️</button>
          </div>
        </div>

        <div class="cachorros-lista" v-if="cliente.cachorros?.length">
          <div class="pets-label">Pets:</div>
          <div v-for="dog in cliente.cachorros" :key="dog.id" class="cachorro-item">
            <div class="dog-header">
              <div class="dog-left">
                <span class="dog-nome">🐾 {{ dog.nome }}</span>
                <span class="dog-info">{{ dog.raca }} · {{ dog.porte }}</span>
              </div>
              <div class="dog-actions">
                <button @click="editarCachorro(cliente, dog)" class="btn btn-ghost btn-sm">Editar</button>
                <button @click="verPacotesCachorro(dog)" class="btn btn-verde btn-sm">📦 Pacotes</button>
                <button @click="confirmarExclusaoCachorro(cliente.id, dog)" class="btn btn-danger btn-sm">🗑️</button>
              </div>
            </div>
            <span v-if="dog.observacoes" class="dog-obs">{{ dog.observacoes }}</span>
          </div>
        </div>
        <div v-else class="no-pets">Nenhum pet cadastrado ainda.</div>
      </div>
    </div>

    <!-- Modal Cliente -->
    <div class="modal-wrap" v-if="showNovoCliente">
      <div class="modal-overlay" @click="showNovoCliente = false"></div>
      <div class="modal-content">
        <h3 class="modal-title">{{ editando ? 'Editar' : 'Novo' }} Cliente</h3>
        <form @submit.prevent="salvarCliente">
          <div class="form-group">
            <label>Nome *</label>
            <input v-model="formCliente.nome" required />
          </div>
          <div class="form-group">
            <label>Telefone</label>
            <input v-model="formCliente.telefone" />
          </div>
          <div class="form-group">
            <label>Endereço</label>
            <input v-model="formCliente.endereco" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showNovoCliente = false" class="btn btn-cancelar">Cancelar</button>
            <button type="submit" class="btn btn-primario">Salvar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Pet -->
    <div class="modal-wrap" v-if="showNovoCachorro">
      <div class="modal-overlay" @click="showNovoCachorro = false"></div>
      <div class="modal-content">
        <h3 class="modal-title">{{ editandoDog ? 'Editar' : 'Novo' }} Pet — {{ clienteAtual?.nome }}</h3>
        <form @submit.prevent="salvarCachorro">
          <div class="form-group">
            <label>Nome *</label>
            <input v-model="formCachorro.nome" required />
          </div>
          <div class="form-group">
            <label>Raça</label>
            <input v-model="formCachorro.raca" />
          </div>
          <div class="form-group">
            <label>Porte *</label>
            <select v-model="formCachorro.porte" required>
              <option value="pequeno">Pequeno</option>
              <option value="medio">Médio</option>
              <option value="grande">Grande</option>
            </select>
          </div>
          <div class="form-group">
            <label>Observações</label>
            <textarea v-model="formCachorro.observacoes" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showNovoCachorro = false" class="btn btn-cancelar">Cancelar</button>
            <button type="submit" class="btn btn-primario">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useClientesStore } from '../stores/clientes'

const router = useRouter()
const clientesStore = useClientesStore()

const busca = ref('')
const showNovoCliente = ref(false)
const showNovoCachorro = ref(false)
const editando = ref(false)
const editandoDog = ref(false)
const clienteAtual = ref(null)
const dogAtual = ref(null)

const formCliente = ref({ nome: '', telefone: '', endereco: '' })
const formCachorro = ref({ nome: '', raca: '', porte: 'medio', observacoes: '', cliente_id: null })

const clientesFiltrados = computed(() => {
  if (!busca.value) return clientesStore.clientes
  const termo = busca.value.toLowerCase()
  return clientesStore.clientes.filter(c => c.nome.toLowerCase().includes(termo))
})

function editarCliente(cliente) {
  editando.value = true
  clienteAtual.value = cliente
  formCliente.value = { ...cliente }
  showNovoCliente.value = true
}
function adicionarCachorro(cliente) {
  editandoDog.value = false
  clienteAtual.value = cliente
  formCachorro.value = { nome: '', raca: '', porte: 'medio', observacoes: '', cliente_id: cliente.id }
  showNovoCachorro.value = true
}
function editarCachorro(cliente, dog) {
  editandoDog.value = true
  clienteAtual.value = cliente
  dogAtual.value = dog
  formCachorro.value = { ...dog }
  showNovoCachorro.value = true
}
function verPacotesCachorro(dog) {
  router.push(`/pacotes?cachorro_id=${dog.id}`)
}
async function salvarCliente() {
  try {
    if (editando.value) {
      await clientesStore.atualizarCliente(clienteAtual.value.id, formCliente.value)
    } else {
      await clientesStore.criarCliente(formCliente.value)
    }
    showNovoCliente.value = false
    formCliente.value = { nome: '', telefone: '', endereco: '' }
    editando.value = false
  } catch (err) { alert('Erro: ' + err) }
}
async function salvarCachorro() {
  try {
    if (editandoDog.value) {
      await clientesStore.atualizarCachorro(clienteAtual.value.id, dogAtual.value.id, formCachorro.value)
      alert('Pet atualizado com sucesso!')
    } else {
      await clientesStore.adicionarCachorro(clienteAtual.value.id, formCachorro.value)
      alert('Pet adicionado com sucesso!')
    }
    showNovoCachorro.value = false
    formCachorro.value = { nome: '', raca: '', porte: 'medio', observacoes: '', cliente_id: null }
    editandoDog.value = false
  } catch (err) { alert('Erro ao salvar pet: ' + err) }
}
async function confirmarExclusao(cliente) {
  if (!confirm(`Excluir o cliente "${cliente.nome}" e todos os seus pets? Esta ação não pode ser desfeita.`)) return
  try {
    await clientesStore.deletarCliente(cliente.id)
    alert('Cliente excluído com sucesso!')
  } catch (err) { alert('Erro ao excluir cliente: ' + err) }
}
async function confirmarExclusaoCachorro(clienteId, dog) {
  if (!confirm(`Deseja excluir o pet "${dog.nome}"?`)) return
  try {
    await clientesStore.deletarCachorro(clienteId, dog.id)
    alert('Pet excluído com sucesso!')
  } catch (err) { alert('Erro ao excluir pet: ' + err) }
}
onMounted(() => { clientesStore.fetchClientes() })
</script>

<style scoped>
.clientes-view {
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

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.2rem;
}
.page-title {
  font-size: 1.6rem; font-weight: 800; color: var(--marrom);
  border-left: 5px solid var(--dourado); padding-left: 0.75rem;
}

/* SEARCH */
.search-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1rem 1.2rem;
  box-shadow: 0 2px 8px rgba(59,42,26,0.08);
  margin-bottom: 1.2rem;
}
.search-input {
  width: 100%; padding: 0.7rem 1rem;
  border: 2px solid var(--creme-escuro);
  border-radius: 8px; font-size: 0.95rem;
  color: var(--text); background: var(--creme);
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.search-input:focus { border-color: var(--dourado); outline: none; }
.search-input::placeholder { color: var(--text-muted); }

/* LISTA */
.clientes-lista { display: flex; flex-direction: column; gap: 1rem; }

.cliente-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.3rem 1.5rem;
  box-shadow: var(--shadow);
  border-left: 5px solid var(--marrom);
  transition: border-color 0.2s;
}
.cliente-card:hover { border-left-color: var(--dourado); }

.cliente-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 0.6rem;
}
.cliente-nome { font-size: 1.1rem; font-weight: 800; color: var(--marrom); margin: 0 0 4px; }
.cliente-info { display: flex; gap: 1rem; color: var(--text-muted); font-size: 0.88rem; font-weight: 600; }
.cliente-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }

/* PETS */
.pets-label { font-size: 0.78rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; margin-top: 0.8rem; }
.cachorros-lista { border-top: 2px solid var(--creme-escuro); padding-top: 0.8rem; margin-top: 0.8rem; }
.cachorro-item {
  background: var(--creme);
  padding: 0.7rem 1rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  border: 1px solid var(--creme-escuro);
}
.dog-header { display: flex; justify-content: space-between; align-items: center; }
.dog-left { display: flex; align-items: center; gap: 10px; }
.dog-nome { font-weight: 800; color: var(--marrom); font-size: 0.95rem; }
.dog-info { font-size: 0.82rem; color: var(--text-muted); }
.dog-actions { display: flex; gap: 0.4rem; }
.dog-obs { font-size: 0.8rem; color: var(--text-muted); font-style: italic; display: block; margin-top: 0.4rem; }
.no-pets { padding: 0.75rem; color: var(--text-muted); font-size: 0.9rem; font-style: italic; margin-top: 0.6rem; text-align: center; }

/* BOTÕES */
.btn {
  padding: 0.55rem 1rem; border: none; border-radius: 7px;
  font-weight: 700; cursor: pointer; font-size: 0.9rem; transition: all 0.15s;
}
.btn-primario { background: var(--marrom); color: var(--dourado); }
.btn-primario:hover { background: var(--marrom-medio); }
.btn-dourado { background: var(--dourado); color: var(--marrom); }
.btn-dourado:hover { background: #c49838; }
.btn-verde { background: var(--verde-bg); color: var(--verde); border: 1px solid var(--verde); }
.btn-verde:hover { background: var(--verde); color: white; }
.btn-ghost { background: var(--creme-escuro); color: var(--marrom); }
.btn-ghost:hover { background: var(--dourado-claro); }
.btn-danger { background: #fdeaea; color: #b94040; }
.btn-danger:hover { background: #f8c8c8; }
.btn-cancelar { background: var(--creme-escuro); color: var(--marrom); }
.btn-cancelar:hover { background: #e0d5c2; }
.btn-sm { padding: 0.35rem 0.75rem; font-size: 0.8rem; }

/* MODAL */
.modal-wrap {
  position: fixed; inset: 0;
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.45); }
.modal-content {
  background: var(--white);
  padding: 2rem; border-radius: var(--radius);
  width: 90%; max-width: 480px;
  position: relative; z-index: 1001;
  border-top: 5px solid var(--dourado);
  box-shadow: 0 8px 32px rgba(59,42,26,0.2);
}
.modal-title { font-size: 1.1rem; font-weight: 800; color: var(--marrom); margin-bottom: 1.2rem; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.3rem; font-weight: 700; font-size: 0.9rem; color: var(--marrom); }
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%; padding: 0.6rem 0.75rem;
  border: 2px solid var(--creme-escuro); border-radius: 7px;
  font-size: 0.95rem; color: var(--text); background: var(--creme);
  transition: border-color 0.15s; box-sizing: border-box;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus { border-color: var(--dourado); outline: none; }
.form-actions { display: flex; gap: 0.75rem; margin-top: 1.5rem; }
.form-actions .btn { flex: 1; }
</style>
