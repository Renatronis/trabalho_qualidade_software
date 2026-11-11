"""
Entradas do usuário na tela principal (o jogo inteiro roda com teclado simulado).

Casos de teste: CT31 a CT34 (defeitos D09 e D25).
Requisitos: RF08 (ir ao baralho), RF15 (entrada inválida não encerra o jogo),
UC01 (nomes dos jogadores).
"""
import pytest

from conftest import EntradasEsgotadas

pytestmark = [pytest.mark.entrada, pytest.mark.cenario, pytest.mark.lento]

HUMANO = ["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"]
BOT = ["12 de OUROS", "11 de BASTOS", "4 de COPAS"]   # envido 4: o bot não pede envido
MAOS = [(HUMANO, BOT)] * 3


@pytest.mark.requisito("CT31")
@pytest.mark.defeito("D09")
@pytest.mark.xfail(reason="D09: int(input()) sem tratamento; texto na escolha da carta encerra o jogo com ValueError")
def test_D09_texto_na_escolha_da_carta_pede_de_novo(executar_partida):
    partida = executar_partida("Renato", "Lucas", "a", "0", maos=MAOS)
    assert isinstance(partida.erro, EntradasEsgotadas)        # o jogo continuou
    assert "Selecione um valor válido!" in partida.saida


@pytest.mark.requisito("CT32")
def test_CT32_opcao_inexistente_avisa_e_pergunta_de_novo(executar_partida):
    partida = executar_partida("Renato", "Lucas", "-1", "5", "12", "0", maos=MAOS)
    assert partida.saida.count("Selecione um valor válido!") == 3
    assert all("Qual carta você quer jogar?" in p for p in partida.perguntas[2:6])
    assert "Renato jogou a carta: 1 de ESPADAS" in partida.saida


@pytest.mark.requisito("CT32")
@pytest.mark.defeito("D25")
@pytest.mark.xfail(reason="D25: o teste usa <= len(mão); o índice igual ao número de cartas dá IndexError")
def test_D25_indice_igual_ao_numero_de_cartas(executar_partida):
    partida = executar_partida("Renato", "Lucas", "3", "0", maos=MAOS)
    assert not isinstance(partida.erro, IndexError)
    assert "Selecione um valor válido!" in partida.saida


@pytest.mark.requisito("CT33")
def test_CT33_ir_ao_baralho_da_o_ponto_ao_bot_e_comeca_nova_mao(executar_partida, tmp_path):
    partida = executar_partida("Renato", "Lucas", "9", maos=MAOS)
    humano, bot = partida.estado["jogador1"], partida.estado["jogador2"]
    assert (humano.pontos, bot.pontos) == (0, 1)
    assert "Jogador Renato fugiu!" in partida.saida
    assert len(humano.mao) == 3 and humano.rodadas == 0            # mão nova
    assert (tmp_path / "jogadas.csv").exists()                     # mão registrada (RF18)


@pytest.mark.requisito("CT34")
def test_CT34_nomes_dos_jogadores(executar_partida):
    for nome_humano, nome_bot in (("Renato", "Lucas"), ("", "")):
        partida = executar_partida(nome_humano, nome_bot, "0", maos=MAOS)
        assert isinstance(partida.erro, EntradasEsgotadas), "nome vazio não pode quebrar o jogo"
        assert f"<< {nome_humano} - Jogador 1 >>" in partida.saida
        assert f"{nome_humano} jogou a carta: 1 de ESPADAS" in partida.saida
        assert f"<< {nome_bot} - Jogador 2 >>" in partida.saida
