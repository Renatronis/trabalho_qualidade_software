"""
Configuração compartilhada dos testes do Truco Gaudério com CBR.

Trabalho de Qualidade de Software 2026/02 - Renato e Lucas.

Este arquivo é carregado automaticamente pelo PyTest e oferece as "fixtures"
(peças reutilizáveis) usadas por todos os testes:

    nova_carta / nova_mao       -> cria cartas a partir de texto ("1 de ESPADAS")
    baralho_fixo                -> baralho com ordem de cartas conhecida
    jogador_com_mao / bot_com_mao -> jogador e bot com mãos definidas pelo teste
    entradas_usuario            -> simula o que o usuário digita no input()
    CbrFalsa / cbr_falsa        -> IA "dublê", com respostas controladas pelo teste
    cbr_real                    -> a IA verdadeira, com a base de casos completa
    executar_partida            -> roda o jogo inteiro (truco/__main__.py)

Regra do trabalho: o código do jogo NÃO é alterado. Tudo o que é preciso para
testá-lo fica aqui, do lado dos testes.
"""
import builtins
import os
import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from truco.baralho import Baralho  # noqa: E402
from truco.bot import Bot  # noqa: E402
from truco.carta import Carta  # noqa: E402
from truco.interface import Interface  # noqa: E402
from truco.jogador import Jogador  # noqa: E402

ARQUIVO_BASE_CASOS = RAIZ / "dbtrucoimitacao_maos.csv"


# ---------------------------------------------------------------------------
# Adaptador de leitura de CSV (contorno do defeito D01)
# ---------------------------------------------------------------------------
_read_csv_original = pd.read_csv


def read_csv_compativel(caminho, *args, **kwargs):
    """Substituto de pandas.read_csv usado apenas durante os testes.

    Defeito D01: a base de casos 'dbtrucoimitacao_maos.csv' é separada por
    TABULAÇÃO, mas truco/dados.py a lê com o separador padrão (vírgula). Sem
    este adaptador o jogo nem inicia (ValueError: Usecols do not match columns).

    O adaptador faz duas coisas, sem mudar o código do jogo:
      1. detecta o separador (tabulação ou vírgula) pela primeira linha;
      2. se o caminho relativo não existir na pasta atual, procura na raiz do
         projeto. Assim os testes podem rodar numa pasta temporária e o
         arquivo 'jogadas.csv' gravado pelo jogo não suja o projeto.
    """
    caminho_real = Path(caminho)
    if not caminho_real.is_absolute() and not caminho_real.exists():
        caminho_real = RAIZ / caminho_real
    if "sep" not in kwargs and "delimiter" not in kwargs:
        with open(caminho_real, encoding="utf-8") as arquivo:
            kwargs["sep"] = "\t" if "\t" in arquivo.readline() else ","
    return _read_csv_original(caminho_real, *args, **kwargs)


@pytest.fixture(autouse=True)
def ambiente_do_jogo(request, monkeypatch, tmp_path):
    """Executada antes de TODOS os testes.

    - Testes comuns rodam numa pasta temporária, com o adaptador de CSV ativo.
    - Testes marcados com @pytest.mark.sem_adaptador rodam na raiz do projeto
      com o pandas original, exatamente como o usuário executaria o jogo.
    """
    if request.node.get_closest_marker("sem_adaptador"):
        monkeypatch.chdir(RAIZ)
    else:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(pd, "read_csv", read_csv_compativel)
    yield


# ---------------------------------------------------------------------------
# Cartas, mãos e baralho
# ---------------------------------------------------------------------------
def criar_carta(texto):
    """'1 de ESPADAS' -> Carta(1, 'ESPADAS')."""
    numero, naipe = texto.split(" de ")
    return Carta(int(numero), naipe.strip().upper())


@pytest.fixture
def nova_carta():
    """Fábrica de cartas: nova_carta('7 de OUROS')."""
    return criar_carta


@pytest.fixture
def nova_mao():
    """Fábrica de mãos: nova_mao('1 de ESPADAS', '3 de COPAS', '4 de OUROS')."""
    def _fabrica(*textos):
        return [criar_carta(t) for t in textos]
    return _fabrica


class BaralhoFixo(Baralho):
    """Baralho cujas cartas saem exatamente na ordem informada.

    retirar_carta() usa pop() (tira do fim da lista); por isso a ordem é
    invertida ao montar o baralho.
    """

    def __init__(self, textos):
        super().__init__()
        self.cartas = [criar_carta(t) for t in reversed(textos)]


@pytest.fixture
def baralho_fixo():
    """Fábrica: baralho_fixo(['1 de ESPADAS', '3 de COPAS', ...])."""
    return BaralhoFixo


@pytest.fixture
def jogador_com_mao():
    """Fábrica: jogador humano com a mão escolhida pelo teste."""
    def _fabrica(*textos, nome="Renato"):
        jogador = Jogador(nome)
        jogador.criar_mao(BaralhoFixo(list(textos)))
        return jogador
    return _fabrica


@pytest.fixture
def bot_com_mao():
    """Fábrica: bot com a mão escolhida pelo teste (já calcula envido, flor e qualidade)."""
    def _fabrica(*textos, nome="Bot"):
        bot = Bot(nome)
        bot.criar_mao(BaralhoFixo(list(textos)))
        return bot
    return _fabrica


@pytest.fixture
def interface():
    return Interface()


# ---------------------------------------------------------------------------
# Entradas do usuário (input simulado)
# ---------------------------------------------------------------------------
class EntradasEsgotadas(Exception):
    """O jogo pediu mais entradas do que o teste forneceu."""


