"""
Etapa 3 - Testes das mensagens e da exibição na tela.

Casos de teste: CT28 a CT30 (defeitos D16, D17).
Requisito: RF14 (o jogador vê as cartas e as opções válidas a cada jogada).
A saída do terminal é capturada com a fixture capsys do PyTest.
"""
import pytest

from truco.jogador import Jogador

SEM_FLOR = ("1 de ESPADAS", "3 de COPAS", "4 de OUROS")
COM_FLOR = ("1 de COPAS", "5 de COPAS", "7 de COPAS")
OPCOES_ENVIDO = ("[6] Envido", "[7] Real Envido", "[8] Falta Envido")


def opcoes(jogador, interface, capsys):
    jogador.mostrar_opcoes(interface)
    return capsys.readouterr().out


# ---------------------------------------------------------------- CT28 / RF14
@pytest.mark.requisito("CT28")
class TestMostrarOpcoes:
    def test_tres_cartas_sem_flor(self, jogador_com_mao, interface, capsys):
        saida = opcoes(jogador_com_mao(*SEM_FLOR), interface, capsys)
        for texto in ("[0] 1 de ESPADAS", "[1] 3 de COPAS", "[2] 4 de OUROS",
                      "[4] Truco", *OPCOES_ENVIDO, "[9] Ir ao baralho"):
            assert texto in saida
        assert "[5] Flor" not in saida

    def test_tres_cartas_com_flor(self, jogador_com_mao, interface, capsys):
        jogador = jogador_com_mao(*COM_FLOR)
        assert "[5] Flor" in opcoes(jogador, interface, capsys)
        assert jogador.flor is True

    @pytest.mark.defeito("D16")
    @pytest.mark.xfail(reason="D16: a opção [5] Flor some na segunda vez que as opções são exibidas")
    def test_flor_continua_visivel_na_segunda_exibicao(self, jogador_com_mao, interface, capsys):
        jogador = jogador_com_mao(*COM_FLOR)
        opcoes(jogador, interface, capsys)
        assert "[5] Flor" in opcoes(jogador, interface, capsys)

    def test_duas_cartas_sem_envido(self, jogador_com_mao, interface, capsys):
        jogador = jogador_com_mao(*SEM_FLOR)
        jogador.jogar_carta(0)
        saida = opcoes(jogador, interface, capsys)
        assert "[4] Truco" in saida and "[9] Ir ao baralho" in saida
        assert not any(texto in saida for texto in OPCOES_ENVIDO)

    @pytest.mark.defeito("D17")
    @pytest.mark.xfail(reason="D17: com 1 carta na mão a opção [4] Truco não é exibida")
    def test_truco_disponivel_na_ultima_rodada(self, jogador_com_mao, interface, capsys):
        jogador = jogador_com_mao(*SEM_FLOR)
        jogador.jogar_carta(0)
        jogador.jogar_carta(0)
        assert "[4] Truco" in opcoes(jogador, interface, capsys)

    def test_truco_some_depois_do_vale_4(self, jogador_com_mao, interface, capsys):
        jogador = jogador_com_mao(*SEM_FLOR)
        jogador.pediu_truco = True
        assert "[4] Truco" not in opcoes(jogador, interface, capsys)


