"""
Etapa 3 - Testes unitários de Jogador e Bot.

Casos de teste: CT24 (reset de estado) e testes de chamadas com parâmetros
variados e retornos de função dos métodos do Jogador e do Bot
(defeitos D13 e D15).
Requisitos: RF07, RF09, RF12, RF16, RNF03.
"""
import pytest

from truco.bot import Bot
from truco.jogador import Jogador

MAO_FORTE = ("1 de ESPADAS", "3 de COPAS", "4 de OUROS")


# ------------------------------------------------------------------ Jogador
class TestJogador:
    @pytest.mark.parametrize("indice, carta", [(0, "1 de ESPADAS"), (1, "3 de COPAS"), (2, "4 de OUROS")])
    def test_jogar_carta_remove_da_mao(self, jogador_com_mao, indice, carta):
        jogador = jogador_com_mao(*MAO_FORTE)
        assert jogador.jogar_carta(indice).retornar_carta() == carta
        assert len(jogador.checa_mao()) == 2

    @pytest.mark.parametrize("indice", [3, 9])
    def test_jogar_carta_com_indice_fora_da_mao_lanca_excecao(self, jogador_com_mao, indice):
        with pytest.raises(IndexError):
            jogador_com_mao(*MAO_FORTE).jogar_carta(indice)

    @pytest.mark.parametrize("somas, total", [([1], 1), ([2, 3], 5), ([1, 1, 4, 6], 12)])
    def test_adicionar_pontos(self, somas, total):
        jogador = Jogador("Renato")
        for valor in somas:
            jogador.adicionar_pontos(valor)
        assert jogador.retorna_pontos_totais() == total

    def test_adicionar_rodada(self):
        jogador = Jogador("Renato")
        jogador.adicionar_rodada()
        jogador.adicionar_rodada()
        assert jogador.rodadas == 2

    def test_mostrar_mao(self, jogador_com_mao, interface, capsys):
        jogador_com_mao(*MAO_FORTE).mostrar_mao(interface)
        assert capsys.readouterr().out == "[0] 1 de ESPADAS\n[1] 3 de COPAS\n[2] 4 de OUROS\n"


# ---------------------------------------------------------------------- Bot
class TestBotMao:
    def test_criar_mao_preenche_todos_os_atributos(self, bot_com_mao):
        bot = bot_com_mao(*MAO_FORTE)
        assert bot.indices == [0, 1, 2]
        assert bot.pontuacao_cartas == [52, 24, 1]
        assert bot.mao_rank == ["Alta", "Media", "Baixa"]
        assert bot.envido == 4 and bot.flor is False

    def test_qualidade_da_mao_valor_conhecido(self, bot_com_mao):
        assert bot_com_mao(*MAO_FORTE).qualidade_mao == pytest.approx(38.3947, abs=1e-3)

    def test_mao_mais_forte_tem_qualidade_maior(self, bot_com_mao):
        forte = bot_com_mao("1 de ESPADAS", "1 de BASTOS", "7 de ESPADAS")
        media = bot_com_mao("3 de COPAS", "2 de OUROS", "1 de COPAS")
        fraca = bot_com_mao("4 de COPAS", "5 de OUROS", "6 de BASTOS")
        assert forte.qualidade_mao > media.qualidade_mao > fraca.qualidade_mao

    @pytest.mark.parametrize("indice, restantes", [(0, [24, 1]), (1, [52, 1]), (2, [52, 24])])
    def test_ajustar_indices(self, bot_com_mao, indice, restantes):
        bot = bot_com_mao(*MAO_FORTE)
        bot.ajustar_indices(indice)
        assert bot.pontuacao_cartas == restantes
        assert len(bot.mao_rank) == len(bot.indices) == 2
        assert len(bot.mao) == 3  # a carta sai da mão no __main__, não aqui


