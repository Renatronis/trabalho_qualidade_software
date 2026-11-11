"""
Etapa 5 - Cenários de uso ponta a ponta (partida executada pelo __main__).

Casos de teste: CT42 e CT43, mais os cenários UC03, UC04 e UC05
(defeitos D05, D12 e D26 confirmados dentro de uma partida real).

As mãos são fixas e a IA é a verdadeira; com o registro inicial a IA é
determinística, então cada cenário sempre segue o mesmo caminho.
"""
import pandas as pd
import pytest

from conftest import EntradasEsgotadas

pytestmark = [pytest.mark.cenario, pytest.mark.lento]

HUMANO_FORTE = ["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"]
BOT_FRACO = ["12 de OUROS", "11 de BASTOS", "4 de COPAS"]   # envido 4
HUMANO_ENVIDO_7 = ["7 de BASTOS", "5 de ESPADAS", "4 de OUROS"]
BOT_ENVIDO_33 = ["7 de COPAS", "6 de COPAS", "12 de ESPADAS"]


def pontos(partida):
    return partida.estado["jogador1"].pontos, partida.estado["jogador2"].pontos


# ---------------------------------------------------------------- CT42 / UC02
@pytest.mark.requisito("CT42")
class TestMaoCompleta:
    """Renato joga o 1 de Espadas, depois o 1 de Bastos; o bot pede truco na 2ª rodada e Renato aceita."""

    ENTRADAS = ("Renato", "Lucas", "0", "0", "1")

    @pytest.fixture
    def partida(self, executar_partida):
        return executar_partida(*self.ENTRADAS, maos=[(HUMANO_FORTE, BOT_FRACO)] * 2)

    def test_humano_vence_as_duas_rodadas(self, partida):
        assert partida.saida.count("Carta ganhadora: 1 de") == 2
        assert "Renato ganhou a rodada" in partida.saida

    def test_placar_e_atualizado(self, partida):
        assert "Pontuação Total" in partida.saida
        humano, bot = pontos(partida)
        assert humano > 0 and bot == 0

    def test_nova_mao_e_distribuida(self, partida):
        assert len(partida.estado["jogador1"].mao) == 3
        assert (partida.estado["jogador1"].rodadas, partida.estado["jogador2"].rodadas) == (0, 0)
        assert partida.estado["truco"].retornar_valor_aposta() == 1

    def test_mao_e_registrada_no_arquivo_de_jogadas(self, partida, tmp_path):
        assert len(pd.read_csv(tmp_path / "jogadas.csv")) == 1

    @pytest.mark.defeito("D05")
    @pytest.mark.xfail(reason="D05: o truco foi aceito, mas a mão é paga com 1 ponto")
    def test_mao_com_truco_aceito_vale_2_pontos(self, partida):
        assert pontos(partida) == (2, 0)


# ---------------------------------------------------------------- CT43 / UC09
@pytest.mark.requisito("CT43")
class TestFimDaPartida:
    @pytest.fixture
    def partida(self, executar_partida):
        # Renato vai ao baralho 12 vezes: o bot faz 1 ponto por mão
        return executar_partida("Renato", "Lucas", *["9"] * 12, maos=[(HUMANO_FORTE, BOT_FRACO)] * 13)

    def test_partida_termina_aos_12_pontos(self, partida):
        assert partida.erro is None                  # o laço principal terminou sozinho
        assert pontos(partida) == (0, 12)
        assert "Lucas ganhou o jogo" in partida.saida

    def test_laco_principal_roda_uma_vez_por_mao(self, partida, tmp_path):
        assert sum("Qual carta" in p for p in partida.perguntas) == 12
        assert len(pd.read_csv(tmp_path / "jogadas.csv")) == 12

    def test_nada_e_perguntado_depois_do_fim(self, partida):
        assert partida.saida.rstrip().endswith("Lucas ganhou o jogo")


# ---------------------------------------------------------------- UC03 / RF07
@pytest.mark.requisito("CT19")
def test_humano_pede_truco_e_bot_aumenta_para_retruco(executar_partida):
    partida = executar_partida("Renato", "Lucas", "4", "1",
                               maos=[(HUMANO_FORTE, BOT_FRACO)] * 2)
    assert "Truco" in partida.saida and "Retruco" in partida.saida
    resposta_ao_retruco = next(p for p in partida.perguntas if "você aceita" in p)
    assert "passa a valer 3 pontos" in resposta_ao_retruco
    assert partida.estado["truco"].retornar_valor_aposta() == 3


# ---------------------------------------------------------------- UC04 / RF07
@pytest.mark.requisito("CT20")
class TestHumanoRecusaTrucoDoBot:
    @pytest.fixture
    def partida(self, executar_partida):
        return executar_partida("Renato", "Lucas", "0", "0", "0",
                                maos=[(HUMANO_FORTE, BOT_FRACO)] * 2)

    def test_bot_ganha_1_ponto_e_nova_mao_comeca(self, partida):
        assert pontos(partida) == (0, 1)
        assert len(partida.estado["jogador1"].mao) == 3

    @pytest.mark.defeito("D26")
    @pytest.mark.xfail(reason="D26: quem recusou foi Renato, mas a tela diz 'Jogador Lucas fugiu!'")
    def test_tela_informa_quem_fugiu(self, partida):
        assert "Jogador Renato fugiu!" in partida.saida

    @pytest.mark.defeito("D12")
    @pytest.mark.xfail(reason="D12: a pergunta feita ao humano começa com '2, você aceita'")
    def test_pergunta_e_feita_ao_jogador_1(self, partida):
        pergunta = next(p for p in partida.perguntas if "você aceita" in p)
        assert pergunta.startswith("Jogador 1")


# ---------------------------------------------------------------- UC05 / RF09
@pytest.mark.requisito("CT12")
class TestBotPedeEnvidoNoInicio:
    @pytest.fixture
    def partida(self, executar_partida):
        return executar_partida("Renato", "Lucas", "1", maos=[(HUMANO_ENVIDO_7, BOT_ENVIDO_33)] * 2)

    def test_bot_com_33_pontos_pede_e_vence_o_envido(self, partida):
        assert "você aceita o pedido de envido" in partida.perguntas[2]
        assert pontos(partida) == (0, 2)
        assert "Jogador 2 Vencedor Envido" in partida.saida

    def test_partida_continua_depois_do_envido(self, partida):
        assert isinstance(partida.erro, EntradasEsgotadas)
        assert "Qual carta" in partida.perguntas[-1]

    @pytest.mark.defeito("D12")
    @pytest.mark.xfail(reason="D12: a pergunta feita ao humano diz 'Jogador 2, você aceita o pedido de envido?'")
    def test_pergunta_e_feita_ao_jogador_1(self, partida):
        assert partida.perguntas[2].startswith("Jogador 1")
