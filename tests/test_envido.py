"""Cálculo, pedidos e respostas de Envido (CT10 a CT17; D03)."""
import inspect

import pytest

from truco.bot import Bot
from truco.envido import Envido
from truco.jogador import Jogador

MAO_33 = ("7 de COPAS", "6 de COPAS", "1 de OUROS")
MAO_7 = ("7 de BASTOS", "6 de ESPADAS", "1 de COPAS")
ENVIDO, REAL_ENVIDO, FALTA_ENVIDO = 6, 7, 8
HUMANO, BOT = 1, 2


@pytest.fixture
def humano(jogador_com_mao):
    return jogador_com_mao(*MAO_33, nome="Renato")


@pytest.fixture
def bot(bot_com_mao):
    return bot_com_mao(*MAO_7, nome="Lucas")


def pedir(ia, tipo, quem_pediu, humano, bot, interface, envido=None):
    envido = envido or Envido()
    envido.controlador_envido(ia, None, tipo, quem_pediu, humano, bot, interface)
    return envido


# Confere o cálculo dos pontos de Envido para diferentes mãos.
@pytest.mark.requisito("CT10")
def test_CT10_calculo_dos_pontos_de_envido(nova_mao):
    casos = [
        (MAO_33, 33),
        (MAO_7, 7),
        (("5 de COPAS", "4 de COPAS", "7 de OUROS"), 29),      # par vence a carta maior
        (("1 de COPAS", "2 de COPAS", "3 de COPAS"), 25),      # flor: melhor par
        (("12 de COPAS", "11 de OUROS", "10 de BASTOS"), 0),
    ]
    for classe in (Jogador, Bot):
        for textos, pontos in casos:
            assert classe("Teste").calcula_envido(nova_mao(*textos)) == pontos, (classe.__name__, textos)


