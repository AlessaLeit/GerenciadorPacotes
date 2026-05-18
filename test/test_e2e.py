import re
import pytest
from playwright.sync_api import Page, expect

"""
(Não configurado)
Instruções de execução:
1. Certifique-se de que o sistema está rodando (Backend na 8000 e Frontend na 80).
2. Execute: pytest test/test_e2e.py --headed (para ver o navegador abrindo)
"""

BASE_URL = "http://localhost:80"

def realizar_login(page: Page):
    page.goto(f"{BASE_URL}/login")
    # Usando exact=False para ser mais flexível com o texto do label
    page.get_by_label("E-mail", exact=False).fill("email@teste.com")
    page.get_by_label("Senha", exact=False).fill("teste")
    page.get_by_role("button", name="Entrar").click()
    # Espera o redirecionamento para o dashboard
    page.wait_for_url(re.compile(r"/dashboard|/"))
    page.wait_for_load_state("networkidle")

def test_fluxo_completo_novo_cliente_pet_pacote(page: Page):
    # 1. Login Automático
    realizar_login(page)
    
    # Espera até que o título ou algum elemento principal da home apareça
    page.wait_for_load_state("domcontentloaded")
    expect(page).to_have_title(re.compile(r"Banho.*Tosa", re.IGNORECASE))

    # 2. Navegar para Clientes e Criar um Novo
    # Nota: Assumindo que existe um link 'Clientes' no menu lateral/navegação
    page.get_by_role("link", name="Clientes").click()
    page.get_by_role("button", name="+ Novo Cliente").click()
    
    nome_cliente = "Augusto Playwright"
    page.get_by_label("Nome", exact=False).fill(nome_cliente)
    page.get_by_label("Telefone", exact=False).fill("11999998888")
    page.get_by_role("button", name="Salvar").click()

    # Verifica se o cliente foi listado
    expect(page.get_by_text(nome_cliente)).to_be_visible()

    # 3. Adicionar um Pet para este cliente
    # Clica no botão '+ Pet' dentro do card do cliente recém criado
    page.get_by_role("button", name="+ Pet").first.click()
    
    nome_pet = "Spyke E2E"
    page.get_by_label("Nome", exact=False).fill(nome_pet)
    page.get_by_label("Raça", exact=False).fill("Beagle")
    page.get_by_label("Porte", exact=False).select_option("medio")
    page.get_by_role("button", name="Salvar").click()

    # Verifica se o pet aparece no card do cliente
    expect(page.get_by_text(nome_pet)).to_be_visible()

    # 4. Criar um Pacote para o Pet
    page.get_by_role("button", name="📦 Pacotes").first.click()
    page.get_by_role("button", name="+ Novo Pacote").click()
    
    # O pet deve estar pré-selecionado na tela de pacotes vindo de clientes
    page.get_by_label("Plano", exact=False).select_option("semanal")
    page.get_by_label("Dia", exact=False).select_option("sexta")
    page.get_by_role("spinbutton").first.fill("60") # Seleciona pelo tipo de input caso o label falhe
    
    # Clica em criar e aguarda o fechamento do modal/redirecionamento
    page.get_by_role("button", name="Criar Pacote").click()
    
    # 5. Validar no Dashboard
    page.get_by_role("link", name="Dashboard").click()
    
    # Verifica se o pet aparece na lista de agendamentos (se for o dia correto)
    # ou se as estatísticas foram atualizadas
    expect(page.get_by_text("Pacotes Ativos")).to_be_visible()

def test_dashboard_stats_loading(page: Page):
    """Verifica se os cards de estatísticas carregam corretamente"""
    page.goto(BASE_URL)
    
    # Verifica se os elementos principais de resumo estão na tela
    expect(page.get_by_text("Receita Prevista")).to_be_visible()
    expect(page.get_by_text("Cachorros")).to_be_visible()
    
    # Verifica se o componente de calendário foi renderizado
    expect(page.locator(".calendario")).to_be_visible()