<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="nav-brand-icon">🐾</span>
        <div class="nav-brand-text">
          <span class="nav-brand-nome">Recanto Mini Dogs</span>
          <span class="nav-brand-sub">Canil · Banho &amp; Tosa</span>
        </div>
      </div>
      <ul class="nav-links">
        <li><router-link to="/">🏠 Dashboard</router-link></li>
        <li><router-link to="/pacotes">📦 Pacotes</router-link></li>
        <li><router-link to="/clientes">👥 Clientes</router-link></li>
        <li><router-link to="/relatorios">📊 Relatórios</router-link></li>
      </ul>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// Componente raiz - layout principal com navegação
</script>

<style>
/* ══════════════════════════════════════
   VARIÁVEIS GLOBAIS — TEMA RECANTO
══════════════════════════════════════ */
:root {
  --marrom:        #3b2a1a;
  --marrom-medio:  #5a3e28;
  --marrom-claro:  #8b6340;
  --dourado:       #d4a843;
  --dourado-claro: #f5e4a8;
  --dourado-bg:    #fdf6e3;
  --verde:         #6b8f4e;
  --verde-claro:   #a8c47a;
  --verde-bg:      #eef4e6;
  --creme:         #faf6ef;
  --creme-escuro:  #f0e8d8;
  --text:          #2e1e0f;
  --text-muted:    #7a6251;
  --white:         #ffffff;
  --radius:        10px;
  --shadow:        0 2px 12px rgba(59,42,26,0.1);
  --shadow-md:     0 4px 20px rgba(59,42,26,0.14);
}

/* ══ RESET ══ */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--creme);
  color: var(--text);
  min-height: 100vh;
}

/* ══ NAVBAR ══ */
.navbar {
  background: var(--marrom);
  color: var(--white);
  padding: 0 2rem;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 3px 16px rgba(0,0,0,0.25);
  border-bottom: 3px solid var(--dourado);
  position: sticky;
  top: 0;
  z-index: 100;
}

/* BRAND */
.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.nav-brand-icon {
  font-size: 1.6rem;
  width: 42px;
  height: 42px;
  background: var(--dourado);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.nav-brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.nav-brand-nome {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--dourado);
  letter-spacing: 0.3px;
}

.nav-brand-sub {
  font-size: 0.68rem;
  color: rgba(255,255,255,0.5);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* LINKS */
.nav-links {
  display: flex;
  list-style: none;
  gap: 4px;
}

.nav-links a {
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 7px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-links a:hover {
  color: var(--white);
  background: rgba(255,255,255,0.08);
}

.nav-links a.router-link-active {
  background: var(--dourado);
  color: var(--marrom);
  border-color: var(--dourado-claro);
  font-weight: 700;
}

/* ══ CONTEÚDO PRINCIPAL ══ */
.main-content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

/* ══ CARD GLOBAL ══ */
.card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
}

/* ══ BOTÕES GLOBAIS ══ */
.btn {
  padding: 0.55rem 1rem;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--marrom);
  color: var(--dourado);
}
.btn-primary:hover { background: var(--marrom-medio); }

.btn-success {
  background: var(--verde);
  color: var(--white);
}
.btn-success:hover { background: #5a7c3e; }

.btn-danger {
  background: #fdeaea;
  color: #b94040;
}
.btn-danger:hover { background: #f8c8c8; }

.btn-warning {
  background: var(--dourado);
  color: var(--marrom);
}
.btn-warning:hover { background: #c49838; }

.btn-secondary {
  background: var(--creme-escuro);
  color: var(--marrom);
}
.btn-secondary:hover { background: var(--dourado-claro); }

/* ══ GRIDS GLOBAIS ══ */
.grid { display: grid; gap: 1rem; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* ══ UTILITÁRIOS ══ */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-actions h1 {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--marrom);
  border-left: 5px solid var(--dourado);
  padding-left: 0.75rem;
}

/* ══ RESPONSIVO ══ */
@media (max-width: 768px) {
  .grid-2,
  .grid-3,
  .grid-4 {
    grid-template-columns: 1fr;
  }

  .navbar {
    padding: 0 1rem;
    height: auto;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
  }

  .nav-links {
    gap: 2px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-links a {
    font-size: 0.82rem;
    padding: 6px 10px;
  }

  .main-content {
    padding: 0 1rem;
    margin: 1rem auto;
  }
}
</style>
