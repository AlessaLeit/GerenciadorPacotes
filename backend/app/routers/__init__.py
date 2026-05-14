"""
Routers FastAPI - Endpoints da API REST.
"""
from fastapi import APIRouter
from .clientes import router as clientes_router
from .cachorros import router as cachorros_router
from .pacotes import router as pacotes_router
from .banhos import router as banhos_router
from .relatorios import router as relatorios_router
from .agendamentos import router as agendamentos_router
from .auth import router as auth_router

# Router principal que agrega todos os sub-routers
api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(clientes_router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(cachorros_router, prefix="/cachorros", tags=["Cachorros"])
api_router.include_router(pacotes_router, prefix="/pacotes", tags=["Pacotes"])
api_router.include_router(banhos_router, prefix="/banhos", tags=["Banhos"])
api_router.include_router(relatorios_router, prefix="/relatorios", tags=["Relatórios"])
api_router.include_router(agendamentos_router, prefix="/agendamentos", tags=["Agendamentos"])

__all__ = ["api_router"]