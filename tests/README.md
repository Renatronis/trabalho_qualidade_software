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

## Arquivos de teste

| Arquivo | Conteúdo |
| --- | --- |
| `test_00_ambiente.py` | Fumaça do ambiente e CT44 (`python -m truco` inicia) |
| `test_baralho_carta.py` | Baralho, distribuição e força das cartas (CT01 a CT06) |
| `test_jogo.py` | Vencedor da rodada e ordem de jogada (CT04 a CT09) |
| `test_envido.py` | Envido, incluindo o turno real do bot (CT10 a CT17) |
| `test_truco.py` | Truco, retruco e vale 4 (CT18 a CT23) |
| `test_jogador_bot.py` | Métodos do jogador e do bot (CT24) |
| `test_flor.py` | Flor e contraflor (CT25 a CT27) |
| `test_interface.py` | Opções e mensagens na tela (CT28 a CT30) |
| `test_entradas_usuario.py` | Entradas na tela principal (CT31 a CT34) |
| `test_cbr.py` | IA real: base de casos e decisões (CT35 a CT40) |
| `test_dados.py` | Registro de jogadas (CT41) |
| `test_cenarios.py` | Partidas completas (CT42, CT43 e cenários de truco e envido) |

## Defeito D01 (corrigido)

A base `dbtrucoimitacao_maos.csv` é separada por tabulação. O grupo corrigiu
`truco/dados.py` com `sep="\t"`, e os testes `test_CT44_*` comprovam a correção
sem nenhum adaptador: a base carrega e `python -m truco` abre o jogo.

O `conftest.py` ainda usa um adaptador de leitura, mas só para que os testes
rodem numa pasta temporária (o jogo grava `jogadas.csv` na pasta atual).
