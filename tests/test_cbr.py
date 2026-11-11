"""
Inteligência Artificial: CBR com os 100 vizinhos mais próximos.

Casos de teste: CT35 a CT40 (defeitos D19, D20 e D22).
Requisitos: RF16 (o bot decide pela situação mais parecida), RF17 (base de
casos e 100 vizinhos), RNF02 (decisão em menos de 1 segundo).

Usa a IA VERDADEIRA (fixture cbr_real), com a base de 27.515 casos. As
situações de jogo são montadas com os próprios métodos da classe Dados, como
o jogo faria, e por isso o teste conhece a situação e pode conferir a decisão.
"""
import time

import numpy as np
import pandas as pd
import pytest

from truco.cbr import Cbr

pytestmark = [pytest.mark.ia, pytest.mark.lento]

MAO_FORTE = ("1 de ESPADAS", "1 de BASTOS", "3 de COPAS")
MAO_MEDIA = ("7 de OUROS", "2 de COPAS", "12 de BASTOS")
MAO_FRACA = ("4 de COPAS", "5 de OUROS", "6 de BASTOS")


@pytest.fixture
def situacao(cbr_real, bot_com_mao, nova_carta):
    """Grava no registro da IA a mão do bot e a 1ª carta do humano; devolve o bot."""
    def _montar(mao_bot, carta_humano):
        bot = bot_com_mao(*mao_bot)
        cbr_real.dados.primeira_rodada(list(bot.pontuacao_cartas), list(bot.mao_rank),
                                       bot.qualidade_mao, nova_carta(carta_humano))
        return bot
    return _montar


def vizinhos(cbr):
    return cbr.nbrs.kneighbors(cbr.dados.retornar_registro().to_numpy().reshape(1, -1))


# ---------------------------------------------------------------- CT35 / RF17
@pytest.mark.requisito("CT35")
def test_CT35_base_de_casos_e_consulta_de_100_vizinhos(cbr_real):
    assert cbr_real.dataset.shape == (27515, 52)
    assert cbr_real.dataset.isna().sum().sum() == 0
    assert list(cbr_real.dados.retornar_registro().columns) == list(cbr_real.dataset.columns)
    distancias, indices = vizinhos(cbr_real)
    assert indices.shape == (1, 100)
    assert list(distancias[0]) == sorted(distancias[0])


@pytest.mark.requisito("CT35")
def test_CT35_caso_da_base_recupera_ele_mesmo(cbr_real):
    """Etapa de recuperação do CBR: um caso idêntico é o vizinho mais próximo, com distância 0."""
    for linha in (0, 13000, 27514):
        distancias, indices = cbr_real.nbrs.kneighbors(cbr_real.dataset.iloc[[linha]].to_numpy())
        assert distancias[0][0] == 0
        assert cbr_real.dataset.iloc[indices[0][0]].equals(cbr_real.dataset.iloc[linha])


# ---------------------------------------------------------------- CT36 / RF16
@pytest.mark.requisito("CT36")
def test_CT36_escolhe_sempre_uma_carta_da_mao(cbr_real, situacao):
    for mao in (MAO_MEDIA, MAO_FRACA):
        for carta_humano in ("3 de OUROS", "4 de ESPADAS"):
            bot = situacao(mao, carta_humano)
            assert cbr_real.jogar_carta(1, list(bot.pontuacao_cartas)) in (0, 1, 2), (mao, carta_humano)
    assert cbr_real.jogar_carta(2, [24, 1]) in (0, 1)
    assert cbr_real.jogar_carta(3, [1]) == 0


@pytest.mark.requisito("CT36")
def test_CT36_joga_a_carta_mais_proxima_do_valor_de_referencia(cbr_real, monkeypatch):
    """Fixamos o valor mais comum entre os casos vencedores em 24; a IA deve jogar a carta mais próxima."""
    original = pd.Series.value_counts

    def referencia_24(serie, *args, **kwargs):
        if serie.name and serie.name.endswith("CartaRobo"):
            return pd.Series([10], index=[24])
        return original(serie, *args, **kwargs)

    monkeypatch.setattr(pd.Series, "value_counts", referencia_24)
    assert cbr_real.jogar_carta(1, [52, 24, 1]) == 1
    assert cbr_real.jogar_carta(1, [52, 30, 1]) == 1
    assert cbr_real.jogar_carta(1, [12, 52, 40]) == 0


