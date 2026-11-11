"""
Etapa 3 - Testes unitários da classe Jogo (rodadas e vencedor da rodada).

Casos de teste: CT04, CT07, CT08, CT09.
Requisitos: RF03 (força), RF04 (empate), RF05 (melhor de 3), RF06 (quem joga primeiro).
"""
import itertools

import pytest

from truco.carta import Carta
from truco.jogador import Jogador
from truco.jogo import Jogo

NAIPES = ["ESPADAS", "OUROS", "COPAS", "BASTOS"]
NUMEROS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
ORDEM_COMUM = [4, 5, 6, 7, 10, 11, 12, 1, 2, 3]  # README, da menor para a maior
ORDEM_MANILHAS = ["7 de OUROS", "7 de ESPADAS", "1 de BASTOS", "1 de ESPADAS"]


def forca(carta):
    """Força da carta segundo o README (independente do código do jogo)."""
    nome = carta.retornar_carta()
    if nome in ORDEM_MANILHAS:
        return 100 + ORDEM_MANILHAS.index(nome)
    return ORDEM_COMUM.index(carta.retornar_numero())


BARALHO = [Carta(n, s) for s in NAIPES for n in NUMEROS]


@pytest.fixture
def jogo():
    return Jogo()


# ---------------------------------------------------------------- CT04 / RF03
@pytest.mark.requisito("CT04")
@pytest.mark.parametrize("texto_1, texto_2, vencedora", [
    # manilha x manilha
    ("1 de ESPADAS", "1 de BASTOS", 1),
    ("7 de OUROS", "7 de ESPADAS", 2),
    ("1 de BASTOS", "7 de ESPADAS", 1),
    # manilha x comum
    ("7 de OUROS", "3 de COPAS", 1),
    # comum x manilha
    ("3 de COPAS", "7 de OUROS", 2),
    # comum x comum
    ("3 de COPAS", "2 de OUROS", 1),
    ("4 de COPAS", "12 de OUROS", 2),
    ("1 de COPAS", "12 de BASTOS", 1),
    ("7 de COPAS", "10 de OUROS", 2),
], ids=["manilha-manilha-1", "manilha-manilha-2", "manilha-manilha-3", "manilha-comum",
        "comum-manilha", "comum-comum-1", "comum-comum-2", "comum-comum-3", "comum-comum-4"])
def test_carta_vencedora_exemplos(jogo, nova_carta, texto_1, texto_2, vencedora):
    carta_1, carta_2 = nova_carta(texto_1), nova_carta(texto_2)
    esperada = carta_1 if vencedora == 1 else carta_2
    assert jogo.verificar_carta_vencedora(carta_1, carta_2) is esperada


@pytest.mark.requisito("CT04")
def test_carta_vencedora_todos_os_pares_de_forca_diferente(jogo):
    """Percorre os 1.560 pares ordenados de cartas e confere cada vencedor."""
    erros = []
    for carta_1, carta_2 in itertools.permutations(BARALHO, 2):
        if forca(carta_1) == forca(carta_2):
            continue
        esperada = carta_1 if forca(carta_1) > forca(carta_2) else carta_2
        if jogo.verificar_carta_vencedora(carta_1, carta_2) is not esperada:
            erros.append((carta_1.retornar_carta(), carta_2.retornar_carta()))
    assert erros == []


def test_verificar_ganhador_mostra_carta_ganhadora(jogo, nova_carta, interface, capsys):
    carta_1, carta_2 = nova_carta("2 de COPAS"), nova_carta("1 de ESPADAS")
    assert jogo.verificar_ganhador(carta_1, carta_2, interface) is carta_2
    assert "Carta ganhadora: 1 de ESPADAS" in capsys.readouterr().out


# ---------------------------------------------------------------- CT07 / RF04
@pytest.mark.requisito("CT07")
@pytest.mark.defeito("D02")
@pytest.mark.xfail(reason="D02: cartas de mesma força não empatam; vence sempre a do jogador 1")
@pytest.mark.parametrize("texto_1, texto_2", [
    ("3 de COPAS", "3 de OUROS"),
    ("4 de BASTOS", "4 de ESPADAS"),
    ("12 de OUROS", "12 de COPAS"),
])
def test_cartas_de_mesma_forca_empatam(jogo, nova_carta, texto_1, texto_2):
    carta_1, carta_2 = nova_carta(texto_1), nova_carta(texto_2)
    assert jogo.verificar_carta_vencedora(carta_1, carta_2) not in (carta_1, carta_2)


