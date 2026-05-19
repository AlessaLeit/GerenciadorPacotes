<template>
  <div class="login-container">
    <div class="login-card">

      <div class="logo">
        <div class="logo-icon">🐾</div>
        <h1 class="logo-titulo">Recanto Mini Dogs</h1>
        <p class="logo-sub">Canil · Banho &amp; Tosa</p>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label>E-mail</label>
          <input v-model="form.email" type="email" placeholder="seu@email.com" required />
        </div>

        <div class="form-group">
          <label>Senha</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>

        <div v-if="error" class="error-message">
          ⚠️ {{ error }}
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="btn-loading">⏳ Processando...</span>
          <span v-else>Entrar</span>
        </button>
      </form>

      <div class="login-footer">
        Recanto Mini Dogs © {{ new Date().getFullYear() }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const error = ref('')

const form = reactive({
  email: '',
  password: ''
})

async function handleSubmit() {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.email, form.password)
    router.push('/')
  } catch (err) {
    error.value = err || 'Ocorreu um erro ao processar sua solicitação.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── VARIÁVEIS ── */
.login-container {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
  --marrom-claro:  #8b6340;
  --dourado:       #d4a843;
  --dourado-claro: #f5e4a8;
  --dourado-bg:    #fdf6e3;
  --verde:         #6b8f4e;
  --creme:         #faf6ef;
  --creme-escuro:  #f0e8d8;
  --text:          #2e1e0f;
  --text-muted:    #7a6251;
  --white:         #ffffff;
  --radius:        12px;
  --shadow:        0 8px 32px rgba(59,42,26,0.18);

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;

  /* Fundo com padrão de patinhas sutil */
  background-color: var(--marrom);
  background-image:
    radial-gradient(circle at 20% 20%, rgba(212,168,67,0.12) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(107,143,78,0.1) 0%, transparent 50%);
}

/* ── CARD ── */
.login-card {
  background: var(--white);
  padding: 2.5rem 2.25rem 1.75rem;
  border-radius: 18px;
  box-shadow: var(--shadow);
  width: 100%;
  max-width: 400px;
  border-top: 6px solid var(--dourado);
}

/* ── LOGO ── */
.logo {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  background: var(--marrom);
  border-radius: 50%;
  font-size: 2rem;
  margin-bottom: 0.9rem;
  border: 4px solid var(--dourado);
  box-shadow: 0 4px 16px rgba(59,42,26,0.25);
}

.logo-titulo {
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--marrom);
  margin: 0 0 0.25rem;
  line-height: 1.2;
}

.logo-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ── FORMULÁRIO ── */
.login-form { margin-top: 0.5rem; }

.form-group { margin-bottom: 1.25rem; }

.form-group label {
  display: block;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--marrom);
  margin-bottom: 0.4rem;
}

.form-group input {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border: 2px solid var(--creme-escuro);
  border-radius: 8px;
  font-size: 0.95rem;
  color: var(--text);
  background: var(--creme);
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: var(--dourado);
  box-shadow: 0 0 0 3px rgba(212,168,67,0.15);
  background: var(--white);
}

.form-group input::placeholder { color: #b5a090; }

/* ── ERRO ── */
.error-message {
  background: #fdeaea;
  border: 1px solid #f5c0c0;
  border-radius: 8px;
  color: #b94040;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.65rem 0.9rem;
  margin-bottom: 0.75rem;
  text-align: center;
}

/* ── BOTÃO ── */
.btn-submit {
  width: 100%;
  padding: 0.8rem;
  background: var(--marrom);
  color: var(--dourado);
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  margin-top: 0.5rem;
  letter-spacing: 0.3px;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: 0 3px 10px rgba(59,42,26,0.25);
}

.btn-submit:hover:not(:disabled) {
  background: var(--marrom-medio);
  transform: translateY(-1px);
  box-shadow: 0 5px 16px rgba(59,42,26,0.3);
}

.btn-submit:active:not(:disabled) { transform: translateY(0); }

.btn-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-loading { opacity: 0.85; }

/* ── RODAPÉ ── */
.login-footer {
  text-align: center;
  margin-top: 1.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--creme-escuro);
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
}
</style>