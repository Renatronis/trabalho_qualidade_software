"""
Etapa 3 - Testes unitários do Envido.

Casos de teste: CT10 a CT17 (defeitos D03, D04, D09, D10).
Requisitos: RF09 (pedidos e valores), RF10 (cálculo dos pontos), RF11 (vencedor).

O bot responde por meio de uma IA "dublê" (cbr_falsa), para que o teste
controle a resposta. O humano responde pelo teclado simulado (entradas_usuario).
Nas chamadas, quem_pediu = 1 é o humano e quem_pediu = 2 é o bot.
"""
import pytest

from truco.bot import Bot
from truco.envido import Envido
from truco.jogador import Jogador

MAO_33 = ("7 de COPAS", "6 de COPAS", "1 de OUROS")    # 20 + 7 + 6 = 33
MAO_7 = ("7 de BASTOS", "6 de ESPADAS", "1 de COPAS")  # naipes diferentes: maior carta = 7

# Códigos usados pelo jogo
ENVIDO, REAL_ENVIDO, FALTA_ENVIDO = 6, 7, 8
HUMANO, BOT = 1, 2


@pytest.fixture
def envido():
    return Envido()


@pytest.fixture
def humano(jogador_com_mao):
    """Humano com 33 pontos de envido."""
    return jogador_com_mao(*MAO_33, nome="Renato")


@pytest.fixture
def bot(bot_com_mao):
    """Bot com 7 pontos de envido."""
    return bot_com_mao(*MAO_7, nome="Lucas")


def pedir(envido, ia, tipo, quem_pediu, humano, bot, interface):
    return envido.controlador_envido(ia, None, tipo, quem_pediu, humano, bot, interface)


# ---------------------------------------------------------------- CT10 / RF10
CASOS_ENVIDO = [
    pytest.param(MAO_33, 33, id="par-7-6-mesmo-naipe"),
    pytest.param(MAO_7, 7, id="naipes-diferentes"),
    pytest.param(("5 de COPAS", "4 de COPAS", "7 de OUROS"), 29, id="par-5-4"),
    pytest.param(("1 de COPAS", "2 de COPAS", "3 de COPAS"), 25, id="tres-do-mesmo-naipe"),
    pytest.param(("12 de COPAS", "11 de OUROS", "10 de BASTOS"), 0, id="so-figuras"),
    pytest.param(("12 de COPAS", "7 de COPAS", "4 de OUROS"), 27, id="figura-e-7-mesmo-naipe",
                 marks=[pytest.mark.defeito("D03"),
                        pytest.mark.xfail(reason="D03: par com figura vira 'maior carta' (retorna 7)")]),
    pytest.param(("10 de COPAS", "11 de COPAS", "4 de OUROS"), 20, id="duas-figuras-mesmo-naipe",
                 marks=[pytest.mark.defeito("D03"),
                        pytest.mark.xfail(reason="D03: par de figuras deveria valer 20 (retorna 4)")]),
]


@pytest.mark.requisito("CT10")
@pytest.mark.parametrize("classe", [Jogador, Bot], ids=["jogador", "bot"])
@pytest.mark.parametrize("mao, pontos", CASOS_ENVIDO)
def test_calcula_envido(nova_mao, classe, mao, pontos):
    assert classe("Teste").calcula_envido(nova_mao(*mao)) == pontos


def test_criar_mao_guarda_os_pontos_de_envido(humano, bot):
    assert humano.retorna_pontos_envido() == 33
    assert bot.retorna_pontos_envido() == 7


