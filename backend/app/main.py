"""
Ponto de entrada da aplicação FastAPI.
Configura CORS, lifespan e registra todos os routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import api_router
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciamento do ciclo de vida da aplicação.
    Cria tabelas na inicialização (em dev; em prod use Alembic).
    """
    try:
        # Startup: cria tabelas se não existirem
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao conectar no banco de dados: {e}")
        # Em Docker, é melhor deixar o container crashar para o restart policy atuar
    
    yield
    # Shutdown: cleanup se necessário


# Instância principal do FastAPI
app = FastAPI(
    title="Banho & Tosa API",
    description="API para gerenciamento de pacotes de banho e tosa para pets",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração CORS para permitir requisições do frontend Vue (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Vite dev server (IP)
        "http://localhost:3000",  # Alternativa comum
        "http://localhost",       # Nginx frontend container
        "http://127.0.0.1",       # Localhost alternativo
        "http://frontend",        # Nome do serviço no Docker
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra todos os routers da API
app.include_router(auth.router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """Endpoint de health check."""
    return {
        "message": "Banho & Tosa API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check para monitoramento."""
    return {"status": "healthy"}