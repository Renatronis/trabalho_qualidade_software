"""
Etapa 4 - Testes do registro de jogadas (classe Dados).

Caso de teste: CT41 (defeitos D23 e D24).
Requisito: RF18 (ao fim de cada mão as jogadas são registradas) e a base de
casos da IA (RF17): o registro de uma mão precisa seguir o mesmo formato da
base, senão a IA compara situações que não correspondem.

Formato da base (conferido em dbtrucoimitacao_maos.csv): cada carta jogada é
gravada pelo seu CÓDIGO de pontos (3 = 24, 1 de Espadas = 52 ...), e cada
rodada tem colunas próprias: primeiraCartaRobo, segundaCartaHumano etc.
"""
import pandas as pd
import pytest

from truco.dados import Dados

pytestmark = pytest.mark.lento


@pytest.fixture(scope="module")
def _dados_carregados():
    with pytest.MonkeyPatch.context() as mp:
        from conftest import RAIZ, read_csv_compativel
        mp.setattr(pd, "read_csv", read_csv_compativel)
        mp.chdir(RAIZ)
        return Dados()


@pytest.fixture
def dados(_dados_carregados):
    _dados_carregados.registro = _dados_carregados.carregar_modelo_zerado()
    return _dados_carregados


def valor(dados, coluna):
    return dados.retornar_registro()[coluna].iloc[0]


def codigo(carta):
    return carta.retornar_pontos_carta(carta)