# ---------------------------------------------------------------- CT29 / RF14
@pytest.mark.requisito("CT29")
class TestMensagens:
    def test_border_msg_simples(self, interface, capsys):
        interface.border_msg("abc")
        assert capsys.readouterr().out == "╔═════╗\n║ abc ║\n╚═════╝\n"

    def test_border_msg_com_titulo_e_varias_linhas(self, interface, capsys):
        interface.border_msg("a\nbcd", title="T")
        assert capsys.readouterr().out == "╔═════╗\n║ T   ║\n║ -   ║\n║ a   ║\n║ bcd ║\n╚═════╝\n"

    @pytest.mark.parametrize("indent, largura, topo", [(1, None, "╔═════╗"), (2, None, "╔═══════╗"),
                                                       (1, 6, "╔════════╗")])
    def test_border_msg_parametros(self, interface, capsys, indent, largura, topo):
        interface.border_msg("abc", indent=indent, width=largura)
        linhas = capsys.readouterr().out.splitlines()
        assert linhas[0] == topo
        assert len({len(linha) for linha in linhas}) == 1  # moldura alinhada

    def test_placar_total(self, interface, capsys):
        interface.mostrar_placar_total("Renato", 3, "Lucas", 5)
        saida = capsys.readouterr().out
        assert "Pontuação Total" in saida
        assert "Jogador 1 - Renato: 3 Pontos Acumulados" in saida
        assert "Jogador 2 - Lucas: 5 Pontos Acumulados" in saida

    def test_placar_de_rodadas(self, interface, capsys):
        interface.mostrar_placar_rodadas("Renato", 1, "Lucas", 0)
        saida = capsys.readouterr().out
        assert "Rodadas da Partida Atual" in saida and "Renato: Venceu 1 Rodada(s)" in saida

    @pytest.mark.parametrize("vencedor, titulo, linha", [
        (1, "Jogador 1 Vencedor Envido", "Renato: Venceu o envido com 33 pontos"),
        (2, "Jogador 2 Vencedor Envido", "Lucas: Venceu o envido com 7 pontos")])
    def test_vencedor_do_envido(self, interface, capsys, vencedor, titulo, linha):
        interface.mostrar_vencedor_envido(vencedor, "Renato", 33, "Lucas", 7)
        saida = capsys.readouterr().out
        assert titulo in saida and linha in saida and "PERDEU o envido" in saida

    @pytest.mark.parametrize("vencedor, linha", [
        (1, "Jogador 1 - Renato: Venceu a flor e ganhou 3 pontos"),
        (2, "Jogador 2 - Lucas: Venceu a flor e ganhou 3 pontos")])
    def test_vencedor_da_flor(self, interface, capsys, vencedor, linha):
        interface.mostrar_vencedor_flor(vencedor, "Renato", "Lucas", 3)
        assert linha in capsys.readouterr().out

    @pytest.mark.parametrize("metodo, argumentos, esperado", [
        ("mostrar_ganhador_rodada", ("Renato",), "Renato ganhou a rodada\n\n"),
        ("mostrar_ganhador_jogo", ("Lucas",), "\nLucas ganhou o jogo\n"),
        ("mostrar_pediu_truco", ("Renato",), "Renato pediu truco e o pedido já foi aceito, escolha outra jogada!\n"),
        ("mostrar_jogador_opcoes", ("Renato",), "Jogador 1 é mão\n"),
    ])
    def test_mensagens_simples(self, interface, capsys, metodo, argumentos, esperado):
        getattr(interface, metodo)(*argumentos)
        assert capsys.readouterr().out == esperado

    def test_carta_jogada_e_carta_ganhadora(self, interface, capsys, nova_carta):
        interface.mostrar_carta_jogada("Renato", nova_carta("7 de OUROS"))
        interface.mostrar_carta_ganhadora(nova_carta("7 de OUROS"))
        assert capsys.readouterr().out == "Renato jogou a carta: 7 de OUROS\n\nCarta ganhadora: 7 de OUROS\n\n"

    def test_jogador_fugiu(self, interface, capsys):
        interface.mostrar_placar_total_jogador_fugiu(Jogador("Lucas"), "Renato", 0, "Lucas", 1)
        assert capsys.readouterr().out == "Jogador Lucas fugiu!\n"

    def test_limpar_tela_chama_o_comando_do_sistema(self, interface, monkeypatch):
        comandos = []
        monkeypatch.setattr("os.system", comandos.append)
        interface.limpar_tela()
        assert comandos == ["clear"]  # comando de Linux; no Windows seria "cls"


# ---------------------------------------------------------------- CT30 / RF14
@pytest.mark.requisito("CT30")
class TestDesenhoDasCartas:
    @pytest.mark.parametrize("carta, simbolo", [
        ("1 de ESPADAS", "♠"), ("7 de OUROS", "♦"), ("12 de COPAS", "♥"), ("5 de BASTOS", "♣")])
    def test_simbolo_do_naipe_no_centro(self, interface, carta, simbolo):
        desenho = interface.desenhar_cartas(carta)
        assert desenho[4] == f"│. . {simbolo} . .│"

    @pytest.mark.parametrize("carta, canto_superior, canto_inferior", [
        ("1 de ESPADAS", "│.1  . . .│", "│. . . 1 .│"),
        ("12 de COPAS", "│.12 . . .│", "│. . . 12.│")])
    def test_numero_nos_cantos(self, interface, carta, canto_superior, canto_inferior):
        desenho = interface.desenhar_cartas(carta)
        assert desenho[1] == canto_superior and desenho[7] == canto_inferior

    @pytest.mark.parametrize("carta", ["1 de ESPADAS", "10 de OUROS", "12 de COPAS"])
    def test_todas_as_linhas_tem_a_mesma_largura(self, interface, carta):
        desenho = interface.desenhar_cartas(carta)
        assert len(desenho) == 9 and {len(linha) for linha in desenho} == {11}

    def test_exibir_tres_cartas_lado_a_lado(self, interface, capsys):
        interface.exibir_cartas(["1 de ESPADAS", "7 de OUROS", "3 de COPAS"])
        linhas = capsys.readouterr().out.splitlines()
        assert len(linhas) == 9
        assert all(len(linha) == 11 * 3 + 2 * 2 for linha in linhas)
        assert linhas[4].count("│. . ") == 3
