"""
Configuração do banco de dados usando SQLAlchemy 2.x.
Suporta SQLite (desenvolvimento) e PostgreSQL (produção) via variável de ambiente.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Generator
import os


class Settings(BaseSettings):
    """Configurações da aplicação lidas do .env"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignora variáveis extras (ex: do Postgres) sem crashar
    )

    DATABASE_URL: str = "sqlite:///./banho_tosa.db"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    ADMIN_USER: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"


# Instância global das configurações
settings = Settings()

_database_url = settings.DATABASE_URL

# Melhora a detecção de ambiente: Se não estivermos no Docker (onde a variável 
# DOCKER_CONTAINER costuma ser setada ou o host do banco não resolve), 
# e a URL apontar para um host de container, podemos forçar SQLite.
if os.getenv("DATABASE_URL") is None and not os.path.exists("/.dockerenv"):
    _database_url = "sqlite:///./banho_tosa.db"

# Criação do engine com configurações específicas para SQLite/PostgreSQL
if _database_url.startswith("sqlite"):
    # SQLite requer check_same_thread=False para uso com FastAPI
    engine = create_engine(
        _database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    # PostgreSQL ou outros bancos de produção
    engine = create_engine(
        _database_url,
        pool_pre_ping=True,
        echo=settings.DEBUG
    )

# Base declarativa para os modelos - ESSENCIAL!
class Base(DeclarativeBase):
    pass

# Factory de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Dependency do FastAPI para injeção de sessão do banco.
    Garante fechamento da sessão após cada requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()