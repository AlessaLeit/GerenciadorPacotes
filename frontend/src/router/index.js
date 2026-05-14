/**
 * Configuração do Vue Router.
 * Define rotas para todas as views da aplicação.
 */
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Pacotes from '../views/Pacotes.vue'
import Clientes from '../views/Clientes.vue'
import Relatorios from '../views/Relatorios.vue'
import Login from '../views/Login.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { hideHeader: true }
  },
  {
    path: '/pacotes',
    name: 'Pacotes',
    component: Pacotes
  },
  {
    path: '/clientes',
    name: 'Clientes',
    component: Clientes
  },
  {
    path: '/relatorios',
    name: 'Relatorios',
    component: Relatorios
  },
  {
    path: '/pacotes/:id',
    name: 'PacoteDetail',
    component: () => import('../views/PacoteDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // Evita divergência entre store e localStorage.
  // Mesmo que o store demore/ falhe em inicializar, o guard usa o token persistido.
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token

  if (to.path !== '/login' && !isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})


export default router