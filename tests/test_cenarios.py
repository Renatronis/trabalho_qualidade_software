"""
Cenários de uso ponta a ponta (partida executada pelo __main__ com a IA verdadeira).

Casos de teste: CT42, CT43 e o cenário UC05 (defeito D12).
Com mãos fixas e o registro inicial a IA é determinística, então cada cenário
segue sempre o mesmo caminho.
"""
import pandas as pd
import pytest

from conftest import EntradasEsgotadas

pytestmark = [pytest.mark.cenario, pytest.mark.lento]

HUMANO_FORTE = ["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"]
BOT_FRACO = ["12 de OUROS", "11 de BASTOS", "4 de COPAS"]
HUMANO_ENVIDO_7 = ["7 de BASTOS", "5 de ESPADAS", "4 de OUROS"]
BOT_ENVIDO_33 = ["7 de COPAS", "6 de COPAS", "12 de ESPADAS"]


def pontos(partida):
    return partida.estado["jogador1"].pontos, partida.estado["jogador2"].pontos


@pytest.mark.requisito("CT42")
def test_CT42_mao_completa_vencida_pelo_humano(executar_partida, tmp_path):
    """Renato joga o 1 de Espadas e o 1 de Bastos; o bot pede truco na 2ª rodada e Renato aceita."""
    partida = executar_partida("Renato", "Lucas", "0", "0", "1",
                               maos=[(HUMANO_FORTE, BOT_FRACO)] * 2)
    assert partida.saida.count("Carta ganhadora: 1 de") == 2       # venceu as duas rodadas
    assert "Renato ganhou a rodada" in partida.saida
    assert "Pontuação Total" in partida.saida
    humano, bot = pontos(partida)
    assert humano > 0 and bot == 0
    assert len(partida.estado["jogador1"].mao) == 3                 # nova mão distribuída
    assert len(pd.read_csv(tmp_path / "jogadas.csv")) == 1          # mão registrada (RF18)


@pytest.mark.requisito("CT43")
def test_CT43_partida_termina_aos_12_pontos(executar_partida):
    """Renato vai ao baralho 12 vezes: o bot faz 1 ponto por mão e vence."""
    partida = executar_partida("Renato", "Lucas", *["9"] * 12,
                               maos=[(HUMANO_FORTE, BOT_FRACO)] * 13)
    assert partida.erro is None                                     # o laço principal terminou sozinho
    assert pontos(partida) == (0, 12)
    assert sum("Qual carta" in p for p in partida.perguntas) == 12   # uma volta do laço por mão
    assert partida.saida.rstrip().endswith("Lucas ganhou o jogo")


@pytest.mark.requisito("CT12")
def test_UC05_bot_pede_envido_no_inicio_e_vence(executar_partida):
    """O bot, com 33 pontos de envido, pede envido; Renato (7 pontos) aceita."""
    partida = executar_partida("Renato", "Lucas", "1", maos=[(HUMANO_ENVIDO_7, BOT_ENVIDO_33)] * 2)
    assert "você aceita o pedido de envido" in partida.perguntas[2]
    assert pontos(partida) == (0, 2)
    assert "Jogador 2 Vencedor Envido" in partida.saida
    assert isinstance(partida.erro, EntradasEsgotadas)              # a partida continua
    assert "Qual carta" in partida.perguntas[-1]


@pytest.mark.requisito("CT11")
@pytest.mark.defeito("D12")
@pytest.mark.xfail(reason="D12: a pergunta feita ao humano diz 'Jogador 2, você aceita o pedido de envido?'")
def test_D12_pergunta_do_envido_e_feita_ao_jogador_1(executar_partida):
    partida = executar_partida("Renato", "Lucas", "1", maos=[(HUMANO_ENVIDO_7, BOT_ENVIDO_33)] * 2)
    assert partida.perguntas[2].startswith("Jogador 1")
