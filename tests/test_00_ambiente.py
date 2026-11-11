"""Inicialização (CT44, RNF01) e regressão do D01."""
import importlib
import os
import subprocess
import sys

import pandas as pd
import pytest

from conftest import RAIZ

MODULOS = ["baralho", "bot", "carta", "cbr", "dados", "envido", "flor",
           "interface", "jogador", "jogo", "pontos", "truco"]


# Importa os módulos do jogo.
def test_todos_os_modulos_do_jogo_importam():
    for modulo in MODULOS:
        assert importlib.import_module(f"truco.{modulo}") is not None


# Confere se a base carrega sem o adaptador dos testes.
@pytest.mark.requisito("CT44")
@pytest.mark.sem_adaptador
def test_CT44_base_de_casos_carrega_sem_adaptador():
    assert pd.read_csv.__module__.startswith("pandas")
    from truco.dados import Dados
    casos = Dados().retornar_casos()
    assert len(casos) == 27515
    assert casos.isna().sum().sum() == 0


# Executa python -m truco e verifica se o jogo chega ao menu.
@pytest.mark.requisito("CT44")
@pytest.mark.sem_adaptador
@pytest.mark.lento
def test_CT44_python_m_truco_inicia():
    resultado = subprocess.run(
        [sys.executable, "-m", "truco"], cwd=RAIZ, input="Renato\nLucas\n",
        capture_output=True, text=True, encoding="utf-8", timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert "Nome Jogador 2 (Bot):" in resultado.stdout
    assert "[9] Ir ao baralho" in resultado.stdout
    # A entrada termina após os nomes, na primeira escolha de carta.
    assert resultado.stderr.strip().splitlines()[-1].startswith("EOFError")
