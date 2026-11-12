"""Entradas no menu principal (CT31 a CT34; D06 e D11)."""
import pytest

from conftest import EntradasEsgotadas

pytestmark = [pytest.mark.entrada, pytest.mark.cenario, pytest.mark.lento]

HUMANO = ["1 de ESPADAS", "1 de BASTOS", "3 de COPAS"]
BOT = ["12 de OUROS", "11 de BASTOS", "4 de COPAS"]   # envido 4: o bot não pede envido
MAOS = [(HUMANO, BOT)] * 3


# Digita texto ao escolher a carta e espera uma nova tentativa.
@pytest.mark.requisito("CT31")
@pytest.mark.defeito("D06")
@pytest.mark.xfail(reason="D06: int(input()) sem tratamento; texto na escolha da carta encerra o jogo com ValueError")
def test_D06_texto_na_escolha_da_carta_pede_de_novo(executar_partida):
    partida = executar_partida("Renato", "Lucas", "a", "0", maos=MAOS)
    assert isinstance(partida.erro, EntradasEsgotadas)
    assert "Selecione um valor válido!" in partida.saida


# Confere se uma opção inválida gera aviso e repete a pergunta.
@pytest.mark.requisito("CT32")
def test_CT32_opcao_inexistente_avisa_e_pergunta_de_novo(executar_partida):
    partida = executar_partida("Renato", "Lucas", "-1", "5", "12", "0", maos=MAOS)
    assert partida.saida.count("Selecione um valor válido!") == 3
    assert all("Qual carta você quer jogar?" in p for p in partida.perguntas[2:6])
    assert "Renato jogou a carta: 1 de ESPADAS" in partida.saida


# Verifica se o jogo rejeita o índice igual ao número de cartas.
@pytest.mark.requisito("CT32")
@pytest.mark.defeito("D11")
@pytest.mark.xfail(reason="D11: o teste usa <= len(mão); o índice igual ao número de cartas dá IndexError")
def test_D11_indice_igual_ao_numero_de_cartas(executar_partida):
    partida = executar_partida("Renato", "Lucas", "3", "0", maos=MAOS)
    assert not isinstance(partida.erro, IndexError)
    assert "Selecione um valor válido!" in partida.saida


# Confere o ponto do bot e o início de uma nova mão após a desistência.
@pytest.mark.requisito("CT33")
def test_CT33_ir_ao_baralho_da_o_ponto_ao_bot_e_comeca_nova_mao(executar_partida, tmp_path):
    partida = executar_partida("Renato", "Lucas", "9", maos=MAOS)
    humano, bot = partida.estado["jogador1"], partida.estado["jogador2"]
    assert (humano.pontos, bot.pontos) == (0, 1)
    assert "Jogador Renato fugiu!" in partida.saida
    assert len(humano.mao) == 3 and humano.rodadas == 0
    assert (tmp_path / "jogadas.csv").exists()


# Verifica se o jogo recebe e exibe os nomes dos jogadores.
@pytest.mark.requisito("CT34")
def test_CT34_nomes_dos_jogadores(executar_partida):
    for nome_humano, nome_bot in (("Renato", "Lucas"), ("", "")):
        partida = executar_partida(nome_humano, nome_bot, "0", maos=MAOS)
        assert isinstance(partida.erro, EntradasEsgotadas), "nome vazio não pode quebrar o jogo"
        assert f"<< {nome_humano} - Jogador 1 >>" in partida.saida
        assert f"{nome_humano} jogou a carta: 1 de ESPADAS" in partida.saida
        assert f"<< {nome_bot} - Jogador 2 >>" in partida.saida


# Confere a borda superior válida: a última carta da mão é aceita.
@pytest.mark.requisito("CT32")
def test_CT32_ultima_carta_da_mao_e_aceita(executar_partida):
    partida = executar_partida("Renato", "Lucas", "2", maos=MAOS)
    assert "Renato jogou a carta: 3 de COPAS" in partida.saida
    assert "Selecione um valor válido!" not in partida.saida


# Pede Truco pelo menu [4]; o bot aumenta para Retruco e o humano aceita.
@pytest.mark.requisito("CT19")
def test_CT19_truco_pedido_pelo_menu(executar_partida):
    partida = executar_partida("Renato", "Lucas", "4", "1", "0", maos=MAOS)
    resposta = next(p for p in partida.perguntas if "você aceita" in p)
    assert "passa a valer 3 pontos" in resposta
    assert partida.estado["truco"].retornar_valor_aposta() == 3
    assert "Renato jogou a carta: 1 de ESPADAS" in partida.saida   # a partida segue


# Canta Flor pelo menu [5] com três cartas do mesmo naipe.
@pytest.mark.requisito("CT26")
def test_CT26_flor_cantada_pelo_menu(executar_partida):
    flor = ["1 de COPAS", "5 de COPAS", "7 de COPAS"]
    partida = executar_partida("Renato", "Lucas", "5", "0", maos=[(flor, BOT)] * 2)
    assert "[5] Flor" in partida.saida
    assert "Venceu a flor e ganhou 3 pontos" in partida.saida
    assert partida.estado["jogador1"].pontos == 3


# Pede Envido [6], Real Envido [7] e Falta Envido [8] pelo menu, com 33 pontos contra 4.
@pytest.mark.requisito("CT12")
@pytest.mark.requisito("CT13")
@pytest.mark.requisito("CT14")
def test_CT12_CT14_envidos_pedidos_pelo_menu(executar_partida):
    humano_33 = ["7 de COPAS", "6 de COPAS", "1 de OUROS"]
    # [6] o bot aceita e perde (+2); [7] e [8] o bot recusa (+2 e +5, regra do sistema)
    for opcao, pontos in (("6", 2), ("7", 2), ("8", 5)):
        partida = executar_partida("Renato", "Lucas", opcao, "0", maos=[(humano_33, BOT)] * 2)
        assert partida.estado["jogador1"].pontos == pontos, f"opção {opcao}"
        assert "Renato jogou a carta: 7 de COPAS" in partida.saida, f"opção {opcao}"


# Digita texto ao responder Envido e Truco e espera uma nova tentativa.
@pytest.mark.requisito("CT11")
@pytest.mark.requisito("CT22")
@pytest.mark.defeito("D12")
@pytest.mark.xfail(reason="D12: int(input()) sem tratamento também nas respostas de Envido e Truco; texto encerra o jogo")
def test_D12_texto_nas_respostas_de_envido_e_truco(executar_partida):
    humano_7 = ["7 de BASTOS", "5 de ESPADAS", "4 de OUROS"]
    bot_33 = ["7 de COPAS", "6 de COPAS", "12 de ESPADAS"]
    envido = executar_partida("Renato", "Lucas", "s", "1", maos=[(humano_7, bot_33)] * 2)
    truco = executar_partida("Renato", "Lucas", "0", "0", "s", "1", maos=MAOS)
    for partida in (envido, truco):
        assert not isinstance(partida.erro, ValueError)
