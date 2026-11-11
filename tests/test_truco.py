"""Pedidos, respostas e pontuação de Truco (CT18 a CT23; D04)."""
import pytest

from truco.truco import Truco

HUMANO, BOT = 1, 2
MAO_HUMANO = ("3 de COPAS", "2 de OUROS", "4 de BASTOS")
MAO_BOT = ("1 de ESPADAS", "7 de OUROS", "5 de COPAS")


@pytest.fixture
def jogadores(jogador_com_mao, bot_com_mao):
    def _criar():
        return jogador_com_mao(*MAO_HUMANO, nome="Renato"), bot_com_mao(*MAO_BOT, nome="Lucas")
    return _criar


# Confere o retorno de aceitação quando o humano pede Truco e o bot aceita.
@pytest.mark.requisito("CT18")
@pytest.mark.requisito("CT23")
def test_CT18_humano_pede_truco_e_o_bot_aceita(jogadores, cbr_falsa):
    humano, bot = jogadores()
    truco, ia = Truco(), cbr_falsa(truco=1)
    assert truco.retornar_valor_aposta() == 1
    assert truco.controlador_truco(ia, None, HUMANO, humano, bot) is True
    assert truco.estado_atual == "truco"
    assert ia.chamadas == [("truco", "truco", HUMANO, bot.qualidade_mao)]


# Verifica se o Truco aceito aumenta o valor da mão para dois pontos.
@pytest.mark.requisito("CT18")
@pytest.mark.defeito("D04")
@pytest.mark.xfail(reason="D04: truco aceito não atualiza o valor da mão (continua 1)")
def test_D04_truco_aceito_vale_2_pontos(jogadores, cbr_falsa):
    humano, bot = jogadores()
    truco = Truco()
    truco.controlador_truco(cbr_falsa(truco=1), None, HUMANO, humano, bot)
    assert truco.retornar_valor_aposta() == 2


# Confere os valores de três pontos para Retruco e quatro para Vale 4.
@pytest.mark.requisito("CT19")
def test_CT19_retruco_vale_3_e_vale_4_vale_4(jogadores, cbr_falsa, entradas_usuario):
    humano, bot = jogadores()
    truco = Truco()
    entradas_usuario("1")                     # humano aceita o retruco do bot
    truco.controlador_truco(cbr_falsa(truco=2), None, HUMANO, humano, bot)
    assert truco.retornar_valor_aposta() == 3

    humano, bot = jogadores()
    truco = Truco()
    entradas_usuario("2")                     # humano aumenta para vale 4; o bot aceita
    truco.controlador_truco(cbr_falsa(truco=[2, 1]), None, HUMANO, humano, bot)
    assert truco.retornar_valor_aposta() == 4


# Verifica se a recusa concede a quem pediu o valor anterior da aposta.
@pytest.mark.requisito("CT20")
def test_CT20_recusa_entrega_o_valor_anterior_a_quem_pediu(jogadores, cbr_falsa, entradas_usuario):
    # truco recusado pelo bot: humano +1
    humano, bot = jogadores()
    assert Truco().controlador_truco(cbr_falsa(truco=0), None, HUMANO, humano, bot) is False
    assert (humano.pontos, bot.pontos) == (1, 0)
    # retruco do bot recusado pelo humano: bot +2
    humano, bot = jogadores()
    entradas_usuario("0")
    Truco().controlador_truco(cbr_falsa(truco=2), None, HUMANO, humano, bot)
    assert (humano.pontos, bot.pontos) == (0, 2)
    # vale 4 do humano recusado pelo bot: humano +3
    humano, bot = jogadores()
    entradas_usuario("2")
    Truco().controlador_truco(cbr_falsa(truco=[2, 0]), None, HUMANO, humano, bot)
    assert (humano.pontos, bot.pontos) == (3, 0)


# Confere o bloqueio de dois aumentos seguidos pelo mesmo jogador.
@pytest.mark.requisito("CT21")
def test_CT21_mesmo_jogador_nao_aumenta_duas_vezes_seguidas(jogadores, cbr_falsa):
    humano, bot = jogadores()
    truco = Truco()
    truco.controlador_truco(cbr_falsa(truco=1), None, HUMANO, humano, bot)
    ia = cbr_falsa(truco=1)
    assert truco.controlador_truco(ia, None, HUMANO, humano, bot) is None
    assert ia.chamadas == []


# Verifica se uma resposta inválida ao Truco faz a pergunta se repetir.
@pytest.mark.requisito("CT22")
@pytest.mark.entrada
def test_CT22_humano_responde_truco_do_bot_com_opcao_invalida(jogadores, cbr_falsa, entradas_usuario):
    humano, bot = jogadores()
    registro = entradas_usuario("3", "9", "1")
    assert Truco().controlador_truco(cbr_falsa(), None, BOT, humano, bot) is True
    assert len(registro.perguntas) == 3
    for opcao in ("[0] Recusar", "[1] Aceitar", "[2] Aumentar Aposta"):
        assert opcao in registro.perguntas[0]
