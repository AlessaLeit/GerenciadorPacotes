import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.auth import get_current_user
# Importar modelos explicitamente para garantir registro no Base.metadata
from app.models import Cliente, Cachorro, Pacote, Agendamento, Banho

# Configuração do banco de dados de teste (em memória)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"id": 1, "username": "admin"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
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
    """CT01: Cadastro de Cliente Válido (Positivo)
    Tentar cadastrar um cliente fornecendo apenas o campo obrigatório nome.
    O cliente deve ser salvo no banco de dados com sucesso e um ID único deve ser gerado.
    """
    # Act
    response = client.post("/api/v1/clientes/", json={"nome": "João Silva"})
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert "id" in data
    cliente_id = data["id"]
    assert isinstance(cliente_id, int) and cliente_id > 0

    # Assert (Persistence check)
    get_resp = client.get(f"/api/v1/clientes/{cliente_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["nome"] == "João Silva"


@pytest.mark.parametrize("payload", [
    {"telefone": "11999999999"},          # campo nome ausente
    {"nome": "", "telefone": "11999999999"},  # campo nome vazio
])
def test_ct02_cadastro_cliente_sem_nome(payload):
    """CT02: Cadastro de Cliente sem Nome (Negativo)
    Tentar cadastrar um cliente enviando o campo nome vazio ou nulo.
    O sistema deve retornar um erro de validação (422 Unprocessable Entity)
    informando que o nome é obrigatório.
    """
    # Act
    response = client.post("/api/v1/clientes/", json=payload)
    
    # Assert
    assert response.status_code == 422
    detail = response.json().get("detail", [])
    # Verifica se há alguma mensagem de erro relacionada ao campo 'nome'
    assert any("nome" in str(err).lower() for err in detail), (
        f"Esperava erro de validação para o campo 'nome', mas recebeu: {detail}"
    )

# --- FUNCIONALIDADE 2: Controle de Pacotes ---

def test_ct03_criacao_pacote_com_agendamentos():
    """CT03: Criação de Pacote com Geração de Agendamentos (Positivo)"""
    # Arrange
    cli_resp = client.post("/api/v1/clientes/", json={"nome": "Maria"})
    cli_id = cli_resp.json()["id"]
    dog_resp = client.post("/api/v1/cachorros/", json={"nome": "Rex", "porte": "grande", "cliente_id": cli_id})
    dog_id = dog_resp.json()["id"]
    
    # Act
    pac_resp = client.post("/api/v1/pacotes/", json={
        "cachorro_id": dog_id, 
        "tipo_plano": "semanal", 
        "valor_cobrado": 50.0,
        "dia_da_semana": "terca",
        "valor_banho_base": 12.5
    })
    
    # Assert
    assert pac_resp.status_code == 201
    pac_id = pac_resp.json()["id"]
    ag_resp = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}")
    assert ag_resp.status_code == 200
    assert len(ag_resp.json()) > 0

def test_ct04_registro_pagamento_pacote():
    """CT04: Registro de Pagamento de Pacote (Positivo)"""
    # Arrange
    cli_id = client.post("/api/v1/clientes/", json={"nome": "Pedro"}).json()["id"]
    dog_id = client.post("/api/v1/cachorros/", json={"nome": "Bob", "porte": "medio", "cliente_id": cli_id}).json()["id"]
    pac_id = client.post("/api/v1/pacotes/", json={
        "cachorro_id": dog_id, 
        "tipo_plano": "mensal", 
        "valor_cobrado": 80.0,
        "dia_da_semana": "quarta",
        "valor_banho_base": 80.0
    }).json()["id"]
    
    # Act
    # Nota: O backend espera PATCH e query params conforme definido em pacotes.py
    pay_resp = client.patch(f"/api/v1/pacotes/{pac_id}/pagar?valor_pago=80.0&data_pagamento=2024-05-20")
    
    # Assert
    assert pay_resp.status_code == 200
    check_resp = client.get(f"/api/v1/pacotes/{pac_id}")
    assert check_resp.json()["status_pagamento"] == "pago"

# --- FUNCIONALIDADE 3: Agenda Dinâmica ---

def test_ct05_visualizacao_banhos_dashboard():
    """CT05: Visualização de Banhos no Calendário (Positivo)"""
    # Arrange
    cli_id = client.post("/api/v1/clientes/", json={"nome": "Ana"}).json()["id"]
    dog_id = client.post("/api/v1/cachorros/", json={"nome": "Mel", "porte": "pequeno", "cliente_id": cli_id}).json()["id"]
    pac_id = client.post("/api/v1/pacotes/", json={
        "cachorro_id": dog_id, 
        "tipo_plano": "mensal", 
        "valor_cobrado": 60.0,
        "dia_da_semana": "sexta",
        "valor_banho_base": 60.0
    }).json()["id"]
    
    # Obtém a data real de um dos agendamentos gerados para o teste ser determinístico
    ags = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}").json()
    assert len(ags) > 0, "Nenhum agendamento foi gerado automaticamente"
    data_agendada = ags[0]["data_banho"]
    
    # Act
    dash_resp = client.get(f"/api/v1/agendamentos/dashboard/{data_agendada}")
    
    # Assert
    assert dash_resp.status_code == 200
    assert any(item["pet_nome"] == "Mel" for item in dash_resp.json())

def test_ct06_edicao_status_presenca():
    """CT06: Edição de Status de Presença (Positivo)"""
    # Arrange
    cli_id = client.post("/api/v1/clientes/", json={"nome": "Bia"}).json()["id"]
    dog_id = client.post("/api/v1/cachorros/", json={"nome": "Luna", "porte": "pequeno", "cliente_id": cli_id}).json()["id"]
    pac_id = client.post("/api/v1/pacotes/", json={
        "cachorro_id": dog_id, 
        "tipo_plano": "mensal", 
        "valor_cobrado": 60.0,
        "dia_da_semana": "sabado",
        "valor_banho_base": 60.0
    }).json()["id"]
    ag_id = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}").json()[0]["id"]
    
    # Act
    up_resp = client.put(f"/api/v1/agendamentos/{ag_id}", json={"status_presenca": "concluido"})
    
    # Assert
    assert up_resp.status_code == 200
    assert up_resp.json()["status_presenca"] == "concluido"
