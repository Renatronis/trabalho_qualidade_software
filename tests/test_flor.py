"""Identificação, pontuação e respostas de Flor (CT25 a CT27)."""
import pytest

from truco.flor import Flor

FLOR_COPAS = ("1 de COPAS", "5 de COPAS", "7 de COPAS")
FLOR_OUROS = ("12 de OUROS", "2 de OUROS", "3 de OUROS")
SEM_FLOR = ("4 de ESPADAS", "5 de BASTOS", "6 de ESPADAS")


# Confere se Flor exige três cartas do mesmo naipe.
@pytest.mark.requisito("CT25")
def test_CT25_flor_exige_tres_cartas_do_mesmo_naipe(jogador_com_mao, bot_com_mao):
    for fabrica in (jogador_com_mao, bot_com_mao):
        assert fabrica(*FLOR_COPAS).checa_flor() is True
        assert fabrica(*SEM_FLOR).checa_flor() is False
        assert fabrica("1 de COPAS", "5 de COPAS", "7 de OUROS").checa_flor() is False


# Confere três pontos para Flor e seis para Contraflor.
@pytest.mark.requisito("CT26")
def test_CT26_flor_vale_3_e_contraflor_vale_6(jogador_com_mao, bot_com_mao, interface, entradas_usuario, capsys):
    humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*SEM_FLOR)
    humano.flor = True
    Flor().pedir_flor(1, humano, bot, interface)
    assert (humano.pontos, bot.pontos) == (3, 0)
    assert "Venceu a flor e ganhou 3 pontos" in capsys.readouterr().out

    # os dois têm flor: contraflor aceita, vence quem tem mais pontos (32 x 25)
    humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*FLOR_OUROS)
    humano.flor = True
    entradas_usuario("1")
    Flor().pedir_flor(1, humano, bot, interface)
    assert (humano.pontos, bot.pontos) == (6, 0)


# Confere se a pergunta de Contraflor se repete após uma resposta inválida.
@pytest.mark.requisito("CT27")
@pytest.mark.entrada
def test_CT27_resposta_a_contraflor_com_opcao_invalida(entradas_usuario):
    flor = Flor()
    flor.estado_atual = "Contraflor"
    registro = entradas_usuario("5", "-1", "0")
    assert flor.decisao_jogador() is False
    assert len(registro.perguntas) == 3
    assert "você aceita o pedido de Contraflor?" in registro.perguntas[0]
