"""
Etapa 3 - Testes unitários de Baralho e Carta.

Casos de teste: CT01, CT02, CT03, CT05, CT06 (e defeito D08).
Requisitos: RF01 (baralho), RF02 (distribuição), RF03 (força das cartas).
"""
import random
from collections import Counter

import pytest

from truco.baralho import Baralho
from truco.bot import Bot
from truco.carta import Carta
from truco.jogo import Jogo

NAIPES = ["ESPADAS", "OUROS", "COPAS", "BASTOS"]
NUMEROS_VALIDOS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

# Tabela de pontos escrita a partir do README (independente de truco/pontos.py)
MANILHAS = {"1 de ESPADAS": 52, "1 de BASTOS": 50, "7 de ESPADAS": 42, "7 de OUROS": 40}
PONTOS_COMUNS = {3: 24, 2: 16, 1: 12, 12: 8, 11: 7, 10: 6, 7: 4, 6: 3, 5: 2, 4: 1}


def pontos_esperados(numero, naipe):
    return MANILHAS.get(f"{numero} de {naipe}", PONTOS_COMUNS[numero])


TODAS_AS_CARTAS = [(n, s) for s in NAIPES for n in NUMEROS_VALIDOS]


# ---------------------------------------------------------------- CT01 / RF01
@pytest.mark.requisito("CT01")
class TestCriacaoDoBaralho:
    def test_baralho_tem_40_cartas(self):
        assert len(Baralho().cartas) == 40

    def test_dez_cartas_por_naipe(self):
        contagem = Counter(c.retornar_naipe() for c in Baralho().cartas)
        assert contagem == {naipe: 10 for naipe in NAIPES}

    def test_nao_ha_cartas_repetidas(self):
        nomes = [c.retornar_carta() for c in Baralho().cartas]
        assert len(set(nomes)) == 40

    # Limites do laço "for n in range(1, 13): if n < 8 or n >= 10"
    @pytest.mark.parametrize("numero, presente", [
        (1, True),    # início do laço
        (7, True),    # último antes do intervalo excluído
        (8, False),   # primeiro excluído
        (9, False),   # último excluído
        (10, True),   # primeiro depois do intervalo
        (12, True),   # fim do laço
        (13, False),  # fora do range
    ])
    def test_limites_do_laco_de_numeros(self, numero, presente):
        numeros = {c.retornar_numero() for c in Baralho().cartas}
        assert (numero in numeros) is presente

    def test_resetar_e_recriar_volta_a_40_cartas(self):
        baralho = Baralho()
        baralho.retirar_carta()
        baralho.resetar()
        assert baralho.cartas == [] and baralho.manilhas == []
        baralho.criar_baralho()
        assert len(baralho.cartas) == 40


# ---------------------------------------------------------------- CT02 / RF02
@pytest.mark.requisito("CT02")
class TestDistribuicao:
    def test_cada_jogador_recebe_3_e_sobram_34(self):
        baralho = Baralho()
        baralho.embaralhar()
        jogo = Jogo()
        humano = jogo.criar_jogador("Renato", baralho)
        bot = jogo.criar_bot("Bot", baralho)
        assert len(humano.mao) == 3
        assert len(bot.mao) == 3
        assert len(baralho.cartas) == 34

    def test_cartas_distribuidas_saem_do_baralho(self):
        random.seed(5)
        baralho = Baralho()
        baralho.embaralhar()
        jogo = Jogo()
        dadas = jogo.criar_jogador("Renato", baralho).mao + jogo.criar_bot("Bot", baralho).mao
        restantes = {c.retornar_carta() for c in baralho.cartas}
        assert all(c.retornar_carta() not in restantes for c in dadas)
        assert len({c.retornar_carta() for c in dadas}) == 6

    def test_retirar_carta_devolve_a_ultima(self):
        baralho = Baralho()
        ultima = baralho.cartas[-1]
        assert baralho.retirar_carta() is ultima
        assert len(baralho.cartas) == 39

    def test_retirar_de_baralho_vazio_lanca_excecao(self):
        baralho = Baralho()
        baralho.resetar()
        with pytest.raises(IndexError):
            baralho.retirar_carta()


# ---------------------------------------------------------------- CT03 / RF02
@pytest.mark.requisito("CT03")
class TestEmbaralhar:
    def test_mantem_as_mesmas_cartas(self):
        baralho = Baralho()
        antes = sorted(c.retornar_carta() for c in baralho.cartas)
        baralho.embaralhar()
        assert sorted(c.retornar_carta() for c in baralho.cartas) == antes

    def test_sementes_diferentes_geram_ordens_diferentes(self):
        ordens = []
        for semente in (1, 2):
            random.seed(semente)
            baralho = Baralho()
            baralho.embaralhar()
            ordens.append([c.retornar_carta() for c in baralho.cartas])
        assert ordens[0] != ordens[1]

    def test_mesma_semente_gera_mesma_ordem(self):
        ordens = []
        for _ in range(2):
            random.seed(42)
            baralho = Baralho()
            baralho.embaralhar()
            ordens.append([c.retornar_carta() for c in baralho.cartas])
        assert ordens[0] == ordens[1]


# ---------------------------------------------------------------- CT05 / RF03
@pytest.mark.requisito("CT05")
@pytest.mark.parametrize("numero, naipe", TODAS_AS_CARTAS,
                         ids=[f"{n}-{s}" for n, s in TODAS_AS_CARTAS])
def test_pontos_de_cada_carta(numero, naipe):
    carta = Carta(numero, naipe)
    assert carta.retornar_pontos_carta(carta) == pontos_esperados(numero, naipe)


