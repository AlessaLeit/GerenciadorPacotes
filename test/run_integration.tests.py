import os
import sys
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório atual ao sys.path para importar app
sys.path.append(os.getcwd())

from app.main import app
from app.database import Base, get_db
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

def run_tests():
    print("Iniciando execução dos testes para PacotesBanho...\n")
    
    # Cria as tabelas
    Base.metadata.create_all(bind=engine)
    
    results = []

    def log_result(id, cenario, status, msg=""):
        print(f"[{status}] {id}: {cenario} {msg}")
        results.append({"id": id, "cenario": cenario, "status": status, "msg": msg})

    try:
        # CT01
        resp = client.post("/api/v1/clientes/", json={"nome": "João Silva", "telefone": "11999999999"})
        if resp.status_code == 201:
            log_result("CT01", "Cadastro de Cliente Válido", "PASSOU")
        else:
            log_result("CT01", "Cadastro de Cliente Válido", "FALHOU", f"Status: {resp.status_code}")

        # CT02
        resp = client.post("/api/v1/clientes/", json={"telefone": "11999999999"})
        if resp.status_code == 422:
            log_result("CT02", "Cadastro de Cliente sem Nome", "PASSOU")
        else:
            log_result("CT02", "Cadastro de Cliente sem Nome", "FALHOU", f"Status: {resp.status_code}")

        # CT03
        cli_id = client.post("/api/v1/clientes/", json={"nome": "Maria"}).json()["id"]
        dog_id = client.post("/api/v1/cachorros/", json={"nome": "Rex", "porte": "grande", "cliente_id": cli_id}).json()["id"]
        pac_resp = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "semanal", "valor_cobrado": 50.0})
        if pac_resp.status_code == 201:
            pac_id = pac_resp.json()["id"]
            ag_resp = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}")
            if len(ag_resp.json()) > 0:
                log_result("CT03", "Criação de Pacote com Geração de Agendamentos", "PASSOU", f"({len(ag_resp.json())} agendamentos gerados)")
            else:
                log_result("CT03", "Criação de Pacote com Geração de Agendamentos", "FALHOU", "Nenhum agendamento gerado")
        else:
            log_result("CT03", "Criação de Pacote com Geração de Agendamentos", "FALHOU", f"Status: {pac_resp.status_code}")

        # CT04
        cli_id = client.post("/api/v1/clientes/", json={"nome": "Pedro"}).json()["id"]
        dog_id = client.post("/api/v1/cachorros/", json={"nome": "Bob", "porte": "medio", "cliente_id": cli_id}).json()["id"]
        pac_id = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "mensal", "valor_cobrado": 80.0}).json()["id"]
        client.post(f"/api/v1/pacotes/{pac_id}/pagar")
        check_resp = client.get(f"/api/v1/pacotes/{pac_id}")
        if check_resp.json()["status_pagamento"] == "pago":
            log_result("CT04", "Registro de Pagamento de Pacote", "PASSOU")
        else:
            log_result("CT04", "Registro de Pagamento de Pacote", "FALHOU")

        # CT05
        cli_id = client.post("/api/v1/clientes/", json={"nome": "Ana"}).json()["id"]
        dog_id = client.post("/api/v1/cachorros/", json={"nome": "Mel", "porte": "pequeno", "cliente_id": cli_id}).json()["id"]
        pac_id = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "mensal", "valor_cobrado": 60.0}).json()["id"]
        hoje = date.today().isoformat()
        dash_resp = client.get(f"/api/v1/agendamentos/dashboard/{hoje}")
        if any(item["pet_nome"] == "Mel" for item in dash_resp.json()):
            log_result("CT05", "Visualização de Banhos no Calendário", "PASSOU")
        else:
            log_result("CT05", "Visualização de Banhos no Calendário", "FALHOU")

        # CT06
        cli_id = client.post("/api/v1/clientes/", json={"nome": "Bia"}).json()["id"]
        dog_id = client.post("/api/v1/cachorros/", json={"nome": "Luna", "porte": "pequeno", "cliente_id": cli_id}).json()["id"]
        pac_id = client.post("/api/v1/pacotes/", json={"cachorro_id": dog_id, "tipo_plano": "mensal", "valor_cobrado": 60.0}).json()["id"]
        ag_id = client.get(f"/api/v1/agendamentos/?pacote_id={pac_id}").json()[0]["id"]
        up_resp = client.put(f"/api/v1/agendamentos/{ag_id}", json={"status_presenca": "concluido"})
        if up_resp.json()["status_presenca"] == "concluido":
            log_result("CT06", "Edição de Status de Presença", "PASSOU")
        else:
            log_result("CT06", "Edição de Status de Presença", "FALHOU")

    except Exception as e:
        print(f"\nErro durante a execução: {e}")
    
    print("\n--- RESUMO FINAL ---")
    passou = len([r for r in results if r["status"] == "PASSOU"])
    print(f"Total: {len(results)} | Passou: {passou} | Falhou: {len(results) - passou}")

if __name__ == "__main__":
    run_tests()
