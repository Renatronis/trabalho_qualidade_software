"""
Baralho e cartas.

Casos de teste: CT01, CT02, CT03, CT05, CT06 (defeito D08).
Requisitos: RF01 (baralho espanhol de 40 cartas), RF02 (distribuição),
RF03 (força das cartas).
"""
import random
from collections import Counter

import pytest

from truco.baralho import Baralho
from truco.carta import Carta
from truco.jogo import Jogo

NAIPES = ["ESPADAS", "OUROS", "COPAS", "BASTOS"]
NUMEROS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

# Tabela escrita a partir do README, sem importar truco/pontos.py (oráculo independente)
MANILHAS = {"1 de ESPADAS": 52, "1 de BASTOS": 50, "7 de ESPADAS": 42, "7 de OUROS": 40}
PONTOS_COMUNS = {3: 24, 2: 16, 1: 12, 12: 8, 11: 7, 10: 6, 7: 4, 6: 3, 5: 2, 4: 1}


@pytest.mark.requisito("CT01")
def test_CT01_baralho_tem_40_cartas_10_por_naipe_sem_repeticao():
    cartas = Baralho().cartas
    assert len(cartas) == 40
    assert Counter(c.retornar_naipe() for c in cartas) == {naipe: 10 for naipe in NAIPES}
    assert len({c.retornar_carta() for c in cartas}) == 40


@pytest.mark.requisito("CT01")
def test_CT01_limites_do_laco_que_cria_o_baralho():
    """Laço 'for n in range(1, 13)' com 'if n < 8 or n >= 10': conferimos o início,
    o fim e as bordas do intervalo excluído."""
    numeros = {c.retornar_numero() for c in Baralho().cartas}
    assert {1, 7, 10, 12} <= numeros       # início, antes e depois do buraco, fim
    assert not {8, 9, 13} & numeros         # excluídos e fora do range
    assert sorted(numeros) == NUMEROS


@pytest.mark.requisito("CT02")
@pytest.mark.requisito("CT03")
def test_CT02_CT03_distribuicao_e_embaralhamento():
    baralho = Baralho()
    antes = sorted(c.retornar_carta() for c in baralho.cartas)
    random.seed(1)
    baralho.embaralhar()
    ordem_1 = [c.retornar_carta() for c in baralho.cartas]
    assert sorted(ordem_1) == antes          # embaralhar não perde nem cria cartas

    random.seed(2)
    outro = Baralho()
    outro.embaralhar()
    assert [c.retornar_carta() for c in outro.cartas] != ordem_1   # sementes diferentes, ordens diferentes

    jogo = Jogo()
    humano = jogo.criar_jogador("Renato", baralho)
    bot = jogo.criar_bot("Lucas", baralho)
    assert len(humano.mao) == len(bot.mao) == 3
    assert len(baralho.cartas) == 34
    dadas = {c.retornar_carta() for c in humano.mao + bot.mao}
    assert len(dadas) == 6 and not dadas & {c.retornar_carta() for c in baralho.cartas}


@pytest.mark.requisito("CT05")
def test_CT05_pontos_e_ordem_de_forca_das_40_cartas():
    for naipe in NAIPES:
        for numero in NUMEROS:
            carta = Carta(numero, naipe)
            esperado = MANILHAS.get(carta.retornar_carta(), PONTOS_COMUNS[numero])
            assert carta.retornar_pontos_carta(carta) == esperado, carta.retornar_carta()

    ordem_readme = [4, 5, 6, 7, 10, 11, 12, 1, 2, 3]
    pontos = [PONTOS_COMUNS[n] for n in ordem_readme]
    assert pontos == sorted(pontos)
    assert min(MANILHAS.values()) > max(PONTOS_COMUNS.values())


@pytest.mark.requisito("CT06")
def test_CT06_classificar_mao_em_alta_media_e_baixa(nova_mao):
    casos = [
        (["1 de ESPADAS", "3 de COPAS", "4 de OUROS"], [52, 24, 1], ["Alta", "Media", "Baixa"]),
        (["7 de OUROS", "7 de COPAS", "12 de BASTOS"], [40, 4, 8], ["Alta", "Baixa", "Media"]),
        (["7 de ESPADAS", "1 de BASTOS", "5 de COPAS"], [42, 50, 2], ["Media", "Alta", "Baixa"]),
    ]
    for textos, pontos, ranks in casos:
        cartas = nova_mao(*textos)
        assert cartas[0].classificar_carta(cartas) == (pontos, ranks), textos


@pytest.mark.requisito("CT06")
@pytest.mark.defeito("D08")
@pytest.mark.xfail(raises=ValueError,
                   reason="D08: com três cartas de mesma força a mesma carta é 'Alta' e 'Baixa', "
                          "e o bot quebra ao calcular a qualidade da mão")
def test_D08_bot_recebe_tres_cartas_de_mesma_forca(bot_com_mao):
    bot = bot_com_mao("12 de COPAS", "12 de OUROS", "12 de BASTOS")
    assert sorted(bot.mao_rank) == ["Alta", "Baixa", "Media"]