# ---------------------------------------------------------------- CT41 / RF18
@pytest.mark.requisito("CT41")
class TestRegistroDasRodadas:
    def test_primeira_rodada_grava_a_mao_do_bot_e_a_carta_do_humano(self, dados, bot_com_mao, nova_carta):
        bot = bot_com_mao("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
        dados.primeira_rodada(list(bot.pontuacao_cartas), list(bot.mao_rank), bot.qualidade_mao,
                              nova_carta("7 de COPAS"))
        assert (valor(dados, "cartaAltaRobo"), valor(dados, "cartaMediaRobo"),
                valor(dados, "cartaBaixaRobo")) == (52, 24, 1)
        assert valor(dados, "jogadorMao") == 1
        assert valor(dados, "naipePrimeiraCartaHumano") == 4  # COPAS

    def test_ganhadores_das_rodadas(self, dados, nova_carta):
        humano, robo = nova_carta("3 de COPAS"), nova_carta("2 de OUROS")
        dados.segunda_rodada(humano, robo, 1)
        dados.terceira_rodada(humano, robo, 2)
        dados.finalizar_rodadas(humano, robo, 1)
        assert (valor(dados, "ganhadorPrimeiraRodada"), valor(dados, "ganhadorSegundaRodada"),
                valor(dados, "ganhadorTerceiraRodada")) == (1, 2, 1)

    def test_naipes_das_cartas_do_humano(self, dados, nova_carta):
        dados.segunda_rodada(nova_carta("3 de ESPADAS"), nova_carta("2 de OUROS"), 1)
        dados.terceira_rodada(nova_carta("4 de BASTOS"), nova_carta("5 de OUROS"), 1)
        dados.finalizar_rodadas(nova_carta("6 de OUROS"), nova_carta("7 de COPAS"), 1)
        assert (valor(dados, "naipePrimeiraCartaHumano"), valor(dados, "naipeSegundaCartaHumano"),
                valor(dados, "naipeTerceiraCartaHumano")) == (1, 3, 2)

    @pytest.mark.defeito("D23")
    @pytest.mark.xfail(reason="D23: as cartas do robô vão sempre para 'terceiraCartaRobo' e a 2ª carta do humano "
                              "vai para um atributo 'SegundaCartaHumano' (com S maiúsculo)")
    @pytest.mark.parametrize("metodo, coluna_humano, coluna_robo", [
        ("segunda_rodada", "primeiraCartaHumano", "primeiraCartaRobo"),
        ("terceira_rodada", "segundaCartaHumano", "segundaCartaRobo"),
        ("finalizar_rodadas", "terceiraCartaHumano", "terceiraCartaRobo"),
    ], ids=["rodada-1", "rodada-2", "rodada-3"])
    def test_cartas_de_cada_rodada_na_coluna_certa(self, dados, nova_carta, metodo, coluna_humano, coluna_robo):
        humano, robo = nova_carta("3 de COPAS"), nova_carta("1 de ESPADAS")
        getattr(dados, metodo)(humano, robo, 2)
        assert valor(dados, coluna_humano) == codigo(humano)
        assert valor(dados, coluna_robo) == codigo(robo)

    @pytest.mark.defeito("D23")
    @pytest.mark.xfail(reason="D23: 'qualidadeMaoBot' não é coluna da base; a qualidade fica fora do registro")
    def test_qualidade_da_mao_do_bot_e_registrada(self, dados, bot_com_mao, nova_carta):
        bot = bot_com_mao("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
        dados.primeira_rodada(list(bot.pontuacao_cartas), list(bot.mao_rank), bot.qualidade_mao,
                              nova_carta("7 de COPAS"))
        assert valor(dados, "qualidadeMaoRobo") == int(bot.qualidade_mao)

    @pytest.mark.defeito("D23")
    @pytest.mark.xfail(reason="D23: Dados.envido grava em 'quemEnvido', 'quemRealEnvido' e 'quemFaltaEnvido', que não são colunas")
    def test_envido_e_registrado_nas_colunas_da_base(self, dados):
        dados.envido(1, 2, 0, 1)
        assert (valor(dados, "quemPediuEnvido"), valor(dados, "quemPediuRealEnvido"),
                valor(dados, "quemPediuFaltaEnvido"), valor(dados, "quemGanhouEnvido")) == (1, 2, 0, 1)

    def test_nenhum_metodo_cria_campos_fora_da_base(self, dados, nova_carta, bot_com_mao):
        """Os métodos que estão corretos não podem criar colunas novas."""
        dados.truco(1, 2, 1, 0, 2)
        dados.flor(1, 0, 0, 32)
        dados.vencedor_envido(2, 0)
        dados.vencedor_truco(2, 1)
        dados.vencedor_flor(1, 2)
        assert list(dados.retornar_registro().columns) == list(dados.retornar_casos().columns)
        assert (valor(dados, "quemTruco"), valor(dados, "quemGanhouTruco"), valor(dados, "pontosFlorRobo")) == (1, 2, 32)

    @pytest.mark.parametrize("rodada, coluna, coluna_naipe", [
        ("primeira", "primeiraCartaRobo", "naipePrimeiraCartaRobo"),
        ("segunda", "segundaCartaRobo", "naipeSegundaCartaRobo"),
        ("terceira", "terceiraCartaRobo", "naipeTerceiraCartaRobo"),
    ])
    def test_cartas_jogadas_pelo_bot_usa_a_coluna_da_rodada(self, dados, nova_carta, rodada, coluna, coluna_naipe):
        dados.cartas_jogadas_pelo_bot(rodada, nova_carta("7 de OUROS"))
        assert valor(dados, coluna_naipe) == 2  # OUROS

    @pytest.mark.defeito("D24")
    @pytest.mark.xfail(reason="D24: a carta é gravada pelo número (1) e não pelo código da base (52 para o 1 de Espadas)")
    def test_carta_gravada_com_o_codigo_da_base(self, dados, nova_carta):
        carta = nova_carta("1 de ESPADAS")
        dados.cartas_jogadas_pelo_bot("primeira", carta)
        assert valor(dados, "primeiraCartaRobo") == 52


@pytest.mark.requisito("CT41")
class TestArquivoDeJogadas:
    def test_primeira_mao_cria_o_arquivo_com_cabecalho(self, dados, tmp_path):
        dados.finalizar_partida()
        arquivo = pd.read_csv(tmp_path / "jogadas.csv")
        assert len(arquivo) == 1
        assert "cartaAltaRobo" in arquivo.columns

    def test_maos_seguintes_sao_acrescentadas(self, dados, tmp_path):
        for _ in range(3):
            dados.finalizar_partida()
        linhas = (tmp_path / "jogadas.csv").read_text(encoding="utf-8").strip().splitlines()
        assert len(linhas) == 1 + 3  # um cabeçalho e uma linha por mão

    def test_resetar_zera_o_registro(self, dados, nova_carta):
        dados.segunda_rodada(nova_carta("3 de COPAS"), nova_carta("2 de OUROS"), 1)
        dados.resetar()
        assert (dados.retornar_registro().to_numpy() == 0).all()
        assert len(dados.retornar_casos()) == 27515