# Simula a recusa e a aceitação do pedido de Envido do bot.
@pytest.mark.requisito("CT11")
@pytest.mark.entrada
def test_CT11_humano_recusa_ou_aceita_o_envido_do_bot(jogador_com_mao, bot_com_mao, interface,
                                                      cbr_falsa, entradas_usuario):
    for resposta, pontos_esperados in (("0", (0, 1)), ("1", (2, 0))):
        humano, bot = jogador_com_mao(*MAO_33), bot_com_mao(*MAO_7)
        entradas_usuario(resposta)
        pedir(cbr_falsa(), ENVIDO, BOT, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == pontos_esperados, f"resposta {resposta}"


# Verifica se uma opção inválida faz a pergunta se repetir.
@pytest.mark.requisito("CT11")
@pytest.mark.entrada
def test_CT11_opcao_invalida_repete_a_pergunta(humano, bot, interface, cbr_falsa, entradas_usuario):
    registro = entradas_usuario("9", "-1", "1")
    pedir(cbr_falsa(), ENVIDO, BOT, humano, bot, interface)
    assert len(registro.perguntas) == 3
    assert all("aceita o pedido de envido" in p for p in registro.perguntas)
    assert humano.pontos == 2


# Simula o pedido de Envido do humano e confere a resposta do bot.
@pytest.mark.requisito("CT12")
def test_CT12_humano_pede_envido_e_o_bot_responde(jogador_com_mao, bot_com_mao, interface, cbr_falsa, capsys):
    humano, bot = jogador_com_mao(*MAO_33), bot_com_mao(*MAO_7)
    envido = pedir(cbr_falsa(envido=0), ENVIDO, HUMANO, humano, bot, interface)
    assert (humano.pontos, bot.pontos) == (1, 0)
    assert envido.retornar_quem_fugiu() == BOT

    humano, bot = jogador_com_mao(*MAO_33), bot_com_mao(*MAO_7)
    pedir(cbr_falsa(envido=1), ENVIDO, HUMANO, humano, bot, interface)
    assert (humano.pontos, bot.pontos) == (2, 0)
    assert "Jogador 1 Vencedor Envido" in capsys.readouterr().out


# Confere a pontuação de Real Envido e Falta Envido.
@pytest.mark.requisito("CT13")
@pytest.mark.requisito("CT14")
def test_CT13_CT14_valores_do_real_envido_e_da_falta_envido(jogador_com_mao, bot_com_mao, interface, cbr_falsa):
    humano, bot = jogador_com_mao(*MAO_33), bot_com_mao(*MAO_7)
    pedir(cbr_falsa(envido=1), REAL_ENVIDO, HUMANO, humano, bot, interface)
    assert humano.pontos == 5

    for pontos_bot, falta in ((0, 12), (8, 4)):
        humano, bot = jogador_com_mao(*MAO_33), bot_com_mao(*MAO_7)
        bot.pontos = pontos_bot
        envido = pedir(cbr_falsa(envido=1), FALTA_ENVIDO, HUMANO, humano, bot, interface)
        assert envido.valor_envido == falta and humano.pontos == falta


# Confere o vencedor do Envido com pontos diferentes ou iguais.
@pytest.mark.requisito("CT15")
def test_CT15_vencedor_do_envido_inclusive_no_empate():
    for pontos_j1, pontos_j2, vencedor in ((33, 7, 1), (7, 33, 2), (25, 25, 1)):
        envido, j1, j2 = Envido(), Jogador("Renato"), Jogador("Lucas")
        envido.jogador1_pontos, envido.jogador2_pontos = pontos_j1, pontos_j2
        envido.avaliar_vencedor_envido(HUMANO, j1, j2)
        assert envido.quem_venceu_envido == vencedor, (pontos_j1, pontos_j2)


# Verifica se um segundo pedido de Envido na mesma mão é ignorado.
@pytest.mark.requisito("CT16")
def test_CT16_segundo_pedido_na_mesma_mao_e_ignorado(humano, bot, interface, cbr_falsa):
    envido = pedir(cbr_falsa(envido=1), ENVIDO, HUMANO, humano, bot, interface)
    ia = cbr_falsa(envido=1)
    assert envido.controlador_envido(ia, None, REAL_ENVIDO, HUMANO, humano, bot, interface) is None
    assert ia.chamadas == []
    assert humano.pontos == 2


# Força o Envido no turno do bot e verifica quem pediu e quem respondeu.
@pytest.mark.requisito("CT17")
@pytest.mark.cenario
@pytest.mark.lento
@pytest.mark.defeito("D03")
@pytest.mark.xfail(reason="D03: turno_do_bot chama controlador_envido com os argumentos errados (TypeError) "
                          "e, em seguida, registra o pedido como sendo do humano (quem_pediu=1)")
def test_D03_bot_pede_envido_na_sua_vez(executar_partida, monkeypatch):
    jogar_carta_original = Bot.jogar_carta
    vezes = {"n": 0}

    def bot_decide_pedir_envido(self, cbr, truco):
        vezes["n"] += 1
        return ENVIDO if vezes["n"] == 1 else jogar_carta_original(self, cbr, truco)

    controlador_original = Envido.controlador_envido
    assinatura = inspect.signature(controlador_original)
    pedidos = []

    def controlador_espiao(self, *args, **kwargs):
        argumentos = assinatura.bind(self, *args, **kwargs)
        pedidos.append((argumentos.arguments["tipo"], argumentos.arguments["quem_pediu"]))
        return controlador_original(self, *args, **kwargs)

    avaliar_original = Bot.avaliar_envido
    respostas_do_bot = []

    def avaliar_espiao(self, cbr, tipo, quem_pediu, pontos_totais_adversario):
        if quem_pediu == HUMANO:
            respostas_do_bot.append(tipo)
        return avaliar_original(self, cbr, tipo, quem_pediu, pontos_totais_adversario)

    monkeypatch.setattr(Bot, "jogar_carta", bot_decide_pedir_envido)
    monkeypatch.setattr(Envido, "controlador_envido", controlador_espiao)
    monkeypatch.setattr(Bot, "avaliar_envido", avaliar_espiao)

    partida = executar_partida(
        "Renato", "Lucas", "0", "1", "1", "1",
        maos=[(["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"],
               ["12 de OUROS", "11 de BASTOS", "4 de COPAS"])])

    assert not isinstance(partida.erro, TypeError)
    assert pedidos and all(quem_pediu == BOT for _, quem_pediu in pedidos), f"pedidos: {pedidos}"
    assert any("aceita o pedido de envido" in p for p in partida.perguntas)
    assert respostas_do_bot == []