@pytest.fixture
def entradas_usuario(monkeypatch):
    """Simula o teclado.

    Uso:
        registro = entradas_usuario("Renato", "Bot", "0")
        ... código que chama input() ...
        registro.perguntas  -> textos exibidos por cada input()
        registro.restantes  -> entradas não consumidas

    Se o código pedir mais entradas do que as fornecidas, lança
    EntradasEsgotadas (útil para detectar laços infinitos de validação).
    """
    def _definir(*respostas):
        registro = SimpleNamespace(perguntas=[], restantes=[str(r) for r in respostas])

        def input_falso(prompt=""):
            registro.perguntas.append(str(prompt))
            if not registro.restantes:
                raise EntradasEsgotadas(f"Sem mais entradas. Última pergunta: {prompt!r}")
            return registro.restantes.pop(0)

        monkeypatch.setattr(builtins, "input", input_falso)
        return registro

    return _definir


# ---------------------------------------------------------------------------
# Inteligência artificial
# ---------------------------------------------------------------------------
class CbrFalsa:
    """Dublê da classe Cbr: devolve respostas fixas e registra as chamadas.

    Permite testar Truco, Envido, Flor e Bot sem depender da base de casos.
    """

    def __init__(self, truco=1, envido=1, jogar_carta=0, flor=False):
        self.resposta_truco = truco
        self.resposta_envido = envido
        self.resposta_jogar_carta = jogar_carta
        self.resposta_flor = flor
        self.chamadas = []

    def _proxima(self, valor):
        # Aceita um valor fixo ou uma lista de valores (um por chamada)
        if isinstance(valor, list):
            return valor.pop(0)
        return valor

    def truco(self, tipo, quem_pediu, qualidade_mao_bot):
        self.chamadas.append(("truco", tipo, quem_pediu, qualidade_mao_bot))
        return self._proxima(self.resposta_truco)

    def envido(self, tipo, quem_pediu, pontos_envido_robo, robo_perdendo=None):
        self.chamadas.append(("envido", tipo, quem_pediu, pontos_envido_robo, robo_perdendo))
        return self._proxima(self.resposta_envido)

    def jogar_carta(self, rodada, pontuacao_cartas):
        self.chamadas.append(("jogar_carta", rodada, list(pontuacao_cartas)))
        return self._proxima(self.resposta_jogar_carta)

    def flor(self):
        self.chamadas.append(("flor",))
        return self._proxima(self.resposta_flor)


@pytest.fixture
def cbr_falsa():
    """Fábrica: cbr_falsa(truco=2, envido=0, ...)."""
    return CbrFalsa


@pytest.fixture(scope="session")
def _cbr_carregada():
    """Carrega a IA verdadeira uma única vez por execução (leva alguns segundos)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pd, "read_csv", read_csv_compativel)
        mp.chdir(RAIZ)
        from truco.cbr import Cbr
        return Cbr()


@pytest.fixture
def cbr_real(_cbr_carregada):
    """IA verdadeira, com o registro do caso atual zerado antes de cada teste."""
    _cbr_carregada.dados.registro = _cbr_carregada.dados.carregar_modelo_zerado()
    return _cbr_carregada


# ---------------------------------------------------------------------------
# Partida completa (cenários de uso)
# ---------------------------------------------------------------------------
@pytest.fixture
def executar_partida(entradas_usuario, monkeypatch, capsys):
    """Executa truco/__main__.py como se fosse 'python -m truco'.

    Parâmetros:
        respostas : tudo o que o usuário digita, em ordem
        seed      : semente do embaralhamento (partida reproduzível)
        maos      : lista de pares (cartas_jogador1, cartas_bot) para fixar as
                    mãos de cada "mão" da partida, na ordem em que são dadas

    Retorna um objeto com:
        saida     : tudo o que foi impresso na tela
        perguntas : textos de cada input()
        estado    : variáveis globais do jogo (jogador1, jogador2, truco...)
        erro      : exceção que interrompeu o jogo (None se terminou)
    """
    def _executar(*respostas, seed=0, maos=None):
        random.seed(seed)
        fila_maos = list(maos or [])
        embaralhar_original = Baralho.embaralhar

        def embaralhar_controlado(self):
            embaralhar_original(self)
            if fila_maos:
                cartas_j1, cartas_bot = fila_maos.pop(0)
                escolhidas = [criar_carta(t) for t in list(cartas_j1) + list(cartas_bot)]
                nomes = {c.retornar_carta() for c in escolhidas}
                resto = [c for c in self.cartas if c.retornar_carta() not in nomes]
                # pop() tira do fim: as escolhidas vão para o fim, em ordem invertida
                self.cartas = resto + list(reversed(escolhidas))

        monkeypatch.setattr(Baralho, "embaralhar", embaralhar_controlado)
        registro = entradas_usuario(*respostas)

        estado = {"__name__": "__main__", "__package__": "truco",
                  "__file__": str(RAIZ / "truco" / "__main__.py")}
        codigo = compile((RAIZ / "truco" / "__main__.py").read_text(encoding="utf-8"),
                         str(RAIZ / "truco" / "__main__.py"), "exec")
        erro = None
        try:
            exec(codigo, estado)
        except EntradasEsgotadas as e:
            erro = e
        except Exception as e:  # o teste decide se o erro era esperado
            erro = e
        return SimpleNamespace(saida=capsys.readouterr().out, perguntas=registro.perguntas,
                               estado=estado, erro=erro)

    return _executar
