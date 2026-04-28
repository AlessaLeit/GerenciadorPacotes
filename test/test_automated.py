import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
# Importar modelos explicitamente para garantir registro no Base.metadata
from app.models import Cliente, Cachorro, Pacote, Agendamento, Banho

# Configuração do banco de dados de teste (em memória)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Cria as tabelas antes de cada teste no engine de teste
    Base.metadata.create_all(bind=engine)
    yield
    # Remove as tabelas após cada teste
    Base.metadata.drop_all(bind=engine)

# --- FUNCIONALIDADE 1: Gestão de Clientes ---

def test_ct01_cadastro_cliente_valido():
    """CT01: Cadastro de Cliente Válido (Positivo)"""
    response = client.post("/api/v1/clientes/", json={"nome": "João Silva", "telefone": "11999999999"})
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert "id" in data

def test_ct02_cadastro_cliente_sem_nome():
    """CT02: Cadastro de Cliente sem Nome (Negativo)"""
    response = client.post("/api/v1/clientes/", json={"telefone": "11999999999"})
    assert response.status_code == 422

# --- FUNCIONALIDADE 2: Controle de Pacotes ---

def test_ct03_criacao_pacote_com_agendamentos():
    """CT03: Criação de Pacote com Geração de Agendamentos (Positivo)"""
    cli_resp = client.post("/api/v1/clientes/", json={"nome": "Maria"})
    cli_id = cli_resp.json()["id"]
    dog_resp = client.post("/api/v1/cachorros/", json={"nome": "Rex", "porte": "grande", "cliente_id": cli_id})
    dog_id = dog_resp.json()["id"]
    pac_resp = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "semanal", "valor_cobrado": 50.0})
    assert pac_resp.status_code == 201
    pac_id = pac_resp.json()["id"]
    ag_resp = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}")
    assert ag_resp.status_code == 200
    assert len(ag_resp.json()) > 0

def test_ct04_registro_pagamento_pacote():
    """CT04: Registro de Pagamento de Pacote (Positivo)"""
    cli_id = client.post("/api/v1/clientes/", json={"nome": "Pedro"}).json()["id"]
    dog_id = client.post("/api/v1/cachorros/", json={"nome": "Bob", "porte": "medio", "cliente_id": cli_id}).json()["id"]
    pac_id = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "mensal", "valor_cobrado": 80.0}).json()["id"]
    pay_resp = client.post(f"/api/v1/pacotes/{pac_id}/pagar")
    assert pay_resp.status_code == 200
    check_resp = client.get(f"/api/v1/pacotes/{pac_id}")
    assert check_resp.json()["status_pagamento"] == "pago"

# --- FUNCIONALIDADE 3: Agenda Dinâmica ---

def test_ct05_visualizacao_banhos_dashboard():
    """CT05: Visualização de Banhos no Calendário (Positivo)"""
    cli_id = client.post("/api/v1/clientes/", json={"nome": "Ana"}).json()["id"]
    dog_id = client.post("/api/v1/cachorros/", json={"nome": "Mel", "porte": "pequeno", "cliente_id": cli_id}).json()["id"]
    pac_id = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "mensal", "valor_cobrado": 60.0}).json()["id"]
    from datetime import date
    hoje = date.today().isoformat()
    dash_resp = client.get(f"/api/v1/agendamentos/dashboard/{hoje}")
    assert dash_resp.status_code == 200
    assert any(item["pet_nome"] == "Mel" for item in dash_resp.json())

def test_ct06_edicao_status_presenca():
    """CT06: Edição de Status de Presença (Positivo)"""
    cli_id = client.post("/api/v1/clientes/", json={"nome": "Bia"}).json()["id"]
    dog_id = client.post("/api/v1/cachorros/", json={"nome": "Luna", "porte": "pequeno", "cliente_id": cli_id}).json()["id"]
    pac_id = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "mensal", "valor_cobrado": 60.0}).json()["id"]
    ag_id = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}").json()[0]["id"]
    up_resp = client.put(f"/api/v1/agendamentos/{ag_id}", json={"status_presenca": "concluido"})
    assert up_resp.status_code == 200
    assert up_resp.json()["status_presenca"] == "concluido"
