"""Registro de jogadas em CSV (CT41, RF18)."""
import pandas as pd
import pytest

from truco.dados import Dados

pytestmark = pytest.mark.lento


@pytest.fixture
def dados():
    return Dados()


# Confere o registro da mão do bot na primeira rodada.
@pytest.mark.requisito("CT41")
def test_CT41_primeira_rodada_grava_a_mao_do_bot(dados, bot_com_mao, nova_carta):
    bot = bot_com_mao("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
    dados.primeira_rodada(list(bot.pontuacao_cartas), list(bot.mao_rank), bot.qualidade_mao,
                          nova_carta("7 de COPAS"))
    registro = dados.retornar_registro().iloc[0]
    assert (registro.cartaAltaRobo, registro.cartaMediaRobo, registro.cartaBaixaRobo) == (52, 24, 1)
    assert registro.jogadorMao == 1
    assert registro.naipePrimeiraCartaHumano == 4
    assert list(dados.retornar_registro().columns) == list(dados.retornar_casos().columns)


# Verifica se cada mão acrescenta uma linha ao arquivo jogadas.csv.
@pytest.mark.requisito("CT41")
def test_CT41_cada_mao_vira_uma_linha_em_jogadas_csv(dados, tmp_path):
    for _ in range(3):
        dados.finalizar_partida()
    arquivo = pd.read_csv(tmp_path / "jogadas.csv")
    assert len(arquivo) == 3
    assert "cartaAltaRobo" in arquivo.columns


# Grava as três rodadas, as apostas e os vencedores; depois confere o reset do registro.
@pytest.mark.requisito("CT41")
def test_CT41_registro_das_rodadas_apostas_e_reset(dados, nova_carta):
    robo = nova_carta("7 de OUROS")
    dados.segunda_rodada(nova_carta("3 de ESPADAS"), robo, 1)
    dados.terceira_rodada(nova_carta("4 de BASTOS"), robo, 2)
    dados.finalizar_rodadas(nova_carta("6 de OUROS"), robo, 1)
    dados.cartas_jogadas_pelo_bot("primeira", robo)
    dados.envido(1, 0, 0, 1)
    dados.truco(1, 2, 1, 0, 2)
    dados.flor(1, 0, 0, 32)
    dados.vencedor_envido(1, 0)
    dados.vencedor_truco(2, 1)
    dados.vencedor_flor(1, 2)
    r = dados.retornar_registro().iloc[0]
    assert (r.ganhadorPrimeiraRodada, r.ganhadorSegundaRodada, r.ganhadorTerceiraRodada) == (1, 2, 1)
    assert (r.naipePrimeiraCartaHumano, r.naipeSegundaCartaHumano, r.naipeTerceiraCartaHumano) == (1, 3, 2)
    assert r.naipePrimeiraCartaRobo == 2
    assert (r.quemTruco, r.quemGanhouTruco, r.quemGanhouEnvido, r.pontosFlorRobo) == (1, 2, 1, 32)
    dados.resetar()
    assert (dados.retornar_registro().to_numpy() == 0).all()