# ---------------------------------------------------------------- CT11 / RF09
@pytest.mark.requisito("CT11")
@pytest.mark.entrada
class TestHumanoRespondeEnvidoDoBot:
    @pytest.mark.parametrize("respostas, pontos_humano, pontos_bot", [
        (["0"], 0, 1),          # recusa: o bot (quem pediu) ganha 1
        (["1"], 2, 0),          # aceita: humano vence 33 x 7 e ganha 2
        (["2"], 5, 0),          # pede Real Envido; o bot aceita; humano ganha 5
        (["3"], 12, 0),         # pede Falta Envido; o bot aceita; humano ganha 12 - 0
    ], ids=["recusar", "aceitar", "real-envido", "falta-envido"])
    def test_cada_opcao(self, envido, humano, bot, interface, cbr_falsa, entradas_usuario,
                        respostas, pontos_humano, pontos_bot):
        entradas_usuario(*respostas)
        pedir(envido, cbr_falsa(envido=1), ENVIDO, BOT, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (pontos_humano, pontos_bot)

    @pytest.mark.parametrize("invalidas", [["9"], ["-1"], ["4", "7"]], ids=["9", "-1", "4-e-7"])
    def test_opcao_invalida_repete_a_pergunta(self, envido, humano, bot, interface, cbr_falsa,
                                              entradas_usuario, invalidas):
        registro = entradas_usuario(*invalidas, "1")
        pedir(envido, cbr_falsa(), ENVIDO, BOT, humano, bot, interface)
        assert len(registro.perguntas) == len(invalidas) + 1
        assert all("aceita o pedido de envido" in p for p in registro.perguntas)
        assert humano.pontos == 2

    @pytest.mark.defeito("D09")
    @pytest.mark.xfail(raises=ValueError, reason="D09: entrada não numérica derruba o jogo (int(input()))")
    def test_entrada_nao_numerica_repete_a_pergunta(self, envido, humano, bot, interface,
                                                    cbr_falsa, entradas_usuario):
        entradas_usuario("s", "1")
        pedir(envido, cbr_falsa(), ENVIDO, BOT, humano, bot, interface)
        assert humano.pontos == 2


# ---------------------------------------------------------------- CT12 / RF09
@pytest.mark.requisito("CT12")
class TestHumanoPedeEnvido:
    def test_bot_recusa_humano_ganha_1(self, envido, humano, bot, interface, cbr_falsa, capsys):
        pedir(envido, cbr_falsa(envido=0), ENVIDO, HUMANO, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (1, 0)
        assert envido.retornar_quem_fugiu() == BOT
        assert "Vencedor Envido" not in capsys.readouterr().out

    def test_bot_aceita_e_humano_vence(self, envido, humano, bot, interface, cbr_falsa, capsys):
        pedir(envido, cbr_falsa(envido=1), ENVIDO, HUMANO, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (2, 0)
        assert "Jogador 1 Vencedor Envido" in capsys.readouterr().out

    def test_bot_aceita_e_bot_vence(self, envido, jogador_com_mao, bot_com_mao, interface, cbr_falsa):
        humano = jogador_com_mao(*MAO_7)
        bot = bot_com_mao(*MAO_33)
        pedir(envido, cbr_falsa(envido=1), ENVIDO, HUMANO, humano, bot, interface)
        assert (humano.pontos, bot.pontos) == (0, 2)

    def test_bot_aumenta_para_real_envido_e_humano_aceita(self, envido, humano, bot, interface,
                                                         cbr_falsa, entradas_usuario):
        registro = entradas_usuario("1")
        pedir(envido, cbr_falsa(envido=2), ENVIDO, HUMANO, humano, bot, interface)
        assert "Real envido" in registro.perguntas[0]
        assert humano.pontos == 5

    def test_bot_aumenta_para_falta_envido_e_humano_aceita(self, envido, humano, bot, interface,
                                                          cbr_falsa, entradas_usuario):
        entradas_usuario("1")
        humano.pontos = 3
        pedir(envido, cbr_falsa(envido=3), ENVIDO, HUMANO, humano, bot, interface)
        assert humano.pontos == 3 + (12 - 3)  # falta = 12 - pontos do adversário de quem pediu

    def test_ia_recebe_o_tipo_e_os_pontos_do_bot(self, envido, humano, bot, interface, cbr_falsa):
        ia = cbr_falsa(envido=1)
        pedir(envido, ia, ENVIDO, HUMANO, humano, bot, interface)
        nome, tipo, quem_pediu, pontos_robo, _ = ia.chamadas[0]
        assert (nome, tipo, quem_pediu, pontos_robo) == ("envido", ENVIDO, HUMANO, 7)

    @pytest.mark.defeito("D10")
    @pytest.mark.xfail(reason="D10: o bot avalia se está perdendo com os próprios pontos de envido, não com o placar")
    def test_bot_empatado_no_placar_nao_esta_perdendo(self, envido, humano, bot, interface, cbr_falsa):
        ia = cbr_falsa(envido=1)
        humano.pontos, bot.pontos = 0, 0
        pedir(envido, ia, ENVIDO, HUMANO, humano, bot, interface)
        robo_perdendo = ia.chamadas[0][4]
        assert robo_perdendo is False


# ---------------------------------------------------------------- CT13 / RF09
@pytest.mark.requisito("CT13")
@pytest.mark.parametrize("resposta_bot, pontos_humano", [(1, 5), (0, 2)], ids=["aceita", "recusa"])
def test_real_envido(envido, humano, bot, interface, cbr_falsa, resposta_bot, pontos_humano):
    pedir(envido, cbr_falsa(envido=resposta_bot), REAL_ENVIDO, HUMANO, humano, bot, interface)
    assert humano.pontos == pontos_humano


@pytest.mark.requisito("CT13")
def test_real_envido_bot_aumenta_para_falta(envido, humano, bot, interface, cbr_falsa, entradas_usuario):
    registro = entradas_usuario("1")
    pedir(envido, cbr_falsa(envido=2), REAL_ENVIDO, HUMANO, humano, bot, interface)
    assert "[1] Aceitar" in registro.perguntas[0]
    assert humano.pontos == 12


# ---------------------------------------------------------------- CT14 / RF09
@pytest.mark.requisito("CT14")
@pytest.mark.parametrize("pontos_bot, valor_falta", [(0, 12), (8, 4), (11, 1)])
def test_falta_envido_vale_12_menos_pontos_do_adversario(envido, humano, bot, interface, cbr_falsa,
                                                         pontos_bot, valor_falta):
    bot.pontos = pontos_bot
    pedir(envido, cbr_falsa(envido=1), FALTA_ENVIDO, HUMANO, humano, bot, interface)
    assert envido.valor_envido == valor_falta
    assert humano.pontos == valor_falta


@pytest.mark.requisito("CT14")
def test_falta_envido_recusado(envido, humano, bot, interface, cbr_falsa):
    pedir(envido, cbr_falsa(envido=0), FALTA_ENVIDO, HUMANO, humano, bot, interface)
    assert (humano.pontos, bot.pontos) == (5, 0)


# ---------------------------------------------------------------- CT15 / RF11
@pytest.mark.requisito("CT15")
@pytest.mark.parametrize("metodo", ["avaliar_vencedor_envido", "avaliar_vencedor_falta_envido"])
@pytest.mark.parametrize("pontos_j1, pontos_j2, vencedor", [
    (33, 7, 1), (7, 33, 2), (25, 25, 1)], ids=["j1-maior", "j2-maior", "empate-vence-j1"])
def test_vencedor_do_envido(envido, metodo, pontos_j1, pontos_j2, vencedor):
    j1, j2 = Jogador("Renato"), Jogador("Lucas")
    envido.jogador1_pontos, envido.jogador2_pontos = pontos_j1, pontos_j2
    getattr(envido, metodo)(HUMANO, j1, j2)
    assert envido.quem_venceu_envido == vencedor
    assert (j1.pontos > 0, j2.pontos > 0) == (vencedor == 1, vencedor == 2)


# ---------------------------------------------------------------- CT16 / RF09
@pytest.mark.requisito("CT16")
class TestBloqueiosDoEnvido:
    def test_segundo_pedido_na_mesma_mao_e_ignorado(self, envido, humano, bot, interface, cbr_falsa):
        pedir(envido, cbr_falsa(envido=1), ENVIDO, HUMANO, humano, bot, interface)
        ia = cbr_falsa(envido=1)
        assert pedir(envido, ia, REAL_ENVIDO, HUMANO, humano, bot, interface) is None
        assert ia.chamadas == []
        assert humano.pontos == 2

    def test_jogador_bloqueado_nao_pode_pedir(self, envido, humano, bot, interface, cbr_falsa):
        envido.jogador_bloqueado = HUMANO
        ia = cbr_falsa(envido=1)
        assert pedir(envido, ia, ENVIDO, HUMANO, humano, bot, interface) is None
        assert ia.chamadas == [] and humano.pontos == 0

    def test_inverter_jogador_bloqueado(self, envido):
        envido.inicializar_jogador_bloqueado(1)
        envido.inverter_jogador_bloqueado()
        assert envido.jogador_bloqueado == 2
        envido.inverter_jogador_bloqueado()
        assert envido.jogador_bloqueado == 1

    def test_resetar_volta_ao_estado_inicial(self, envido, humano, bot, interface, cbr_falsa):
        pedir(envido, cbr_falsa(envido=1), FALTA_ENVIDO, HUMANO, humano, bot, interface)
        envido.resetar()
        assert vars(envido) == vars(Envido())


# ---------------------------------------------------------------- CT17 / RF09
@pytest.mark.requisito("CT17")
@pytest.mark.cenario
@pytest.mark.lento
@pytest.mark.defeito("D04")
@pytest.mark.xfail(reason="D04: turno_do_bot chama controlador_envido com os argumentos errados (TypeError)")
def test_bot_pede_envido_na_sua_vez(executar_partida, monkeypatch):
    """Executa o turno REAL do bot (truco/__main__.py, linhas 125-136).

    Só a decisão do bot é fixada: na primeira vez que ele joga, escolhe 6
    (Envido). Todo o resto, inclusive a chamada defeituosa, é o código do jogo.
    Quando o D04 for corrigido, este teste passa sem precisar de mudança.
    """
    jogar_carta_original = Bot.jogar_carta
    vezes = {"n": 0}

    def bot_decide_pedir_envido(self, cbr, truco):
        vezes["n"] += 1
        if vezes["n"] == 1:
            return ENVIDO
        return jogar_carta_original(self, cbr, truco)

    monkeypatch.setattr(Bot, "jogar_carta", bot_decide_pedir_envido)
    partida = executar_partida(
        "Renato", "Lucas", "0", "1", "1", "1",
        maos=[(["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"],
               ["12 de OUROS", "11 de BASTOS", "4 de COPAS"])])
    assert not isinstance(partida.erro, TypeError)
    assert "Jogador pediu Envido!" in partida.saida


@pytest.mark.requisito("CT11")
@pytest.mark.defeito("D12")
@pytest.mark.xfail(reason="D12: quando o bot pede, a pergunta ao humano diz 'Jogador 2, você aceita...'")
def test_pergunta_do_envido_e_feita_ao_jogador_1(envido, humano, bot, interface, cbr_falsa, entradas_usuario):
    registro = entradas_usuario("1")
    pedir(envido, cbr_falsa(), ENVIDO, BOT, humano, bot, interface)
    assert registro.perguntas[0].startswith("Jogador 1")
