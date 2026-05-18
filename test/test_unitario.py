import pytest
from datetime import date, timedelta
import calendar

# Simulação da lógica interna de backend/app/routers/pacotes.py para teste unitário puro
# Em uma refatoração real, essa lógica deveria ser extraída para uma função de serviço.
def calcular_datas_agendamentos(tipo_plano: str, dia_semana_extenso: str, data_referencia: date):
    """
    Lógica de negócio extraída do router de pacotes para validação unitária.
    Gera as datas de banho baseadas no plano e dia da semana escolhido.
    """
    mapa_dow = {
        "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5,
    }
    
    alvo_dow = mapa_dow.get(dia_semana_extenso)
    if alvo_dow is None:
        return []

    primeiro_dia_mes = date(data_referencia.year, data_referencia.month, 1)
    ultimo_dia_mes = date(data_referencia.year, data_referencia.month, 
                          calendar.monthrange(data_referencia.year, data_referencia.month)[1])

    # Encontra a primeira ocorrência do dia da semana no mês
    primeira = None
    d = primeiro_dia_mes
    while d <= ultimo_dia_mes:
        if d.weekday() == alvo_dow:
            primeira = d
            break
        d += timedelta(days=1)

    if not primeira:
        return []

    datas = []
    if tipo_plano == "semanal":
        datas = [primeira + timedelta(days=7 * i) for i in range(4)]
    elif tipo_plano == "quinzenal":
        datas = [primeira + timedelta(days=15 * i) for i in range(2)]
    elif tipo_plano == "mensal":
        datas = [primeira]

    # Filtra apenas datas que pertencem ao mês de referência
    return [dt for dt in datas if primeiro_dia_mes <= dt <= ultimo_dia_mes]

def calcular_valor_total_pacote(valor_base: float, tipo_plano: str):
    """Valida a regra de cálculo de valor total (recalculado no frontend e gravado no backend)"""
    multiplicadores = {
        "semanal": 4,
        "quinzenal": 2,
        "mensal": 1
    }
    return valor_base * multiplicadores.get(tipo_plano, 0)

# --- TESTES UNITÁRIOS ---

def test_unit_geracao_datas_semanal():
    """Cenário: Plano Semanal na Terça-feira em Maio/2024 (Primeira terça é dia 07)"""
    ref = date(2024, 5, 1)
    datas = calcular_datas_agendamentos("semanal", "terca", ref)
    
    assert len(datas) == 4
    assert datas[0] == date(2024, 5, 7)
    assert datas[3] == date(2024, 5, 28)

def test_unit_geracao_datas_quinzenal():
    """Cenário: Plano Quinzenal na Quarta-feira (Intervalo de 15 dias)"""
    # 01/05/2024 é uma Quarta. Próxima: 16/05.
    ref = date(2024, 5, 1)
    datas = calcular_datas_agendamentos("quinzenal", "quarta", ref)
    
    assert len(datas) == 2
    assert datas[0] == date(2024, 5, 1)
    assert datas[1] == date(2024, 5, 16)

def test_unit_geracao_datas_mensal():
    """Cenário: Plano Mensal deve gerar exatamente 1 data no mês"""
    ref = date(2024, 6, 1) # Junho 2024
    datas = calcular_datas_agendamentos("mensal", "sabado", ref)
    
    assert len(datas) == 1
    assert datas[0] == date(2024, 6, 1) # Primeiro sábado de Junho/24

def test_unit_filtro_fim_do_mes():
    """Cenário: Garantir que banhos não transbordem para o próximo mês"""
    # Fevereiro 2024 (29 dias). 
    # Se a primeira terça é dia 06. 06 + 7*3 = 27 (ok). 
    # Se o plano fosse gerar 5 banhos, o 5º seria em Março e deve ser filtrado.
    ref = date(2024, 2, 1)
    datas = calcular_datas_agendamentos("semanal", "terca", ref)
    
    for d in datas:
        assert d.month == 2
        assert d.year == 2024

def test_unit_calculo_valor_total():
    """Cenário: Valida se a multiplicação do valor base pelo plano está correta"""
    assert calcular_valor_total_pacote(50.0, "semanal") == 200.0
    assert calcular_valor_total_pacote(60.0, "quinzenal") == 120.0
    assert calcular_valor_total_pacote(80.0, "mensal") == 80.0
    assert calcular_valor_total_pacote(50.0, "invalido") == 0.0