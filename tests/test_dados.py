"""
Registro de jogadas (classe Dados).

Caso de teste: CT41.
Requisito: RF18 (ao fim de cada mão as jogadas são registradas em jogadas.csv)
e o formato da base de casos usada pela IA (RF17).
"""
import pandas as pd
import pytest

from truco.dados import Dados

pytestmark = pytest.mark.lento


@pytest.fixture
def dados():
    return Dados()   # o conftest faz o jogo rodar numa pasta temporária


@pytest.mark.requisito("CT41")
def test_CT41_primeira_rodada_grava_a_mao_do_bot(dados, bot_com_mao, nova_carta):
    bot = bot_com_mao("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
    dados.primeira_rodada(list(bot.pontuacao_cartas), list(bot.mao_rank), bot.qualidade_mao,
                          nova_carta("7 de COPAS"))
    registro = dados.retornar_registro().iloc[0]
    assert (registro.cartaAltaRobo, registro.cartaMediaRobo, registro.cartaBaixaRobo) == (52, 24, 1)
    assert registro.jogadorMao == 1
    assert registro.naipePrimeiraCartaHumano == 4                # COPAS
    assert list(dados.retornar_registro().columns) == list(dados.retornar_casos().columns)


@pytest.mark.requisito("CT41")
def test_CT41_cada_mao_vira_uma_linha_em_jogadas_csv(dados, tmp_path):
    for _ in range(3):
        dados.finalizar_partida()
    arquivo = pd.read_csv(tmp_path / "jogadas.csv")
    assert len(arquivo) == 3                                     # um cabeçalho e uma linha por mão
    assert "cartaAltaRobo" in arquivo.columns
