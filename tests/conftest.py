"""Fixtures compartilhadas pelos testes do Truco Gaudério."""
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


_read_csv_original = pd.read_csv


def read_csv_compativel(caminho, *args, **kwargs):
    """Busca CSVs na raiz quando preciso e detecta o separador se ele não for informado."""
    caminho_real = Path(caminho)
    if not caminho_real.is_absolute() and not caminho_real.exists():
        caminho_real = RAIZ / caminho_real
    if "sep" not in kwargs and "delimiter" not in kwargs:
        with open(caminho_real, encoding="utf-8") as arquivo:
            kwargs["sep"] = "\t" if "\t" in arquivo.readline() else ","
    return _read_csv_original(caminho_real, *args, **kwargs)


@pytest.fixture(autouse=True)
def ambiente_do_jogo(request, monkeypatch, tmp_path):
    """Isola a gravação de jogadas.csv. Testes sem adaptador rodam na raiz."""
    if request.node.get_closest_marker("sem_adaptador"):
        monkeypatch.chdir(RAIZ)
    else:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(pd, "read_csv", read_csv_compativel)
    yield


def criar_carta(texto):
    numero, naipe = texto.split(" de ")
    return Carta(int(numero), naipe.strip().upper())


@pytest.fixture
def nova_carta():
    return criar_carta


@pytest.fixture
def nova_mao():
    def _fabrica(*textos):
        return [criar_carta(t) for t in textos]
    return _fabrica


class BaralhoFixo(Baralho):
    """Entrega as cartas na ordem informada, embora a retirada use pop()."""

    def __init__(self, textos):
        super().__init__()
        self.cartas = [criar_carta(t) for t in reversed(textos)]


@pytest.fixture
def baralho_fixo():
    return BaralhoFixo


@pytest.fixture
def jogador_com_mao():
    def _fabrica(*textos, nome="Renato"):
        jogador = Jogador(nome)
        jogador.criar_mao(BaralhoFixo(list(textos)))
        return jogador
    return _fabrica


@pytest.fixture
def bot_com_mao():
    def _fabrica(*textos, nome="Bot"):
        bot = Bot(nome)
        bot.criar_mao(BaralhoFixo(list(textos)))
        return bot
    return _fabrica


@pytest.fixture
def interface():
    return Interface()


class EntradasEsgotadas(Exception):
    """O jogo solicitou mais entradas que as fornecidas."""


@pytest.fixture
def entradas_usuario(monkeypatch):
    """Substitui input() por respostas fixas e registra as perguntas."""
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


class CbrFalsa:
    """Devolve respostas fixas ou em sequência e registra as chamadas."""

    def __init__(self, truco=1, envido=1, jogar_carta=0, flor=False):
        self.resposta_truco = truco
        self.resposta_envido = envido
        self.resposta_jogar_carta = jogar_carta
        self.resposta_flor = flor
        self.chamadas = []

    def _proxima(self, valor):
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
    return CbrFalsa


@pytest.fixture(scope="session")
def _cbr_carregada():
    """Carrega a CBR real uma vez por sessão."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pd, "read_csv", read_csv_compativel)
        mp.chdir(RAIZ)
        from truco.cbr import Cbr
        return Cbr()


@pytest.fixture
def cbr_real(_cbr_carregada):
    """Zera o registro da CBR real antes de cada teste que usa a fixture."""
    _cbr_carregada.dados.registro = _cbr_carregada.dados.carregar_modelo_zerado()
    return _cbr_carregada


@pytest.fixture
def executar_partida(entradas_usuario, monkeypatch, capsys, _cbr_carregada):
    """Roda o jogo com entradas e mãos controladas e retorna saída, perguntas, estado e erro."""
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
        # A IA verdadeira já carregada é reaproveitada (evita reler 14 MB por partida)
        _cbr_carregada.dados.registro = _cbr_carregada.dados.carregar_modelo_zerado()
        monkeypatch.setattr("truco.cbr.Cbr", lambda: _cbr_carregada)
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
        except Exception as e:
            erro = e
        return SimpleNamespace(saida=capsys.readouterr().out, perguntas=registro.perguntas,
                               estado=estado, erro=erro)

    return _executar
