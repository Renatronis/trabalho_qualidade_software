"""Cenários de partida com mãos fixas (CT11, CT12, CT42 e CT43; D07)."""
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


# Simula uma vitória do humano e verifica o placar, a nova mão e o CSV.
@pytest.mark.requisito("CT42")
def test_CT42_mao_completa_vencida_pelo_humano(executar_partida, tmp_path):
    partida = executar_partida("Renato", "Lucas", "0", "0", "1",
                               maos=[(HUMANO_FORTE, BOT_FRACO)] * 2)
    assert partida.saida.count("Carta ganhadora: 1 de") == 2
    assert "Renato ganhou a rodada" in partida.saida
    assert "Pontuação Total" in partida.saida
    humano, bot = pontos(partida)
    assert humano > 0 and bot == 0
    assert len(partida.estado["jogador1"].mao) == 3
    assert len(pd.read_csv(tmp_path / "jogadas.csv")) == 1


# Confere se a partida termina quando o bot alcança 12 pontos.
@pytest.mark.requisito("CT43")
def test_CT43_partida_termina_aos_12_pontos(executar_partida):
    partida = executar_partida("Renato", "Lucas", *["9"] * 12,
                               maos=[(HUMANO_FORTE, BOT_FRACO)] * 13)
    assert partida.erro is None
    assert pontos(partida) == (0, 12)
    assert sum("Qual carta" in p for p in partida.perguntas) == 12
    assert partida.saida.rstrip().endswith("Lucas ganhou o jogo")


# Simula o bot pedindo Envido no início da partida e vencendo a aposta.
@pytest.mark.requisito("CT12")
def test_UC05_bot_pede_envido_no_inicio_e_vence(executar_partida):
    partida = executar_partida("Renato", "Lucas", "1", maos=[(HUMANO_ENVIDO_7, BOT_ENVIDO_33)] * 2)
    assert "você aceita o pedido de envido" in partida.perguntas[2]
    assert pontos(partida) == (0, 2)
    assert "Jogador 2 Vencedor Envido" in partida.saida
    assert isinstance(partida.erro, EntradasEsgotadas)
    assert "Qual carta" in partida.perguntas[-1]


# Confere se a pergunta de aceitação do Envido é dirigida ao humano.
@pytest.mark.requisito("CT11")
@pytest.mark.defeito("D07")
@pytest.mark.xfail(reason="D07: a pergunta feita ao humano diz 'Jogador 2, você aceita o pedido de envido?'")
def test_D07_pergunta_do_envido_e_feita_ao_jogador_1(executar_partida):
    partida = executar_partida("Renato", "Lucas", "1", maos=[(HUMANO_ENVIDO_7, BOT_ENVIDO_33)] * 2)
    assert partida.perguntas[2].startswith("Jogador 1")


# Mão decidida na terceira rodada: o humano vence a 1ª, perde a 2ª e vence a 3ª.
@pytest.mark.requisito("CT42")
def test_CT42_mao_decidida_na_terceira_rodada(executar_partida):
    humano = ["1 de ESPADAS", "4 de OUROS", "1 de BASTOS"]
    bot = ["3 de OUROS", "12 de COPAS", "2 de BASTOS"]
    partida = executar_partida("Renato", "Lucas", "0", "0", "1", "0", maos=[(humano, bot)] * 2)
    assert partida.saida.count("Carta ganhadora:") == 3
    assert "Carta ganhadora: 2 de BASTOS" in partida.saida          # o bot vence a 2ª rodada
    assert "Renato ganhou a rodada" in partida.saida
    assert pontos(partida) == (1, 0)


# O bot vence a mão jogando cartas e começa a mão seguinte.
@pytest.mark.requisito("CT42")
@pytest.mark.requisito("CT09")
def test_CT42_bot_vence_a_mao_e_comeca_a_seguinte(executar_partida):
    humano = ["4 de COPAS", "5 de OUROS", "6 de BASTOS"]
    partida = executar_partida("Renato", "Lucas", "0", "1", "0",
                               maos=[(humano, HUMANO_FORTE), (humano, BOT_FRACO)])
    assert "Lucas ganhou a rodada" in partida.saida
    humano_pts, bot_pts = pontos(partida)
    assert humano_pts == 0 and bot_pts > 0
    assert partida.estado["jogador2"].primeiro is True
    assert len(partida.estado["jogador2"].mao) == 2                 # na mão nova, o bot já jogou


# O humano vence 12 mãos seguidas e ganha a partida.
@pytest.mark.requisito("CT43")
def test_CT43_humano_vence_a_partida(executar_partida):
    partida = executar_partida("Renato", "Lucas", *["0", "0", "1"] * 12,
                               maos=[(HUMANO_FORTE, BOT_FRACO)] * 13)
    assert partida.erro is None
    assert pontos(partida) == (12, 0)
    assert partida.saida.rstrip().endswith("Renato ganhou o jogo")
