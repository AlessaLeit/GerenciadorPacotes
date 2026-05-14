<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo">
        <span class="icon">🐾</span>
        <h1>Recanto Mini Dogs</h1>
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
          {{ error }}
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Processando...' : 'Entrar' }}
        </button>
      </form>
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
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
.logo {
  text-align: center;
  margin-bottom: 2rem;
}
.logo .icon { font-size: 3rem; }
.logo h1 { font-size: 1.5rem; color: #2d3748; margin-top: 0.5rem; }

.form-group { margin-bottom: 1.25rem; }
.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 0.5rem;
}
.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}
.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}
.error-message { color: #e53e3e; font-size: 0.875rem; margin-top: 0.5rem; text-align: center; }
</style>