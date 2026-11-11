"""
Etapa 1 - Testes de fumaça (smoke tests) do ambiente.

Garantem que a infraestrutura de testes funciona antes de escrever os testes
de verdade: imports, fixtures, simulação de teclado, IA e partida completa.
"""
import importlib

import pandas as pd
import pytest

from conftest import ARQUIVO_BASE_CASOS, EntradasEsgotadas

MODULOS = ["baralho", "bot", "carta", "cbr", "dados", "envido", "flor",
           "interface", "jogador", "jogo", "pontos", "truco"]


@pytest.mark.parametrize("modulo", MODULOS)
def test_todos_os_modulos_do_pacote_importam(modulo):
    assert importlib.import_module(f"truco.{modulo}") is not None


def test_arquivos_de_dados_existem():
    assert ARQUIVO_BASE_CASOS.exists()
    assert (ARQUIVO_BASE_CASOS.parent / "modelo_registro.csv").exists()


def test_fabricas_de_carta_e_mao(nova_carta, nova_mao):
    carta = nova_carta("7 de OUROS")
    assert (carta.numero, carta.naipe) == (7, "OUROS")
    assert [c.retornar_carta() for c in nova_mao("1 de ESPADAS", "3 de COPAS")] == [
        "1 de ESPADAS", "3 de COPAS"]


def test_baralho_fixo_entrega_cartas_na_ordem(baralho_fixo):
    baralho = baralho_fixo(["1 de ESPADAS", "2 de COPAS", "3 de OUROS"])
    assert [baralho.retirar_carta().retornar_carta() for _ in range(3)] == [
        "1 de ESPADAS", "2 de COPAS", "3 de OUROS"]


def test_bot_com_mao_fixa_calcula_atributos(bot_com_mao):
    bot = bot_com_mao("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
    assert len(bot.mao) == 3
    assert sorted(bot.mao_rank) == ["Alta", "Baixa", "Media"]
    assert bot.qualidade_mao > 0


def test_simulacao_de_teclado(entradas_usuario):
    registro = entradas_usuario("Renato", 3)
    assert input("Nome? ") == "Renato"
    assert input("Carta? ") == "3"
    assert registro.perguntas == ["Nome? ", "Carta? "]
    with pytest.raises(EntradasEsgotadas):
        input("Mais uma? ")


def test_cbr_falsa_registra_chamadas(cbr_falsa):
    ia = cbr_falsa(truco=[2, 0])
    assert ia.truco("truco", 1, 10) == 2
    assert ia.truco("truco", 1, 10) == 0
    assert len(ia.chamadas) == 2


@pytest.mark.lento
@pytest.mark.ia
def test_ia_real_carrega_base_de_casos(cbr_real):
    assert len(cbr_real.dataset) > 20000
    assert cbr_real.dataset.isna().sum().sum() == 0
    assert list(cbr_real.dados.retornar_registro().columns) == list(cbr_real.dataset.columns)


@pytest.mark.lento
@pytest.mark.cenario
def test_partida_inicia_e_distribui_cartas(executar_partida):
    partida = executar_partida("Renato", "Bot", seed=1)
    assert isinstance(partida.erro, EntradasEsgotadas)  # parou esperando a 1ª jogada
    assert partida.perguntas[:2] == ["Nome Jogador 1: ", "Nome Jogador 2 (Bot): "]
    assert len(partida.estado["jogador1"].mao) == 3
    assert len(partida.estado["jogador2"].mao) == 3


@pytest.mark.lento
@pytest.mark.cenario
def test_partida_com_maos_fixas(executar_partida):
    partida = executar_partida(
        "Renato", "Bot",
        maos=[(["1 de ESPADAS", "3 de COPAS", "4 de OUROS"],
               ["7 de OUROS", "2 de BASTOS", "5 de COPAS"])])
    assert [c.retornar_carta() for c in partida.estado["jogador1"].mao] == [
        "1 de ESPADAS", "3 de COPAS", "4 de OUROS"]
    assert [c.retornar_carta() for c in partida.estado["jogador2"].mao] == [
        "7 de OUROS", "2 de BASTOS", "5 de COPAS"]


@pytest.mark.defeito("D01")
@pytest.mark.sem_adaptador
@pytest.mark.xfail(raises=ValueError, reason="D01: base de casos separada por TAB, lida como CSV de vírgula")
def test_D01_jogo_carrega_base_de_casos_sem_adaptador():
    """Como o usuário roda o jogo (python -m truco): a base de casos deveria carregar."""
    assert pd.read_csv.__module__.startswith("pandas")  # pandas original, sem adaptador
    from truco.dados import Dados
    Dados()