@pytest.mark.requisito("CT05")
def test_ordem_de_forca_das_cartas_comuns():
    ordem_readme = [4, 5, 6, 7, 10, 11, 12, 1, 2, 3]
    pontos = [Carta(n, "COPAS").retornar_pontos_carta(Carta(n, "COPAS")) for n in ordem_readme]
    assert pontos == sorted(pontos) and len(set(pontos)) == 10


@pytest.mark.requisito("CT05")
def test_manilhas_em_ordem_e_acima_de_todas():
    ordem = ["7 de OUROS", "7 de ESPADAS", "1 de BASTOS", "1 de ESPADAS"]
    pontos = []
    for texto in ordem:
        n, s = texto.split(" de ")
        carta = Carta(int(n), s)
        pontos.append(carta.retornar_pontos_carta(carta))
    assert pontos == sorted(pontos)
    assert min(pontos) > max(PONTOS_COMUNS.values())


# ---------------------------------------------------------------- CT06 / RF03
@pytest.mark.requisito("CT06")
@pytest.mark.parametrize("mao, pontos, ranks", [
    (["1 de ESPADAS", "3 de COPAS", "4 de OUROS"], [52, 24, 1], ["Alta", "Media", "Baixa"]),
    (["4 de OUROS", "3 de COPAS", "1 de ESPADAS"], [1, 24, 52], ["Baixa", "Media", "Alta"]),
    (["7 de OUROS", "7 de COPAS", "12 de BASTOS"], [40, 4, 8], ["Alta", "Baixa", "Media"]),
    (["7 de ESPADAS", "1 de BASTOS", "5 de COPAS"], [42, 50, 2], ["Media", "Alta", "Baixa"]),
    (["5 de COPAS", "5 de OUROS", "4 de BASTOS"], [2, 2, 1], ["Media", "Alta", "Baixa"]),
], ids=["manilha-primeiro", "manilha-ultimo", "manilha-e-figura", "duas-manilhas", "par-e-menor"])
def test_classificar_carta(nova_mao, mao, pontos, ranks):
    cartas = nova_mao(*mao)
    assert cartas[0].classificar_carta(cartas) == (pontos, ranks)


@pytest.mark.requisito("CT06")
@pytest.mark.defeito("D08")
@pytest.mark.xfail(reason="D08: com três cartas de mesma força a mesma carta é 'Alta' e 'Baixa'; não sobra 'Alta'")
def test_classificar_tres_cartas_de_mesma_forca(nova_mao):
    cartas = nova_mao("3 de COPAS", "3 de OUROS", "3 de BASTOS")
    _, ranks = cartas[0].classificar_carta(cartas)
    assert sorted(ranks) == ["Alta", "Baixa", "Media"]


@pytest.mark.requisito("CT06")
@pytest.mark.parametrize("a, b, alta, baixa", [
    ("1 de ESPADAS", "1 de BASTOS", "1 de ESPADAS", "1 de BASTOS"),  # manilha x manilha
    ("7 de OUROS", "7 de ESPADAS", "7 de ESPADAS", "7 de OUROS"),    # manilha x manilha (invertido)
    ("7 de OUROS", "3 de COPAS", "7 de OUROS", "3 de COPAS"),        # manilha x comum
    ("3 de COPAS", "1 de BASTOS", "1 de BASTOS", "3 de COPAS"),      # comum x manilha
    ("2 de COPAS", "12 de OUROS", "2 de COPAS", "12 de OUROS"),      # comum x comum
    ("4 de COPAS", "1 de OUROS", "1 de OUROS", "4 de COPAS"),        # 1 comum vale mais que 4
])
def test_verificar_carta_alta_e_baixa(nova_carta, a, b, alta, baixa):
    carta_a, carta_b = nova_carta(a), nova_carta(b)
    assert carta_a.verificar_carta_alta(carta_a, carta_b).retornar_carta() == alta
    assert carta_a.verificar_carta_baixa(carta_a, carta_b).retornar_carta() == baixa


@pytest.mark.defeito("D08")
@pytest.mark.xfail(raises=ValueError, reason="D08: bot com três cartas de mesma força quebra ao calcular a qualidade da mão")
def test_bot_recebe_tres_cartas_de_mesma_forca(bot_com_mao):
    bot = bot_com_mao("12 de COPAS", "12 de OUROS", "12 de BASTOS")
    assert bot.qualidade_mao > 0


# ------------------------------------------------ Outros retornos da Carta
@pytest.mark.parametrize("naipe, codigo", [
    ("ESPADAS", 1), ("OUROS", 2), ("BASTOS", 3), ("COPAS", 4), ("CURINGA", None)])
def test_naipe_codificado(naipe, codigo):
    assert Carta(1, naipe).retornar_naipe_codificado() == codigo


@pytest.mark.parametrize("numero, pontos", [
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (10, 0), (11, 0), (12, 0)])
def test_pontos_de_envido_por_carta(numero, pontos):
    carta = Carta(numero, "COPAS")
    assert carta.retornar_pontos_envido(carta) == pontos


def test_retornos_de_numero_naipe_e_texto():
    carta = Carta(11, "BASTOS")
    assert carta.retornar_numero() == 11
    assert carta.retornar_naipe() == "BASTOS"
    assert carta.retornar_carta() == "11 de BASTOS"


@pytest.mark.parametrize("indice, esperado", [(0, "[0] 3 de OUROS\n"), (None, "[] 3 de OUROS\n")])
def test_exibir_carta(capsys, indice, esperado):
    Carta(3, "OUROS").exibir_carta(indice)
    assert capsys.readouterr().out == esperado


def test_printar_baralho_mostra_40_linhas(capsys):
    Baralho().printar_baralho()
    assert len(capsys.readouterr().out.strip().splitlines()) == 40
