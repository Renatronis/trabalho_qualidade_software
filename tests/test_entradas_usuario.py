"""
Etapa 5 - Entradas do usuário na tela principal do jogo.

Casos de teste: CT31 a CT34 (defeitos D09 e D25).
Requisitos: RF08 (ir ao baralho), RF14 (opções), RF15 (entrada inválida não
encerra o jogo), UC01 (nomes dos jogadores), RF18 (registro da mão).

Cada teste roda o jogo de verdade (truco/__main__.py) com o teclado simulado
e mãos fixas, e confere a tela, as perguntas e o estado final.
"""
import pandas as pd
import pytest

from conftest import EntradasEsgotadas

pytestmark = [pytest.mark.entrada, pytest.mark.cenario, pytest.mark.lento]

HUMANO = ["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"]
BOT = ["12 de OUROS", "11 de BASTOS", "4 de COPAS"]   # envido 4: o bot não pede envido
MAOS = [(HUMANO, BOT)] * 3
PERGUNTA_CARTA = "Qual carta você quer jogar?"


def jogar(executar_partida, *entradas):
    return executar_partida("Renato", "Lucas", *entradas, maos=MAOS)


def cartas_na_mao(partida, jogador="jogador1"):
    return [c.retornar_carta() for c in partida.estado[jogador].mao]


# ---------------------------------------------------------------- CT31 / RF15
@pytest.mark.requisito("CT31")
@pytest.mark.defeito("D09")
@pytest.mark.xfail(reason="D09: int(input()) sem tratamento; texto na escolha da carta encerra o jogo com ValueError")
@pytest.mark.parametrize("texto", ["a", "1.5", ""], ids=["letra", "decimal", "vazio"])
def test_texto_na_escolha_da_carta_pede_de_novo(executar_partida, texto):
    partida = jogar(executar_partida, texto, "0")
    assert isinstance(partida.erro, EntradasEsgotadas)  # o jogo continuou até acabar as entradas
    assert "Selecione um valor válido!" in partida.saida
    assert "Renato jogou a carta: 1 de ESPADAS" in partida.saida


# ---------------------------------------------------------------- CT32 / RF15
@pytest.mark.requisito("CT32")
class TestIndiceForaDaMao:
    @pytest.mark.parametrize("invalidas", [["-1"], ["5"], ["12"], ["-1", "5", "12"]],
                             ids=["menos-1", "5-sem-flor", "12", "tres-seguidas"])
    def test_opcao_inexistente_avisa_e_pergunta_de_novo(self, executar_partida, invalidas):
        partida = jogar(executar_partida, *invalidas, "0")
        assert partida.saida.count("Selecione um valor válido!") == len(invalidas)
        perguntas_de_carta = partida.perguntas[2:]  # as duas primeiras são os nomes
        assert all(PERGUNTA_CARTA in p for p in perguntas_de_carta[:len(invalidas) + 1])
        assert "Renato jogou a carta: 1 de ESPADAS" in partida.saida

    @pytest.mark.defeito("D25")
    @pytest.mark.xfail(reason="D25: o teste usa <= len(mão); o índice igual ao número de cartas dá IndexError")
    @pytest.mark.parametrize("entradas", [["3"], ["0", "2"]], ids=["3-com-3-cartas", "2-com-2-cartas"])
    def test_indice_igual_ao_numero_de_cartas(self, executar_partida, entradas):
        partida = jogar(executar_partida, *entradas, "0")
        assert not isinstance(partida.erro, IndexError)
        assert "Selecione um valor válido!" in partida.saida


# ---------------------------------------------------------------- CT33 / RF08
@pytest.mark.requisito("CT33")
class TestIrAoBaralho:
    def test_no_inicio_da_mao(self, executar_partida, tmp_path):
        partida = jogar(executar_partida, "9")
        assert (partida.estado["jogador1"].pontos, partida.estado["jogador2"].pontos) == (0, 1)
        assert "Jogador Renato fugiu!" in partida.saida
        assert "Pontuação Total" in partida.saida
        # nova mão distribuída e registrada (RF18)
        assert len(partida.estado["jogador1"].mao) == 3
        assert partida.estado["jogador1"].rodadas == 0
        assert len(pd.read_csv(tmp_path / "jogadas.csv")) == 1

    def test_depois_de_vencer_a_primeira_rodada(self, executar_partida):
        partida = jogar(executar_partida, "0", "9")
        assert partida.estado["jogador2"].pontos == 1
        assert len(partida.estado["jogador1"].mao) == 3   # mão nova

    def test_opcao_aparece_na_tela(self, executar_partida):
        assert "[9] Ir ao baralho" in jogar(executar_partida).saida


# ---------------------------------------------------------------- CT34 / UC01
@pytest.mark.requisito("CT34")
@pytest.mark.parametrize("nome_humano, nome_bot", [
    ("Renato", "Lucas"), ("", ""), ("Renato Marquioro", "Bot 2000")],
    ids=["nomes-comuns", "nomes-vazios", "com-espaco-e-numero"])
def test_nomes_dos_jogadores(executar_partida, nome_humano, nome_bot):
    partida = executar_partida(nome_humano, nome_bot, "0", maos=MAOS)
    assert partida.perguntas[:2] == ["Nome Jogador 1: ", "Nome Jogador 2 (Bot): "]
    assert isinstance(partida.erro, EntradasEsgotadas)          # o jogo seguiu normalmente
    assert f"<< {nome_humano} - Jogador 1 >>" in partida.saida
    assert f"{nome_humano} jogou a carta: 1 de ESPADAS" in partida.saida
    assert f"<< {nome_bot} - Jogador 2 >>" in partida.saida
    assert partida.estado["jogador1"].nome == nome_humano and partida.estado["jogador2"].nome == nome_bot


@pytest.mark.requisito("CT34")
def test_tela_inicial_mostra_cartas_e_opcoes(executar_partida):
    partida = jogar(executar_partida)
    for texto in ("[0] 1 de ESPADAS", "[1] 1 de BASTOS", "[2] 3 de COPAS", "[4] Truco",
                  "[6] Envido", "[7] Real Envido", "[8] Falta Envido", "[9] Ir ao baralho"):
        assert texto in partida.saida
