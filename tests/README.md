# Testes automatizados – Truco Gaudério com CBR

Trabalho de Qualidade de Software 2026/02, feito por Renato e Lucas.

## Instalação (ambiente virtual .venv)

O jeito mais fácil é dar um duplo clique em `configurar_ambiente.bat`, na raiz do projeto.
O script cria o `.venv`, instala as dependências e roda os testes.

Para fazer manualmente no Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-test.txt
```

No Linux ou Mac, o comando de ativação é `source .venv/bin/activate`. Com o ambiente ativado, o
terminal mostra `(.venv)` no início da linha, e todos os comandos abaixo usam o Python do `.venv`.

## Como rodar (sempre a partir da raiz do projeto)

| Comando | O que faz |
| --- | --- |
| `pytest` | Roda todos os testes |
| `pytest -v` | Mostra o resultado de cada teste |
| `pytest -m ia` | Roda só os testes da IA (CBR) |
| `pytest -m entrada` | Roda só os testes de entrada do usuário |
| `pytest -m cenario` | Roda só os cenários de uso (partida completa) |
| `pytest -m defeito` | Roda só os testes que comprovam defeitos |
| `pytest -m "not lento"` | Pula os testes que carregam a base de casos |
| `pytest --cov=truco --cov-report=html` | Gera o relatório de cobertura em `htmlcov/index.html` |

## Como ler o resultado

- **PASSED**: o jogo se comportou como o requisito exige.
- **XFAIL**: o teste comprova um **defeito do jogo**. O motivo e o código do
  defeito (D01, D02, ...) aparecem no resumo. Seguimos a regra de testar o jogo
  sem corrigir o código.
- **FAILED / XPASS**: algo mudou e precisa ser analisado.

## Observação sobre o defeito D01

A base de casos `dbtrucoimitacao_maos.csv` é separada por tabulação, mas o jogo
a lê como CSV de vírgula, por isso `python -m truco` falha ao iniciar. Os testes
contornam isso com um adaptador de leitura em `tests/conftest.py`, sem alterar o
código do jogo. O teste `test_D01_...` comprova o defeito.
