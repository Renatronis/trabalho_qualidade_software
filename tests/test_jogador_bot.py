"""
Jogador e Bot: chamadas com parâmetros variados e retornos.

Caso de teste: CT24 (reset de estado), além dos métodos usados pelo laço do jogo.
Requisitos: RF07, RF16, RNF03.
"""
import pytest

from truco.bot import Bot

MAO = ("1 de ESPADAS", "3 de COPAS", "4 de OUROS")   # pontuação [52, 24, 1]


def test_jogador_joga_cartas_e_acumula_pontos(jogador_com_mao):
    jogador = jogador_com_mao(*MAO)
    assert jogador.jogar_carta(1).retornar_carta() == "3 de COPAS"
    assert [c.retornar_carta() for c in jogador.checa_mao()] == ["1 de ESPADAS", "4 de OUROS"]
    with pytest.raises(IndexError):
        jogador.jogar_carta(5)                      # índice fora da mão
    for valor in (1, 2, 3):
        jogador.adicionar_pontos(valor)
    assert jogador.retorna_pontos_totais() == 6


def test_bot_consulta_a_ia_para_jogar_e_atualiza_a_mao(bot_com_mao, cbr_falsa):
    bot, ia = bot_com_mao(*MAO), cbr_falsa(jogar_carta=1)
    assert bot.qualidade_mao == pytest.approx(38.3947, abs=1e-3)
    assert bot.jogar_carta(ia, None) == 1
    assert ia.chamadas == [("jogar_carta", 1, [52, 24, 1])]   # rodada 1 e a pontuação da mão
    assert bot.pontuacao_cartas == [52, 1]                    # a carta escolhida sai das listas
    assert bot.rodada == 2


def test_bot_com_duas_cartas_pede_truco_conforme_a_ia(bot_com_mao, cbr_falsa):
    """Combinações do 'if truco is None / elif truco in [1, 2]' do Bot.jogar_carta."""
    for resposta_ia, retorno, pediu in ((None, 0, False), (0, 0, False), (1, 4, True), (2, 4, True)):
        bot = bot_com_mao(*MAO)
        bot.mao.pop(0)                                         # sobram 2 cartas
        assert bot.jogar_carta(cbr_falsa(truco=resposta_ia, jogar_carta=0), None) == retorno
        assert bot.pediu_truco is pediu, resposta_ia


@pytest.mark.requisito("CT24")
def test_CT24_nova_mao_zera_o_estado_e_mantem_os_pontos(bot_com_mao, jogador_com_mao, cbr_falsa):
    bot = bot_com_mao(*MAO)
    bot.pontos, bot.rodadas, bot.pediu_truco = 7, 2, True
    bot.jogar_carta(cbr_falsa(), None)
    bot.resetar()
    novo = Bot("Bot")
    novo.pontos = 7
    assert vars(bot) == vars(novo)

    jogador = jogador_com_mao(*MAO)
    jogador.pontos, jogador.rodadas, jogador.pediu_truco = 5, 1, True
    jogador.resetar()
    assert (jogador.mao, jogador.rodadas, jogador.pediu_truco, jogador.pontos) == ([], 0, False, 5)
