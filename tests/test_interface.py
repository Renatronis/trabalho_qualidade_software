"""Opções, mensagens e desenho das cartas (CT28 a CT30)."""
import pytest

OPCOES_ENVIDO = ("[6] Envido", "[7] Real Envido", "[8] Falta Envido")


# Confere as opções exibidas conforme as cartas na mão.
@pytest.mark.requisito("CT28")
def test_CT28_opcoes_mudam_conforme_a_mao(jogador_com_mao, interface, capsys):
    jogador = jogador_com_mao("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
    jogador.mostrar_opcoes(interface)
    saida = capsys.readouterr().out
    for texto in ("[0] 1 de ESPADAS", "[2] 4 de OUROS", "[4] Truco", *OPCOES_ENVIDO, "[9] Ir ao baralho"):
        assert texto in saida
    assert "[5] Flor" not in saida

    jogador.jogar_carta(0)
    jogador.mostrar_opcoes(interface)
    saida = capsys.readouterr().out
    assert "[4] Truco" in saida and not any(t in saida for t in OPCOES_ENVIDO)

    com_flor = jogador_com_mao("1 de COPAS", "5 de COPAS", "7 de COPAS")
    com_flor.mostrar_opcoes(interface)
    assert "[5] Flor" in capsys.readouterr().out


# Verifica a moldura das mensagens.
@pytest.mark.requisito("CT29")
def test_CT29_moldura_das_mensagens(interface, capsys):
    interface.border_msg("abc")
    assert capsys.readouterr().out == "╔═════╗\n║ abc ║\n╚═════╝\n"
    interface.border_msg("a\nbcd", title="T")
    assert capsys.readouterr().out == "╔═════╗\n║ T   ║\n║ -   ║\n║ a   ║\n║ bcd ║\n╚═════╝\n"


# Confere as mensagens de placar e de vencedores.
@pytest.mark.requisito("CT29")
def test_CT29_placar_e_vencedores(interface, capsys):
    interface.mostrar_placar_total("Renato", 3, "Lucas", 5)
    interface.mostrar_vencedor_envido(2, "Renato", 7, "Lucas", 33)
    interface.mostrar_vencedor_flor(1, "Renato", "Lucas", 3)
    interface.mostrar_ganhador_jogo("Lucas")
    saida = capsys.readouterr().out
    assert "Jogador 1 - Renato: 3 Pontos Acumulados" in saida
    assert "Jogador 2 - Lucas: Venceu o envido com 33 pontos" in saida
    assert "Jogador 1 - Renato: Venceu a flor e ganhou 3 pontos" in saida
    assert "Lucas ganhou o jogo" in saida


# Confere o desenho das cartas e os símbolos dos naipes.
@pytest.mark.requisito("CT30")
def test_CT30_desenho_das_cartas(interface):
    for carta, simbolo in (("1 de ESPADAS", "♠"), ("7 de OUROS", "♦"),
                           ("12 de COPAS", "♥"), ("5 de BASTOS", "♣")):
        desenho = interface.desenhar_cartas(carta)
        assert desenho[4] == f"│. . {simbolo} . .│"
        assert len(desenho) == 9 and {len(linha) for linha in desenho} == {11}


# Confere as demais mensagens, a limpeza de tela e as três cartas lado a lado.
@pytest.mark.requisito("CT29")
@pytest.mark.requisito("CT30")
def test_CT29_CT30_demais_mensagens_e_cartas_lado_a_lado(interface, capsys, monkeypatch):
    interface.mostrar_pediu_truco("Renato")
    interface.mostrar_jogador_opcoes("Renato")
    assert capsys.readouterr().out == ("Renato pediu truco e o pedido já foi aceito, escolha outra jogada!\n"
                                       "Jogador 1 é mão\n")
    comandos = []
    monkeypatch.setattr("os.system", comandos.append)
    interface.limpar_tela()
    assert comandos == ["clear"]
    interface.exibir_cartas(["1 de ESPADAS", "7 de OUROS", "3 de COPAS"])
    linhas = capsys.readouterr().out.splitlines()
    assert len(linhas) == 9 and all(len(linha) == 11 * 3 + 2 * 2 for linha in linhas)