@pytest.mark.requisito("CT36")
@pytest.mark.defeito("D19")
@pytest.mark.xfail(raises=IndexError,
                   reason="D19: com duas manilhas, nenhum dos 100 vizinhos é caso vencedor e jogar_carta lança IndexError")
def test_D19_ia_escolhe_carta_com_mao_de_duas_manilhas(cbr_real, situacao):
    bot = situacao(MAO_FORTE, "3 de OUROS")
    assert cbr_real.jogar_carta(1, list(bot.pontuacao_cartas)) in (0, 1, 2)


# ---------------------------------------------------------------- CT37 / RF16
@pytest.mark.requisito("CT37")
def test_CT37_resposta_ao_truco_valida_e_crescente(cbr_real, situacao):
    respostas = [cbr_real.truco("truco", 1, q) for q in range(0, 61, 5)]
    assert set(respostas) <= {0, 1, 2}
    assert respostas == sorted(respostas)          # a resposta nunca diminui quando a mão melhora
    assert respostas[0] == 0                       # mão sem qualidade foge
    bot = situacao(MAO_FORTE, "4 de ESPADAS")
    assert cbr_real.truco("truco", 1, bot.qualidade_mao) != 0   # mão forte não foge


@pytest.mark.requisito("CT37")
@pytest.mark.defeito("D20")
@pytest.mark.xfail(reason="D20: a IA compara os rótulos (2 > 1), e não as contagens; com qualquer mão real ela aumenta")
def test_D20_mao_fraca_nao_aumenta_o_truco(cbr_real, situacao):
    bot = situacao(MAO_FRACA, "3 de OUROS")
    assert cbr_real.truco("truco", 1, bot.qualidade_mao) != 2


# ---------------------------------------------------------------- CT38 / RF16
@pytest.mark.requisito("CT38")
def test_CT38_envido_respostas_validas_e_pedido_so_com_pontos(cbr_real):
    for pontos in (0, 25, 33):
        assert cbr_real.envido(6, 1, pontos, False) in (0, 1, 2, 3)
        assert cbr_real.envido(7, 1, pontos, False) in (0, 1)
        assert cbr_real.envido(8, 1, pontos, False) in (0, 1)
    # chamada do __main__ no início da vez do humano: o bot só pede com 6 pontos ou mais
    for pontos, pede in ((0, False), (4, False), (6, True), (33, True)):
        assert (cbr_real.envido("Envido", 2, pontos, False) in (6, 7, 8)) is pede, pontos


# ---------------------------------------------------------------- CT39 / RNF02
@pytest.mark.requisito("CT39")
def test_CT39_mesma_situacao_mesma_decisao_em_menos_de_1_segundo(cbr_real):
    decisoes = {
        "jogar_carta": lambda ia: ia.jogar_carta(1, [52, 24, 1]),
        "truco": lambda ia: ia.truco("truco", 1, 20),
        "envido": lambda ia: ia.envido(6, 1, 25, False),
    }
    outra_ia = Cbr()
    for nome, decidir in decisoes.items():
        inicio = time.perf_counter()
        resultados = {decidir(cbr_real) for _ in range(5)}
        assert (time.perf_counter() - inicio) / 5 < 1.0, nome
        assert len(resultados) == 1, nome                          # sempre a mesma decisão
        assert decidir(outra_ia) in resultados, nome               # outra instância decide igual


# ---------------------------------------------------------------- CT40 / RF16
@pytest.mark.requisito("CT40")
def test_CT40_situacao_informada_muda_os_vizinhos(cbr_real, situacao):
    _, vizinhos_vazio = vizinhos(cbr_real)
    situacao(MAO_FORTE, "3 de OUROS")
    _, vizinhos_preenchido = vizinhos(cbr_real)
    assert not np.array_equal(vizinhos_vazio, vizinhos_preenchido)


@pytest.mark.requisito("CT40")
@pytest.mark.cenario
@pytest.mark.defeito("D22")
@pytest.mark.xfail(reason="D22: a IA tem a sua própria instância de Dados; a situação gravada pelo jogo nunca chega a ela")
def test_D22_ia_recebe_a_situacao_da_partida(executar_partida):
    partida = executar_partida(
        "Renato", "Lucas", "0",
        maos=[(["3 de COPAS", "5 de OUROS", "6 de BASTOS"],
               ["4 de COPAS", "12 de OUROS", "2 de BASTOS"])])
    registro_da_ia = partida.estado["cbr"].dados.retornar_registro()
    assert registro_da_ia.primeiraCartaHumano.iloc[0] != 0
