# Testes automatizados – Truco Gaudério com CBR

Trabalho de Qualidade de Software 2026/02, feito por Renato e Lucas. A suíte atual tem **60 testes em 12 arquivos**. Na última execução, **50 passaram e 10 apresentaram falhas esperadas**.

## Instalação (ambiente virtual .venv)

No Windows, execute `configurar_ambiente.bat` na raiz do projeto para criar o ambiente virtual, instalar as dependências e rodar os testes.

Para fazer manualmente no Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements-test.txt
```

No Linux ou macOS, a partir da raiz do projeto, rode os comandos abaixo.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
```

## Como rodar (sempre a partir da raiz do projeto)

| Comando | O que faz |
| --- | --- |
| `python -m pytest -v` | Roda toda a suíte e mostra o resultado de cada teste |
| `python -m pytest -m ia -v` | Roda os testes da IA real (CBR) |
| `python -m pytest -m entrada -v` | Roda os testes com entradas do usuário |
| `python -m pytest -m cenario -v` | Roda os testes que exercitam o fluxo da partida |
| `python -m pytest -m defeito -v` | Roda os testes dos defeitos conhecidos |
| `python -m pytest -m "not lento"` | Pula os testes marcados como lentos |
| `python -m pytest --cov=truco --cov-report=term` | Mostra a cobertura de linhas no terminal |
| `python -m pytest --cov=truco --cov-report=html` | Gera o relatório de cobertura em `htmlcov/index.html` |

## Como ler o resultado

- **PASSED** indica que o resultado bateu com o esperado.
- **XFAIL** indica uma falha esperada associada a um defeito conhecido. O resumo mostra o código e o motivo, de D02 a D11.
- **FAILED** indica uma falha inesperada.
- **XPASS(strict)** indica que um teste marcado como falha esperada passou. A configuração do projeto faz a suíte sinalizar esse resultado como falha para revisão.

## Arquivos de teste

| Arquivo | Conteúdo |
| --- | --- |
| `test_00_ambiente.py` | Fumaça do ambiente e CT44 (`python -m truco` inicia) |
| `test_baralho_carta.py` | Baralho, distribuição e força das cartas (CT01 a CT03, CT05 e CT06) |
| `test_jogo.py` | Vencedor da rodada e ordem de jogada (CT04 e CT07 a CT09) |
| `test_envido.py` | Envido, incluindo o turno real do bot (CT10 a CT17) |
| `test_truco.py` | Truco, retruco e vale 4 (CT18 a CT23) |
| `test_jogador_bot.py` | Métodos do jogador e do bot (CT24) |
| `test_flor.py` | Flor e contraflor (CT25 a CT27) |
| `test_interface.py` | Opções e mensagens na tela (CT28 a CT30) |
| `test_entradas_usuario.py` | Entradas na tela principal (CT31 a CT34) |
| `test_cbr.py` | IA real: base de casos e decisões (CT35 a CT40) |
| `test_dados.py` | Registro de jogadas (CT41) |
| `test_cenarios.py` | Vitória em uma mão, fim da partida e pedido de Envido do bot (CT11, CT12, CT42 e CT43) |

## Defeito D01 (corrigido)

A base `dbtrucoimitacao_maos.csv` é separada por tabulação. O grupo corrigiu
`truco/dados.py` com `sep="\t"`, e os testes `test_CT44_*` comprovam a correção
sem nenhum adaptador: a base carrega e `python -m truco` abre o jogo.

O `conftest.py` ainda usa um adaptador de leitura, mas só para que os testes
rodem numa pasta temporária (o jogo grava `jogadas.csv` na pasta atual).
