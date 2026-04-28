# Canil Recanto Mini Dogs — Sistema de Gestão de Banho & Tosa

Sistema completo para gerenciamento de pacotes mensais de banho e tosa, controle de clientes/pets, agendamentos e relatórios financeiros.

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic |
| **Frontend** | Vue 3, Vite, Pinia, Vue Router, Axios |
| **Banco de Dados** | SQLite (desenvolvimento) / PostgreSQL (produção) |
| **Infraestrutura** | Docker, Docker Compose, Nginx |
| **Testes** | pytest, FastAPI TestClient |

---

## Funcionalidades Principais

### 1. Gestão de Clientes e Pets
- Cadastro completo de clientes (nome, telefone, endereço)
- Vínculo de múltiplos cachorros por cliente
- Cadastro de pets com raça, porte e observações médicas/comportamentais
- Busca e filtro de clientes

### 2. Controle de Pacotes Mensais
- Contratação de planos: Semanal (4 banhos), Quinzenal (2 banhos) ou Mensal (1 banho)
- Definição de valor cobrado por banho
- Geração automática de agendamentos ao criar pacote
- Registro de pagamentos e controle de status (em aberto / pago)
- Filtros por status de pagamento e ativação

### 3. Agenda Dinâmica e Relatórios
- Calendário interativo com visualização mensal
- Controle de presença: pendente, concluído, faltou
- Registro de extras e observações por banho
- Relatórios mensais com receita prevista, recebida e pendente
- Taxa de recebimento e listagem de pacotes em aberto

---

## Pré-requisitos

- **Python** 3.10+
- **Node.js** 18+
- **Docker** e Docker Compose (opcional, para produção)

---

## Como Executar

### Opção 1: Windows — Start com 1 Clique

Execute o arquivo `start.bat` na raiz do projeto:

```batch
.\start.bat
```

O que o script faz:
1. Cria virtual environment Python (se não existir)
2. Instala dependências do backend
3. Inicia o backend FastAPI em `http://localhost:8000`
4. Instala dependências do frontend (se necessário)
5. Inicia o frontend Vue em `http://localhost:5173`

Acesse:
- **Aplicação:** http://localhost:5173
- **Documentação da API:** http://localhost:8000/docs

---

### Opção 2: Manual (qualquer SO)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (em outro terminal):**
```bash
cd frontend
npm install
npm run dev
```

---

### Opção 3: Docker (Produção)

```bash
# Configure as variáveis de ambiente no arquivo .env
docker-compose up -d
```

Serviços levantados:
- PostgreSQL na porta 5432
- Backend FastAPI na porta 8000
- Frontend Nginx na porta 80

---

## Configuração

Crie um arquivo `backend/.env` com as seguintes variáveis:

### Desenvolvimento (SQLite)
```env
DATABASE_URL=sqlite:///./banho_tosa.db
DEBUG=True
```

### Produção (PostgreSQL via Docker)
```env
DATABASE_URL=postgresql://postgres:senha@postgres_local:5432/pacotesbanho
DEBUG=False
```

**Variáveis do Docker Compose:**
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha
POSTGRES_DB=pacotesbanho
BACKEND_PORT=8000
```

---

## Estrutura do Projeto

```
PacotesBanho/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py          # Ponto de entrada
│   │   ├── database.py      # Configuração SQLAlchemy
│   │   ├── models/          # Modelos ORM
│   │   ├── routers/         # Endpoints da API
│   │   ├── schemas/         # Validação Pydantic
│   │   └── services/        # Regras de negócio
│   ├── alembic/             # Migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Aplicação Vue 3
│   ├── src/
│   │   ├── views/           # Páginas (Dashboard, Pacotes, Clientes, Relatórios)
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── stores/          # Estado Pinia
│   │   ├── api/             # Cliente HTTP
│   │   └── router/          # Rotas Vue Router
│   ├── package.json
│   └── Dockerfile
├── test/                    # Testes de integração
├── docker-compose.yml
├── start.bat                # Start 1-clique (Windows)
└── README.md
```

---

## API — Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/clientes/` | Listar clientes |
| `POST` | `/api/v1/clientes/` | Criar cliente |
| `GET` | `/api/v1/cachorros/` | Listar cachorros |
| `POST` | `/api/v1/cachorros/` | Criar cachorro |
| `GET` | `/api/v1/pacotes/` | Listar pacotes |
| `POST` | `/api/v1/pacotes/` | Criar pacote (gera agendamentos) |
| `POST` | `/api/v1/pacotes/{id}/pagar` | Registrar pagamento |
| `GET` | `/api/v1/agendamentos/` | Listar agendamentos |
| `PUT` | `/api/v1/agendamentos/{id}` | Atualizar status de presença |
| `GET` | `/api/v1/agendamentos/dashboard/{data}` | Dashboard do dia |
| `GET` | `/api/v1/relatorios/mensal` | Relatório mensal |
| `GET` | `/health` | Health check |

Documentação interativa: http://localhost:8000/docs

---

## Testes

O projeto inclui testes de integração automatizados:

```bash
cd test
python run_integration.tests.py
```

Cenários testados:
- Cadastro de cliente válido e inválido
- Criação de pacote com geração automática de agendamentos
- Registro de pagamento
- Visualização de banhos no calendário
- Edição de status de presença

Para executar com pytest:
```bash
cd backend
pytest
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Porta 8000 ocupada | `taskkill /F /IM uvicorn.exe` (Windows) ou `killall uvicorn` (Linux/Mac) |
| Backend não inicia | Verifique se `pip install -r backend/requirements.txt` foi executado |
| Frontend não conecta à API | Certifique-se de que o backend está rodando antes do frontend |
| Erro de CORS | Verifique se o backend está em `localhost:8000` e o frontend em `localhost:5173` |
| Banco não conecta (Docker) | Aguarde o healthcheck do PostgreSQL (`docker-compose logs -f postgres_local`) |
| `node_modules` ausente | Execute `npm install` dentro da pasta `frontend/` |

---

## Autor

Desenvolvido para gestão do **Canil Recanto Mini Dogs**.

