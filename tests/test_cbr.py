"""
Etapa 4 - Testes da Inteligência Artificial (CBR com vizinhos mais próximos).

Casos de teste: CT35 a CT40 (defeitos D15, D18 a D22).
Requisitos: RF16 (o bot decide pela situação mais parecida), RF17 (base de
casos e 100 vizinhos), RNF02 (decisão em menos de 1 segundo).

Aqui usamos a IA VERDADEIRA (fixture cbr_real), com a base de 27.515 casos.
As situações de jogo são montadas com os próprios métodos da classe Dados,
do mesmo jeito que o jogo faria: assim o teste conhece a situação e pode
conferir a decisão.
"""
import time

import numpy as np
import pandas as pd
import pytest

from truco.bot import Bot
from truco.cbr import Cbr

pytestmark = [pytest.mark.ia, pytest.mark.lento]

MAO_FORTE = ("1 de ESPADAS", "1 de BASTOS", "3 de COPAS")
MAO_MEDIA = ("7 de OUROS", "2 de COPAS", "12 de BASTOS")
MAO_FRACA = ("4 de COPAS", "5 de OUROS", "6 de BASTOS")


@pytest.fixture
def situacao(cbr_real, bot_com_mao, nova_carta):
    """Monta no registro da IA a situação de uma mão em andamento.

    situacao(mao_bot, primeira_carta_humano, rodada=1, ganhador_primeira=None)
    devolve o bot já criado.
    """
    def _montar(mao_bot, carta_humano, rodada=1, ganhador_primeira=1):
        bot = bot_com_mao(*mao_bot)
        dados = cbr_real.dados
        dados.primeira_rodada(list(bot.pontuacao_cartas), list(bot.mao_rank),
                              bot.qualidade_mao, nova_carta(carta_humano))
        if rodada >= 2:
            dados.segunda_rodada(nova_carta(carta_humano), bot.mao[0], ganhador_primeira)
        return bot
    return _montar


# ---------------------------------------------------------------- CT35 / RF17
@pytest.mark.requisito("CT35")
class TestBaseDeCasos:
    def test_tamanho_e_sem_valores_vazios(self, cbr_real):
        assert cbr_real.dataset.shape == (27515, 52)
        assert cbr_real.dataset.isna().sum().sum() == 0

    def test_registro_tem_as_mesmas_colunas_da_base(self, cbr_real):
        assert list(cbr_real.dados.retornar_registro().columns) == list(cbr_real.dataset.columns)

    def test_registro_inicial_e_zerado(self, cbr_real):
        assert (cbr_real.dados.retornar_registro().to_numpy() == 0).all()

    def test_consulta_devolve_100_vizinhos_em_ordem_de_distancia(self, cbr_real):
        registro = cbr_real.dados.retornar_registro().to_numpy().reshape(1, -1)
        distancias, indices = cbr_real.nbrs.kneighbors(registro)
        assert indices.shape == (1, 100)
        assert list(distancias[0]) == sorted(distancias[0])

    @pytest.mark.parametrize("linha", [0, 100, 27514])
    def test_caso_da_base_recupera_ele_mesmo_com_distancia_zero(self, cbr_real, linha):
        """Etapa de recuperação do CBR: um caso idêntico deve ser o vizinho mais próximo."""
        caso = cbr_real.dataset.iloc[[linha]].to_numpy()
        distancias, indices = cbr_real.nbrs.kneighbors(caso)
        assert distancias[0][0] == 0
        assert cbr_real.dataset.iloc[indices[0][0]].equals(cbr_real.dataset.iloc[linha])