class TestBotJogarCarta:
    def test_primeira_jogada_consulta_a_ia_com_a_rodada_1(self, bot_com_mao, cbr_falsa):
        bot, ia = bot_com_mao(*MAO_FORTE), cbr_falsa(jogar_carta=1)
        assert bot.jogar_carta(ia, None) == 1
        assert ia.chamadas == [("jogar_carta", 1, [52, 24, 1])]
        assert bot.rodada == 2
        assert bot.pontuacao_cartas == [52, 1]

    def test_com_3_cartas_nao_pede_truco(self, bot_com_mao, cbr_falsa):
        ia = cbr_falsa(truco=2)
        bot_com_mao(*MAO_FORTE).jogar_carta(ia, None)
        assert [c[0] for c in ia.chamadas] == ["jogar_carta"]

    @pytest.mark.parametrize("resposta_ia, retorno, pediu", [
        (None, 0, False), (0, 0, False), (1, 4, True), (2, 4, True)],
        ids=["ia-sem-resposta", "ia-nao-pede", "ia-pede", "ia-pede-forte"])
    def test_com_2_cartas_pode_pedir_truco(self, bot_com_mao, cbr_falsa, resposta_ia, retorno, pediu):
        bot = bot_com_mao(*MAO_FORTE)
        bot.jogar_carta(cbr_falsa(jogar_carta=0), None)
        bot.mao.pop(0)
        ia = cbr_falsa(truco=resposta_ia, jogar_carta=0)
        assert bot.jogar_carta(ia, None) == retorno
        assert bot.pediu_truco is pediu

    def test_nao_pede_truco_duas_vezes(self, bot_com_mao, cbr_falsa):
        bot = bot_com_mao(*MAO_FORTE)
        bot.mao.pop(0)
        bot.pediu_truco = True
        ia = cbr_falsa(truco=2, jogar_carta=0)
        bot.jogar_carta(ia, None)
        assert "truco" not in [c[0] for c in ia.chamadas]

    @pytest.mark.defeito("D15")
    @pytest.mark.xfail(reason="D15: criar_mao já marca flor=True, então a condição para cantar flor nunca é verdadeira")
    def test_bot_com_flor_canta_flor(self, bot_com_mao, cbr_falsa):
        bot = bot_com_mao("1 de COPAS", "5 de COPAS", "7 de COPAS")
        assert bot.jogar_carta(cbr_falsa(flor=True), None) == 5


class TestBotAvaliacoes:
    @pytest.mark.parametrize("pontos_adversario, pontos_bot, perdendo", [
        (0, 0, False), (6, 0, True), (7, 0, True), (2, 3, False), (3, 3, True), (6, 12, False)])
    def test_avaliar_envido_calcula_se_esta_perdendo(self, bot_com_mao, cbr_falsa,
                                                     pontos_adversario, pontos_bot, perdendo):
        bot, ia = bot_com_mao(*MAO_FORTE), cbr_falsa(envido=1)
        bot.pontos = pontos_bot
        assert bot.avaliar_envido(ia, 6, 1, pontos_adversario) == 1
        assert ia.chamadas[0] == ("envido", 6, 1, bot.envido, perdendo)

    @pytest.mark.parametrize("resposta", [0, 1, 2])
    def test_avaliar_truco_repassa_a_resposta_da_ia(self, bot_com_mao, cbr_falsa, resposta):
        bot, ia = bot_com_mao(*MAO_FORTE), cbr_falsa(truco=resposta)
        assert bot.avaliar_truco(ia, "retruco", 1) == resposta
        assert ia.chamadas[0] == ("truco", "retruco", 1, bot.qualidade_mao)

    def test_avaliar_pedir_envido(self):
        assert Bot("Lucas").avaliar_pedir_envido() == 1


class DadosFalsos:
    def __init__(self):
        self.chamadas = []

    def __getattr__(self, nome):
        return lambda *args: self.chamadas.append(nome)


@pytest.mark.parametrize("rodada, metodo", [
    (1, "primeira_rodada"), (2, "segunda_rodada"), (3, "terceira_rodada"), (4, "finalizar_rodadas"), (5, None)])
def test_enriquecer_bot_chama_o_registro_da_rodada(bot_com_mao, nova_carta, rodada, metodo):
    bot, dados = bot_com_mao(*MAO_FORTE), DadosFalsos()
    bot.rodada = rodada
    bot.enriquecer_bot(dados, nova_carta("3 de OUROS"), nova_carta("4 de COPAS"), 1)
    assert dados.chamadas == ([metodo] if metodo else [])


# ---------------------------------------------------------------- CT24 / RNF03
@pytest.mark.requisito("CT24")
class TestResetarEstado:
    def test_bot_resetar_mantem_nome_e_pontos(self, bot_com_mao, cbr_falsa):
        bot = bot_com_mao(*MAO_FORTE)
        bot.pontos, bot.rodadas, bot.pediu_truco, bot.pediu_flor = 7, 2, True, True
        bot.jogar_carta(cbr_falsa(), None)
        bot.resetar()
        novo = Bot("Bot")
        novo.pontos = 7
        assert vars(bot) == vars(novo)

    def test_jogador_resetar_zera_mao_rodadas_e_truco(self, jogador_com_mao):
        jogador = jogador_com_mao(*MAO_FORTE)
        jogador.pontos, jogador.rodadas, jogador.flor, jogador.pediu_truco = 5, 1, True, True
        jogador.resetar()
        assert (jogador.mao, jogador.rodadas, jogador.flor, jogador.pediu_truco) == ([], 0, False, False)
        assert jogador.pontos == 5

    @pytest.mark.defeito("D13")
    @pytest.mark.xfail(reason="D13: Jogador.resetar não zera pediu_flor; na mão seguinte o envido fica bloqueado")
    def test_jogador_resetar_zera_pediu_flor(self, jogador_com_mao):
        jogador = jogador_com_mao(*MAO_FORTE)
        jogador.pediu_flor = True
        jogador.resetar()
        assert jogador.pediu_flor is False
