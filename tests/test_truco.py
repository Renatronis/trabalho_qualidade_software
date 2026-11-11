"""
Etapa 3 - Testes unitários do Truco.

Casos de teste: CT18 a CT23 (defeitos D05, D06, D07, D09, D11, D12).
Requisito: RF07 (truco = 2, retruco = 3, vale 4 = 4; recusa entrega o valor
anterior; o mesmo jogador não aumenta duas vezes seguidas).

quem_pediu = 1 é o humano (responde pelo teclado simulado) e 2 é o bot
(responde pela IA dublê cbr_falsa).
"""
import pytest

from truco.truco import Truco

HUMANO, BOT = 1, 2


@pytest.fixture
def truco():
    return Truco()


@pytest.fixture
def humano(jogador_com_mao):
    return jogador_com_mao("3 de COPAS", "2 de OUROS", "4 de BASTOS", nome="Renato")


@pytest.fixture
def bot(bot_com_mao):
    return bot_com_mao("1 de ESPADAS", "7 de OUROS", "5 de COPAS", nome="Lucas")


def pedir(truco, ia, quem_pediu, humano, bot):
    return truco.controlador_truco(ia, None, quem_pediu, humano, bot)


# ---------------------------------------------------------------- CT18 / RF07
@pytest.mark.requisito("CT18")
class TestTrucoAceito:
    def test_humano_pede_e_bot_aceita_retorna_true(self, truco, humano, bot, cbr_falsa):
        assert pedir(truco, cbr_falsa(truco=1), HUMANO, humano, bot) is True
        assert truco.estado_atual == "truco"

    def test_bot_pede_e_humano_aceita_retorna_true(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("1")
        assert pedir(truco, cbr_falsa(), BOT, humano, bot) is True

    @pytest.mark.defeito("D05")
    @pytest.mark.xfail(reason="D05: truco aceito não atualiza o valor da mão (continua 1)")
    @pytest.mark.parametrize("quem_pediu", [HUMANO, BOT], ids=["humano-pede", "bot-pede"])
    def test_truco_aceito_vale_2(self, truco, humano, bot, cbr_falsa, entradas_usuario, quem_pediu):
        entradas_usuario("1")
        pedir(truco, cbr_falsa(truco=1), quem_pediu, humano, bot)
        assert truco.retornar_valor_aposta() == 2


# ---------------------------------------------------------------- CT19 / RF07
@pytest.mark.requisito("CT19")
class TestAumentosDeAposta:
    def test_bot_aumenta_para_retruco_e_humano_aceita(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("1")
        assert pedir(truco, cbr_falsa(truco=2), HUMANO, humano, bot) is True
        assert truco.retornar_valor_aposta() == 3

    def test_cadeia_completa_ate_vale_4_numa_unica_resposta(self, truco, humano, bot, cbr_falsa,
                                                            entradas_usuario):
        # humano: truco -> bot: retruco -> humano: vale 4 -> bot: aceita
        entradas_usuario("2")
        assert pedir(truco, cbr_falsa(truco=[2, 1]), HUMANO, humano, bot) is True
        assert truco.retornar_valor_aposta() == 4
        assert humano.pediu_truco and bot.pediu_truco  # opção de truco some para os dois

    @pytest.mark.defeito("D06")
    @pytest.mark.xfail(reason="D06: no estado 'retruco' o controlador chama pedir_retruco de novo; o vale 4 nunca vem")
    def test_vale_4_em_pedidos_separados(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("1", "1")
        pedir(truco, cbr_falsa(truco=1), HUMANO, humano, bot)   # truco aceito
        pedir(truco, cbr_falsa(), BOT, humano, bot)             # bot pede retruco, humano aceita
        pedir(truco, cbr_falsa(truco=1), HUMANO, humano, bot)   # humano pede vale 4, bot aceita
        assert truco.retornar_valor_aposta() == 4


# ---------------------------------------------------------------- CT20 / RF07
@pytest.mark.requisito("CT20")
class TestRecusas:
    def test_bot_recusa_truco_humano_ganha_1(self, truco, humano, bot, cbr_falsa):
        assert pedir(truco, cbr_falsa(truco=0), HUMANO, humano, bot) is False
        assert (humano.pontos, bot.pontos) == (1, 0)

    def test_humano_recusa_truco_bot_ganha_1(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("0")
        assert pedir(truco, cbr_falsa(), BOT, humano, bot) is False
        assert (humano.pontos, bot.pontos) == (0, 1)

    def test_humano_recusa_retruco_bot_ganha_2(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("0")
        assert pedir(truco, cbr_falsa(truco=2), HUMANO, humano, bot) is False
        assert (humano.pontos, bot.pontos) == (0, 2)

    def test_bot_recusa_vale_4_humano_ganha_3(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("2")
        assert pedir(truco, cbr_falsa(truco=[2, 0]), HUMANO, humano, bot) is False
        assert (humano.pontos, bot.pontos) == (3, 0)


# ---------------------------------------------------------------- CT21 / RF07
@pytest.mark.requisito("CT21")
class TestBloqueiosDoTruco:
    def test_mesmo_jogador_nao_pede_duas_vezes_seguidas(self, truco, humano, bot, cbr_falsa):
        pedir(truco, cbr_falsa(truco=1), HUMANO, humano, bot)
        ia = cbr_falsa(truco=1)
        assert pedir(truco, ia, HUMANO, humano, bot) is None
        assert ia.chamadas == []

    def test_estado_invalido_retorna_none(self, truco, humano, bot, cbr_falsa):
        truco.estado_atual = "desconhecido"
        assert pedir(truco, cbr_falsa(), HUMANO, humano, bot) is None

    def test_estado_vale_quatro_bloqueia_novos_pedidos(self, truco, humano, bot, cbr_falsa):
        truco.estado_atual = "vale_quatro"
        assert pedir(truco, cbr_falsa(), BOT, humano, bot) is None

    @pytest.mark.defeito("D11")
    @pytest.mark.xfail(reason="D11: o estado 'vale_quatro' nunca é gravado; novo pedido rebaixa a mão para 3")
    def test_depois_do_vale_4_nenhum_pedido_e_aceito(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("2", "1")
        pedir(truco, cbr_falsa(truco=[2, 1]), HUMANO, humano, bot)   # chega ao vale 4
        resultado = pedir(truco, cbr_falsa(), BOT, humano, bot)       # bot tenta pedir de novo
        assert resultado is None
        assert truco.retornar_valor_aposta() == 4


# ---------------------------------------------------------------- CT22 / RF07
@pytest.mark.requisito("CT22")
@pytest.mark.entrada
class TestHumanoRespondeTrucoDoBot:
    @pytest.mark.parametrize("invalidas", [["3"], ["9", "-1"]], ids=["3", "9-e-menos-1"])
    def test_opcao_invalida_repete_a_pergunta(self, truco, humano, bot, cbr_falsa, entradas_usuario, invalidas):
        registro = entradas_usuario(*invalidas, "1")
        assert pedir(truco, cbr_falsa(), BOT, humano, bot) is True
        assert len(registro.perguntas) == len(invalidas) + 1

    def test_pergunta_mostra_as_opcoes(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        registro = entradas_usuario("1")
        pedir(truco, cbr_falsa(), BOT, humano, bot)
        for opcao in ("[0] Recusar", "[1] Aceitar", "[2] Aumentar Aposta"):
            assert opcao in registro.perguntas[0]

    @pytest.mark.defeito("D05")
    @pytest.mark.xfail(reason="D05: a pergunta diz que a mão passa a valer 1 ponto")
    def test_pergunta_informa_que_a_mao_passa_a_valer_2(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        registro = entradas_usuario("1")
        pedir(truco, cbr_falsa(), BOT, humano, bot)
        assert "passa a valer 2 pontos" in registro.perguntas[0]

    @pytest.mark.defeito("D12")
    @pytest.mark.xfail(reason="D12: a mensagem diz que quem PEDIU aceitou, e não quem respondeu")
    def test_mensagem_cita_quem_aceitou(self, truco, humano, bot, cbr_falsa, entradas_usuario, capsys):
        entradas_usuario("1")
        pedir(truco, cbr_falsa(), BOT, humano, bot)
        assert "Jogador 1 aceitou o pedido." in capsys.readouterr().out

    @pytest.mark.defeito("D09")
    @pytest.mark.xfail(raises=ValueError, reason="D09: entrada não numérica derruba o jogo")
    def test_entrada_nao_numerica_repete_a_pergunta(self, truco, humano, bot, cbr_falsa, entradas_usuario):
        entradas_usuario("sim", "1")
        assert pedir(truco, cbr_falsa(), BOT, humano, bot) is True


# ---------------------------------------------------------------- CT23 / RF07
@pytest.mark.requisito("CT23")
class TestRetornosDoTruco:
    def test_valor_inicial_da_aposta_e_1(self, truco):
        assert truco.retornar_valor_aposta() == 1

    def test_ia_recebe_tipo_quem_pediu_e_qualidade_da_mao(self, truco, humano, bot, cbr_falsa):
        ia = cbr_falsa(truco=1)
        pedir(truco, ia, HUMANO, humano, bot)
        assert ia.chamadas == [("truco", "truco", HUMANO, bot.qualidade_mao)]

    @pytest.mark.defeito("D07")
    @pytest.mark.xfail(reason="D07: retornar_quem_fugiu devolve o próprio método e jogador_fugiu nunca é preenchido")
    def test_retornar_quem_fugiu(self, truco, humano, bot, cbr_falsa):
        pedir(truco, cbr_falsa(truco=0), HUMANO, humano, bot)
        assert truco.retornar_quem_fugiu() == BOT

    def test_resetar_volta_ao_estado_inicial(self, truco, humano, bot, cbr_falsa):
        pedir(truco, cbr_falsa(truco=1), HUMANO, humano, bot)
        truco.resetar()
        assert (truco.valor_aposta, truco.jogador_bloqueado, truco.estado_atual) == (1, 0, "")

    def test_inverter_jogador_bloqueado(self, truco):
        truco.inicializar_jogador_bloqueado(2)
        truco.inverter_jogador_bloqueado()
        assert truco.jogador_bloqueado == 1
        truco.inverter_jogador_bloqueado()
        assert truco.jogador_bloqueado == 2