# ---------------------------------------------------------------- CT36 / RF16
@pytest.mark.requisito("CT36")
class TestJogarCarta:
    @pytest.mark.parametrize("mao", [
        pytest.param(MAO_FORTE, id="forte", marks=[
            pytest.mark.defeito("D19"),
            pytest.mark.xfail(raises=IndexError,
                              reason="D19: com duas manilhas, nenhum dos 100 vizinhos é caso vencedor e a IA quebra")]),
        pytest.param(MAO_MEDIA, id="media"),
        pytest.param(MAO_FRACA, id="fraca"),
    ])
    @pytest.mark.parametrize("carta_humano", ["3 de OUROS", "1 de COPAS", "4 de ESPADAS"])
    def test_primeira_rodada_devolve_indice_valido(self, cbr_real, situacao, mao, carta_humano):
        bot = situacao(mao, carta_humano)
        escolha = cbr_real.jogar_carta(1, list(bot.pontuacao_cartas))
        assert escolha in (0, 1, 2)

    @pytest.mark.parametrize("pontuacao", [[52, 24, 1], [24, 1], [1]], ids=["3-cartas", "2-cartas", "1-carta"])
    def test_indice_valido_com_mao_de_qualquer_tamanho(self, cbr_real, pontuacao):
        escolha = cbr_real.jogar_carta(4 - len(pontuacao), list(pontuacao))
        assert 0 <= escolha < len(pontuacao)

    def test_com_o_registro_inicial_joga_a_carta_mais_fraca_primeiro(self, cbr_real):
        """Situação conhecida: sem informação da partida, a IA guarda as cartas fortes."""
        assert cbr_real.jogar_carta(1, [52, 24, 1]) == 2

    def test_escolhe_a_carta_mais_proxima_do_valor_de_referencia(self, cbr_real, monkeypatch):
        """Se os casos vencedores mais comuns jogaram uma carta de valor 24, a IA joga o 3 (24 pontos)."""
        original = pd.Series.value_counts

        def referencia_fixa(serie, *args, **kwargs):
            if serie.name and serie.name.endswith("CartaRobo"):
                return pd.Series([10], index=[24])
            return original(serie, *args, **kwargs)

        monkeypatch.setattr(pd.Series, "value_counts", referencia_fixa)
        assert cbr_real.jogar_carta(1, [52, 24, 1]) == 1
        assert cbr_real.jogar_carta(1, [52, 30, 1]) == 1   # 30 é o mais próximo de 24
        assert cbr_real.jogar_carta(1, [12, 52, 40]) == 0  # 12 é o mais próximo de 24

    @pytest.mark.defeito("D18")
    @pytest.mark.xfail(reason="D18: o filtro de 'jogadas vencidas' deixa de fora as mãos que o bot venceu na 1ª e na 2ª rodada")
    def test_filtro_considera_todas_as_maos_vencidas(self, cbr_real):
        base = cbr_real.dataset
        g1, g2, g3 = (base[c] == 2 for c in
                      ("ganhadorPrimeiraRodada", "ganhadorSegundaRodada", "ganhadorTerceiraRodada"))
        venceu_duas = (g1 & g2) | (g1 & g3) | (g2 & g3)
        # mesma expressão usada em Cbr.jogar_carta
        filtro_do_jogo = ((g1 & g2 | g1) & g3) | (g2 & g3)
        assert (venceu_duas & ~filtro_do_jogo).sum() == 0

    @pytest.mark.defeito("D19")
    @pytest.mark.xfail(raises=IndexError,
                       reason="D19: sem nenhum caso vencedor entre os 100 vizinhos, jogar_carta lança IndexError")
    def test_segunda_rodada_depois_de_perder_a_primeira(self, cbr_real, situacao):
        bot = situacao(MAO_MEDIA, "12 de COPAS", rodada=2, ganhador_primeira=1)
        escolha = cbr_real.jogar_carta(2, [24, 1])
        assert escolha in (0, 1)


# ---------------------------------------------------------------- CT37 / RF16
@pytest.mark.requisito("CT37")
class TestTruco:
    @pytest.mark.parametrize("qualidade", [0, 5, 20, 38.4, 60])
    def test_resposta_e_0_1_ou_2(self, cbr_real, qualidade):
        assert cbr_real.truco("truco", 1, qualidade) in (0, 1, 2)

    def test_resposta_nunca_diminui_quando_a_mao_melhora(self, cbr_real):
        respostas = [cbr_real.truco("truco", 1, q) for q in range(0, 61, 5)]
        assert respostas == sorted(respostas)

    def test_mao_sem_qualidade_foge(self, cbr_real):
        assert cbr_real.truco("truco", 1, 0) == 0

    def test_mao_forte_nao_foge(self, cbr_real, situacao):
        bot = situacao(MAO_FORTE, "4 de ESPADAS")
        assert cbr_real.truco("truco", 1, bot.qualidade_mao) != 0

    @pytest.mark.defeito("D20")
    @pytest.mark.xfail(reason="D20: a IA compara os rótulos (2 > 1), e não as contagens; com qualquer mão real ela aumenta")
    def test_mao_fraca_nao_aumenta_a_aposta(self, cbr_real, situacao):
        bot = situacao(MAO_FRACA, "3 de OUROS")
        assert cbr_real.truco("truco", 1, bot.qualidade_mao) != 2


# ---------------------------------------------------------------- CT38 / RF16
@pytest.mark.requisito("CT38")
class TestEnvido:
    @pytest.mark.parametrize("pontos", [0, 7, 25, 33])
    @pytest.mark.parametrize("perdendo", [False, True])
    def test_resposta_ao_envido(self, cbr_real, pontos, perdendo):
        assert cbr_real.envido(6, 1, pontos, perdendo) in (0, 1, 2, 3)

    @pytest.mark.parametrize("tipo", [7, 8], ids=["real-envido", "falta-envido"])
    @pytest.mark.parametrize("pontos", [0, 33])
    def test_resposta_ao_real_e_falta_envido(self, cbr_real, tipo, pontos):
        assert cbr_real.envido(tipo, 1, pontos, False) in (0, 1)

    @pytest.mark.parametrize("pontos, pede", [(0, False), (4, False), (6, True), (28, True), (33, True)])
    def test_bot_so_pede_envido_com_pontos(self, cbr_real, pontos, pede):
        """Chamada feita pelo __main__ no início da vez do humano: avaliar_envido(cbr, 'Envido', 2, ...)."""
        resposta = cbr_real.envido("Envido", 2, pontos, False)
        assert (resposta in (6, 7, 8)) is pede

    @pytest.mark.defeito("D20")
    @pytest.mark.xfail(reason="D20: a resposta ao envido é a mesma com 0 ou com 33 pontos (compara rótulos, não contagens)")
    def test_resposta_depende_dos_pontos_do_bot(self, cbr_real):
        assert cbr_real.envido(6, 1, 0, False) != cbr_real.envido(6, 1, 33, False)


