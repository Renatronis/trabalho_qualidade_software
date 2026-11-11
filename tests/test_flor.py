"""
Etapa 3 - Testes unitários da Flor.

Casos de teste: CT25 a CT27 (defeitos D09, D14).
Requisito: RF12 (flor = 3 cartas do mesmo naipe, vale 3; contraflor vale 6;
contraflor e o resto vale a contraflor mais a falta).
"""
import pytest

from truco.flor import Flor

FLOR_COPAS = ("1 de COPAS", "5 de COPAS", "7 de COPAS")      # envido 32
FLOR_OUROS = ("12 de OUROS", "2 de OUROS", "3 de OUROS")     # envido 25
SEM_FLOR = ("4 de ESPADAS", "5 de BASTOS", "6 de ESPADAS")


@pytest.fixture
def flor():
    return Flor()


# ---------------------------------------------------------------- CT25 / RF12
@pytest.mark.requisito("CT25")
@pytest.mark.parametrize("tipo", ["jogador", "bot"])
@pytest.mark.parametrize("mao, tem_flor", [
    (FLOR_COPAS, True),
    (FLOR_OUROS, True),
    (SEM_FLOR, False),
    (("1 de COPAS", "5 de COPAS", "7 de OUROS"), False),   # 2 + 1
    (("1 de ESPADAS", "5 de COPAS", "7 de OUROS"), False), # 3 naipes diferentes
], ids=["flor-copas", "flor-ouros", "sem-flor", "dois-mais-um", "todos-diferentes"])
def test_checa_flor(jogador_com_mao, bot_com_mao, tipo, mao, tem_flor):
    fabrica = jogador_com_mao if tipo == "jogador" else bot_com_mao
    assert fabrica(*mao).checa_flor() is tem_flor


def test_bot_marca_flor_ao_receber_a_mao(bot_com_mao):
    assert bot_com_mao(*FLOR_COPAS).flor is True
    assert bot_com_mao(*SEM_FLOR).flor is False


# ---------------------------------------------------------------- CT26 / RF12
@pytest.mark.requisito("CT26")
class TestPedirFlor:
    def test_so_o_humano_tem_flor(self, flor, jogador_com_mao, bot_com_mao, interface, capsys):
        humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*SEM_FLOR)
        humano.flor = True
        flor.pedir_flor(1, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (3, 0)
        assert humano.pediu_flor is True
        assert "Jogador 1 - Renato: Venceu a flor e ganhou 3 pontos" in capsys.readouterr().out

    def test_so_o_bot_tem_flor(self, flor, jogador_com_mao, bot_com_mao, interface, capsys):
        humano, bot = jogador_com_mao(*SEM_FLOR), bot_com_mao(*FLOR_OUROS)
        flor.pedir_flor(2, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (0, 3)
        assert bot.pediu_flor is True
        assert "Jogador 2 - Bot: Venceu a flor" in capsys.readouterr().out

    @pytest.mark.parametrize("mao_humano, mao_bot, pontos", [
        (FLOR_COPAS, FLOR_OUROS, (6, 0)),   # 32 x 25: humano vence
        (FLOR_OUROS, FLOR_COPAS, (0, 6)),   # 25 x 32: bot vence
    ], ids=["humano-vence", "bot-vence"])
    def test_contraflor_aceita(self, flor, jogador_com_mao, bot_com_mao, interface, entradas_usuario,
                               mao_humano, mao_bot, pontos):
        humano, bot = jogador_com_mao(*mao_humano), bot_com_mao(*mao_bot)
        humano.flor = True
        registro = entradas_usuario("1")
        flor.pedir_flor(1, humano, bot, interface)
        assert "Contraflor" in registro.perguntas[0]
        assert (humano.pontos, bot.pontos) == pontos

    def test_contraflor_recusada_bot_ganha_4(self, flor, jogador_com_mao, bot_com_mao, interface,
                                             entradas_usuario):
        humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*FLOR_OUROS)
        humano.flor = True
        entradas_usuario("0")
        flor.pedir_flor(1, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (0, 4)

    def test_contraflor_e_resto_e_oferecida_quando_o_bot_esta_atras(self, flor, jogador_com_mao, bot_com_mao,
                                                                   interface, entradas_usuario):
        humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*FLOR_OUROS)
        humano.flor, humano.pontos, bot.pontos = True, 6, 0
        registro = entradas_usuario("1")
        flor.pedir_flor(1, humano, bot, interface)
        assert "Contraflor e Resto" in registro.perguntas[0]

    @pytest.mark.defeito("D14")
    @pytest.mark.xfail(reason="D14: contraflor e o resto vale apenas 3 pontos (o valor da flor simples)")
    def test_contraflor_e_resto_vale_mais_que_a_contraflor(self, flor, jogador_com_mao, bot_com_mao,
                                                          interface, entradas_usuario):
        humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*FLOR_OUROS)
        humano.flor, humano.pontos, bot.pontos = True, 6, 0
        entradas_usuario("1")
        flor.pedir_flor(1, humano, bot, interface)
        assert humano.pontos - 6 > 6

    def test_flor_so_pode_ser_cantada_uma_vez_por_mao(self, flor, jogador_com_mao, bot_com_mao, interface):
        humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*SEM_FLOR)
        humano.flor = True
        flor.pedir_flor(1, humano, bot, interface)
        flor.pedir_flor(1, humano, bot, interface)
        assert humano.pontos == 3

    def test_resetar_flor(self, flor, jogador_com_mao, bot_com_mao, interface):
        humano, bot = jogador_com_mao(*FLOR_COPAS), bot_com_mao(*SEM_FLOR)
        humano.flor = True
        flor.pedir_flor(1, humano, bot, interface)
        flor.resetar_flor()
        assert vars(flor) == vars(Flor())


# ---------------------------------------------------------------- CT27 / RF12
@pytest.mark.requisito("CT27")
@pytest.mark.entrada
class TestDecisaoDoJogador:
    @pytest.mark.parametrize("respostas, esperado, perguntas", [
        (["1"], True, 1),
        (["0"], False, 1),
        (["5", "1"], True, 2),
        (["2", "-1", "0"], False, 3),
    ], ids=["sim", "nao", "invalida-depois-sim", "duas-invalidas-depois-nao"])
    def test_respostas(self, flor, entradas_usuario, respostas, esperado, perguntas):
        flor.estado_atual = "Contraflor"
        registro = entradas_usuario(*respostas)
        assert flor.decisao_jogador() is esperado
        assert len(registro.perguntas) == perguntas
        assert "você aceita o pedido de Contraflor?" in registro.perguntas[0]

    @pytest.mark.defeito("D09")
    @pytest.mark.xfail(raises=ValueError, reason="D09: entrada não numérica derruba o jogo")
    def test_entrada_nao_numerica(self, flor, entradas_usuario):
        entradas_usuario("sim", "1")
        assert flor.decisao_jogador() is True
