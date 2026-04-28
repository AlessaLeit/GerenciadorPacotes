"""
Ponto de entrada da aplicação FastAPI.
Configura CORS, lifespan e registra todos os routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciamento do ciclo de vida da aplicação.
    Cria tabelas na inicialização (em dev; em prod use Alembic).
    """
    # Startup: cria tabelas se não existirem
    Base.metadata.create_all(bind=engine)
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