# ---------------------------------------------------------------- CT39 / RNF02
@pytest.mark.requisito("CT39")
class TestConsistenciaEDesempenho:
    @pytest.mark.parametrize("decisao", [
        lambda ia: ia.jogar_carta(1, [52, 24, 1]),
        lambda ia: ia.truco("truco", 1, 20),
        lambda ia: ia.envido(6, 1, 25, False),
    ], ids=["jogar_carta", "truco", "envido"])
    def test_mesma_situacao_mesma_decisao(self, cbr_real, decisao):
        assert len({decisao(cbr_real) for _ in range(5)}) == 1

    def test_duas_ias_independentes_decidem_igual(self, cbr_real):
        outra = Cbr()
        assert outra.jogar_carta(1, [52, 24, 1]) == cbr_real.jogar_carta(1, [52, 24, 1])
        assert outra.truco("truco", 1, 20) == cbr_real.truco("truco", 1, 20)

    @pytest.mark.parametrize("decisao", [
        lambda ia: ia.jogar_carta(1, [52, 24, 1]),
        lambda ia: ia.truco("truco", 1, 20),
        lambda ia: ia.envido(6, 1, 25, False),
    ], ids=["jogar_carta", "truco", "envido"])
    def test_decisao_em_menos_de_1_segundo(self, cbr_real, decisao):
        inicio = time.perf_counter()
        decisao(cbr_real)
        assert time.perf_counter() - inicio < 1.0


# ---------------------------------------------------------------- CT40 / RF16
@pytest.mark.requisito("CT40")
class TestUsoDaRodadaCorreta:
    @staticmethod
    def colunas_consultadas(cbr, monkeypatch, rodada):
        consultadas = []
        original = pd.DataFrame.__getitem__

        def espiao(df, chave):
            if isinstance(chave, str) and chave.endswith("CartaRobo"):
                consultadas.append(chave)
            return original(df, chave)

        monkeypatch.setattr(pd.DataFrame, "__getitem__", espiao)
        cbr.jogar_carta(rodada, [52, 24, 1][: 4 - rodada])
        monkeypatch.undo()
        return consultadas

    def test_rodada_2_consulta_a_segunda_carta(self, cbr_real, monkeypatch):
        assert self.colunas_consultadas(cbr_real, monkeypatch, 2) == ["segundaCartaRobo"]

    @pytest.mark.defeito("D21")
    @pytest.mark.xfail(reason="D21: rodada 1 consulta 'terceiraCartaRobo' e rodada 3 consulta 'primeiraCartaRobo' (invertidas)")
    @pytest.mark.parametrize("rodada, coluna", [(1, "primeiraCartaRobo"), (3, "terceiraCartaRobo")])
    def test_rodadas_1_e_3_consultam_a_propria_carta(self, cbr_real, monkeypatch, rodada, coluna):
        assert self.colunas_consultadas(cbr_real, monkeypatch, rodada) == [coluna]

    def test_registro_preenchido_muda_a_consulta(self, cbr_real, situacao):
        """Quando a situação é informada, os vizinhos encontrados mudam."""
        vazio = cbr_real.dados.retornar_registro().to_numpy().reshape(1, -1)
        _, vizinhos_vazio = cbr_real.nbrs.kneighbors(vazio)
        situacao(MAO_FORTE, "3 de OUROS")
        preenchido = cbr_real.dados.retornar_registro().to_numpy().reshape(1, -1)
        _, vizinhos_preenchido = cbr_real.nbrs.kneighbors(preenchido)
        assert not np.array_equal(vizinhos_vazio, vizinhos_preenchido)

    @pytest.mark.cenario
    @pytest.mark.defeito("D22")
    @pytest.mark.xfail(reason="D22: a IA tem a sua própria instância de Dados; a situação gravada pelo jogo nunca chega a ela")
    def test_ia_recebe_a_situacao_da_partida(self, executar_partida):
        partida = executar_partida(
            "Renato", "Lucas", "0",
            maos=[(["3 de COPAS", "5 de OUROS", "6 de BASTOS"],
                   ["4 de COPAS", "12 de OUROS", "2 de BASTOS"])])
        registro_da_ia = partida.estado["cbr"].dados.retornar_registro()
        assert registro_da_ia.primeiraCartaHumano.iloc[0] == 3


@pytest.mark.defeito("D15")
@pytest.mark.xfail(reason="D15: o bot chama cbr.flor(), mas a classe Cbr não tem esse método")
def test_ia_sabe_decidir_sobre_a_flor(cbr_real):
    assert cbr_real.flor() in (True, False)