# ---------------------------------------------------------------- CT08 / RF05
@pytest.mark.requisito("CT08")
class TestAdicionarRodada:
    def setup_method(self):
        self.jogo = Jogo()
        self.humano, self.bot = Jogador("Renato"), Jogador("Bot")
        self.carta_1, self.carta_2 = Carta(3, "COPAS"), Carta(4, "OUROS")

    def test_vitoria_do_jogador_1(self):
        resultado = self.jogo.adicionar_rodada(self.humano, self.bot, self.carta_1, self.carta_2, self.carta_1)
        assert resultado == 1
        assert (self.humano.rodadas, self.bot.rodadas) == (1, 0)

    def test_vitoria_do_jogador_2(self):
        resultado = self.jogo.adicionar_rodada(self.humano, self.bot, self.carta_1, self.carta_2, self.carta_2)
        assert resultado == 2
        assert (self.humano.rodadas, self.bot.rodadas) == (0, 1)

    def test_ganhador_invalido_retorna_erro(self):
        outra = Carta(7, "COPAS")
        resultado = self.jogo.adicionar_rodada(self.humano, self.bot, self.carta_1, self.carta_2, outra)
        assert resultado == "Erro"
        assert (self.humano.rodadas, self.bot.rodadas) == (0, 0)

    def test_duas_vitorias_fecham_a_mao(self):
        for _ in range(2):
            self.jogo.adicionar_rodada(self.humano, self.bot, self.carta_1, self.carta_2, self.carta_1)
        assert self.humano.rodadas == 2


# ---------------------------------------------------------------- CT09 / RF06
@pytest.mark.requisito("CT09")
@pytest.mark.parametrize("vencedor, primeiro_j1, primeiro_j2", [
    (1, True, False),
    (2, False, True),
    (None, "inalterado", "inalterado"),  # ganhador que não é nenhuma das cartas
])
def test_quem_joga_primeiro(jogo, vencedor, primeiro_j1, primeiro_j2):
    humano, bot = Jogador("Renato"), Jogador("Bot")
    humano.primeiro, bot.primeiro = "inalterado", "inalterado"
    carta_1, carta_2 = Carta(3, "COPAS"), Carta(4, "OUROS")
    ganhador = {1: carta_1, 2: carta_2, None: Carta(5, "COPAS")}[vencedor]
    jogo.quem_joga_primeiro(humano, bot, carta_1, carta_2, ganhador)
    assert (humano.primeiro, bot.primeiro) == (primeiro_j1, primeiro_j2)


@pytest.mark.parametrize("rodadas, ultimo, esperado_primeiro", [
    ((0, 0), "j1", ("j1",)),
    ((0, 0), "j2", ("j2",)),
    ((1, 0), "j1", ()),       # mão já começou: nada muda
])
def test_quem_inicia_rodada(jogo, rodadas, ultimo, esperado_primeiro):
    j1, j2 = Jogador("Renato"), Jogador("Bot")
    j1.rodadas, j2.rodadas = rodadas
    j1.ultimo, j2.ultimo = (ultimo == "j1"), (ultimo == "j2")
    jogo.quem_inicia_rodada(j1, j2)
    primeiros = tuple(nome for nome, j in (("j1", j1), ("j2", j2)) if j.primeiro)
    assert primeiros == esperado_primeiro


def test_criar_jogador_e_bot(jogo, baralho_fixo):
    baralho = baralho_fixo(["1 de ESPADAS", "2 de COPAS", "3 de OUROS",
                            "4 de BASTOS", "5 de COPAS", "6 de OUROS"])
    humano = jogo.criar_jogador("Renato", baralho)
    bot = jogo.criar_bot("Lucas", baralho)
    assert humano.nome == "Renato" and bot.nome == "Lucas"
    assert [c.retornar_carta() for c in humano.mao] == ["1 de ESPADAS", "2 de COPAS", "3 de OUROS"]
    assert [c.retornar_carta() for c in bot.mao] == ["4 de BASTOS", "5 de COPAS", "6 de OUROS"]


def test_jogador_fugiu_devolve_a_vez_ao_jogador_1(jogo, capsys):
    j1, j2 = Jogador("Renato"), Jogador("Bot")
    j1.primeiro, j2.primeiro = False, True
    jogo.jogador_fugiu(j2, j1, j2, -1)
    assert (j1.primeiro, j2.primeiro) == (True, False)
    assert "Jogador fugiu!" in capsys.readouterr().out
