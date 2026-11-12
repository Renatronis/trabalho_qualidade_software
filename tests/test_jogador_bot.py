"""Ações do jogador e do bot e reinício da mão (CT24)."""
import pytest

from truco.bot import Bot

MAO = ("1 de ESPADAS", "3 de COPAS", "4 de OUROS")


# Confere a retirada de cartas da mão e a soma de pontos do jogador.
def test_jogador_joga_cartas_e_acumula_pontos(jogador_com_mao):
    jogador = jogador_com_mao(*MAO)
    assert jogador.jogar_carta(1).retornar_carta() == "3 de COPAS"
    assert [c.retornar_carta() for c in jogador.checa_mao()] == ["1 de ESPADAS", "4 de OUROS"]
    with pytest.raises(IndexError):
        jogador.jogar_carta(5)
    for valor in (1, 2, 3):
        jogador.adicionar_pontos(valor)
    assert jogador.retorna_pontos_totais() == 6


# Verifica se o bot consulta a IA e atualiza a mão após jogar.
def test_bot_consulta_a_ia_para_jogar_e_atualiza_a_mao(bot_com_mao, cbr_falsa):
    bot, ia = bot_com_mao(*MAO), cbr_falsa(jogar_carta=1)
    assert bot.qualidade_mao == pytest.approx(38.3947, abs=1e-3)
    assert bot.jogar_carta(ia, None) == 1
    assert ia.chamadas == [("jogar_carta", 1, [52, 24, 1])]
    assert bot.pontuacao_cartas == [52, 1]
    assert bot.rodada == 2


# Confere o pedido de Truco do bot com duas cartas conforme a resposta da IA.
def test_bot_com_duas_cartas_pede_truco_conforme_a_ia(bot_com_mao, cbr_falsa):
    for resposta_ia, retorno, pediu in ((None, 0, False), (0, 0, False), (1, 4, True), (2, 4, True)):
        bot = bot_com_mao(*MAO)
        bot.mao.pop(0)
        assert bot.jogar_carta(cbr_falsa(truco=resposta_ia, jogar_carta=0), None) == retorno
        assert bot.pediu_truco is pediu, resposta_ia


# Confere a limpeza do estado da mão e a preservação dos pontos.
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


# Exercita os métodos auxiliares do bot, do baralho, do jogo e do envido.
def test_metodos_auxiliares_de_bot_baralho_jogo_e_envido(bot_com_mao, capsys):
    from truco.baralho import Baralho
    from truco.envido import Envido
    from truco.jogador import Jogador
    from truco.jogo import Jogo

    bot = bot_com_mao(*MAO)
    bot.adicionar_rodada()
    bot.adicionar_pontos(3)
    assert bot.rodadas == 1 and bot.retorna_pontos_totais() == 3
    assert bot.avaliar_pedir_envido() == 1

    bot.mostrar_mao()
    Baralho().printar_baralho()
    saida = capsys.readouterr().out.splitlines()
    assert saida[0] == "[0] 1 de ESPADAS" and len(saida) == 3 + 40   # mão do bot + baralho inteiro

    envido = Envido()
    envido.inicializar_jogador_bloqueado(1)
    envido.inverter_jogador_bloqueado()
    assert envido.jogador_bloqueado == 2

    humano, outro = Jogador("Renato"), Jogador("Lucas")
    humano.primeiro, outro.primeiro = False, True
    Jogo().jogador_fugiu(outro, humano, outro, -1)
    assert (humano.primeiro, outro.primeiro) == (True, False)
