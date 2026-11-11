"""
Rodadas: vencedor de cada rodada e ordem de jogada.

Casos de teste: CT04, CT07 (defeito D02), CT08, CT09.
Requisitos: RF03 (força), RF04 (empate), RF05 (melhor de 3), RF06 (quem joga primeiro).
"""
import itertools

import pytest

from truco.carta import Carta
from truco.jogador import Jogador
from truco.jogo import Jogo

NAIPES = ["ESPADAS", "OUROS", "COPAS", "BASTOS"]
NUMEROS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
ORDEM_COMUM = [4, 5, 6, 7, 10, 11, 12, 1, 2, 3]
ORDEM_MANILHAS = ["7 de OUROS", "7 de ESPADAS", "1 de BASTOS", "1 de ESPADAS"]


def forca(carta):
    """Força da carta segundo o README (independente do código do jogo)."""
    nome = carta.retornar_carta()
    if nome in ORDEM_MANILHAS:
        return 100 + ORDEM_MANILHAS.index(nome)
    return ORDEM_COMUM.index(carta.retornar_numero())


@pytest.mark.requisito("CT04")
def test_CT04_carta_mais_forte_vence_nos_1560_confrontos():
    """Percorre todos os pares ordenados de cartas de força diferente:
    manilha x manilha, manilha x comum, comum x manilha e comum x comum."""
    jogo = Jogo()
    baralho = [Carta(n, s) for s in NAIPES for n in NUMEROS]
    erros = []
    for carta_1, carta_2 in itertools.permutations(baralho, 2):
        if forca(carta_1) == forca(carta_2):
            continue
        esperada = carta_1 if forca(carta_1) > forca(carta_2) else carta_2
        if jogo.verificar_carta_vencedora(carta_1, carta_2) is not esperada:
            erros.append((carta_1.retornar_carta(), carta_2.retornar_carta()))
    assert erros == []


@pytest.mark.requisito("CT07")
@pytest.mark.defeito("D02")
@pytest.mark.xfail(reason="D02: cartas de mesma força não empatam; vence sempre a do jogador 1")
def test_D02_cartas_de_mesma_forca_empatam(nova_carta):
    carta_1, carta_2 = nova_carta("3 de COPAS"), nova_carta("3 de OUROS")
    assert Jogo().verificar_carta_vencedora(carta_1, carta_2) not in (carta_1, carta_2)


@pytest.mark.requisito("CT08")
def test_CT08_adicionar_rodada_retorna_o_vencedor():
    jogo = Jogo()
    carta_1, carta_2 = Carta(3, "COPAS"), Carta(4, "OUROS")
    humano, bot = Jogador("Renato"), Jogador("Lucas")

    assert jogo.adicionar_rodada(humano, bot, carta_1, carta_2, carta_1) == 1
    assert jogo.adicionar_rodada(humano, bot, carta_1, carta_2, carta_2) == 2
    assert jogo.adicionar_rodada(humano, bot, carta_1, carta_2, Carta(7, "COPAS")) == "Erro"
    assert (humano.rodadas, bot.rodadas) == (1, 1)   # o "Erro" não soma rodada a ninguém


@pytest.mark.requisito("CT09")
def test_CT09_vencedor_da_rodada_joga_primeiro():
    jogo = Jogo()
    carta_1, carta_2 = Carta(3, "COPAS"), Carta(4, "OUROS")
    humano, bot = Jogador("Renato"), Jogador("Lucas")

    jogo.quem_joga_primeiro(humano, bot, carta_1, carta_2, carta_2)
    assert (humano.primeiro, bot.primeiro) == (False, True)
    jogo.quem_joga_primeiro(humano, bot, carta_1, carta_2, carta_1)
    assert (humano.primeiro, bot.primeiro) == (True, False)
