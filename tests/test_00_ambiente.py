"""
Ambiente e inicialização do jogo.

Caso de teste: CT44 (RNF01: o jogo inicia com 'python -m truco').
O defeito D01 (base separada por tabulação lida com vírgula) foi corrigido
pelo grupo; estes testes comprovam a correção sem nenhum adaptador.
"""
import importlib
import os
import subprocess
import sys

import pandas as pd
import pytest

from conftest import RAIZ

MODULOS = ["baralho", "bot", "carta", "cbr", "dados", "envido", "flor",
           "interface", "jogador", "jogo", "pontos", "truco"]


def test_todos_os_modulos_do_jogo_importam():
    for modulo in MODULOS:
        assert importlib.import_module(f"truco.{modulo}") is not None


@pytest.mark.requisito("CT44")
@pytest.mark.sem_adaptador
def test_CT44_base_de_casos_carrega_sem_adaptador():
    """A base de casos carrega com o pandas original, a partir da raiz do projeto."""
    assert pd.read_csv.__module__.startswith("pandas")
    from truco.dados import Dados
    casos = Dados().retornar_casos()
    assert len(casos) == 27515
    assert casos.isna().sum().sum() == 0


@pytest.mark.requisito("CT44")
@pytest.mark.sem_adaptador
@pytest.mark.lento
def test_CT44_python_m_truco_inicia():
    """'python -m truco' abre o jogo, pede os nomes e mostra as cartas.

    Depois dos dois nomes a entrada acaba e o jogo para com EOFError na
    pergunta seguinte, o que mostra que ele chegou a iniciar.
    """
    resultado = subprocess.run(
        [sys.executable, "-m", "truco"], cwd=RAIZ, input="Renato\nLucas\n",
        capture_output=True, text=True, encoding="utf-8", timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert "Nome Jogador 2 (Bot):" in resultado.stdout
    assert "[9] Ir ao baralho" in resultado.stdout
    assert resultado.stderr.strip().splitlines()[-1].startswith("EOFError")
