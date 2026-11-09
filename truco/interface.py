import os

class Interface():
    def __init__(self):
        pass


    def border_msg(self, msg, indent=1, width=None, title=None):
        """Exibe uma caixa em torno de determinada mensagem."""
        lines = msg.split('\n')
        space = " " * indent
        if not width:
            width = max(map(len, lines))
        box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border

        if title:
            box += f'║{space}{title:<{width}}{space}║\n'  # title
            box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore

        box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
        box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
        print(box)
  

    def limpar_tela(self):
        """Limpa a tela do usuário após determinado ponto da partida, sendo necessário adaptar pro sistema operacional utilizado."""
        # Caso rodar em Linux
        os.system("clear")
        # Caso rodar em Windows
        # os.system("cls")


    def mostrar_carta_jogada(self, jogador, carta):
        """Exibe a última carta jogada."""
        print(f"{jogador} jogou a carta: {carta.retornar_carta()}")


    def mostrar_carta_ganhadora(self, carta):
        """Exibe quem ganhou a rodada."""
        print(f"\nCarta ganhadora: {carta.retornar_carta()}\n")

    def mostrar_ganhador_rodada(self, jogador):
        print(f"{jogador} ganhou a rodada\n")


    def mostrar_placar_total_jogador_fugiu(self, jogador_fugiu, jogador1, jogador1_pontos, jogador2, jogador2_pontos):
        """Exibe um aviso de que o jogador fugiu e o placar total,"""
        print(f'Jogador {jogador_fugiu.nome} fugiu!')
        # self.mostrar_placar_total(jogador1, jogador1_pontos, jogador2, jogador2_pontos)


    def mostrar_placar_total(self, jogador1, jogador1_pontos, jogador2, jogador2_pontos):
        """Exibe o placar total da partida."""
        self.border_msg(f"Jogador 1 - {jogador1}: {jogador1_pontos} Pontos Acumulados\nJogador 2 - {jogador2}: {jogador2_pontos} Pontos Acumulados", title='Pontuação Total')


    def mostrar_placar_rodadas(self, jogador1, jogador1_pontos, jogador2, jogador2_pontos):
        """Exibe o placar entre cada uma das rodadas."""
        self.border_msg(f"Jogador 1 - {jogador1}: Venceu {jogador1_pontos} Rodada(s)\nJogador 2 - {jogador2}: Venceu {jogador2_pontos} Rodada(s)", title='Rodadas da Partida Atual')

    def mostrar_vencedor_flor(self, vencedor, jogador1, jogador2, pontos):
        """Exibe o placar entre cada uma das rodadas."""
        if (vencedor == 1):
            self.border_msg(f"Jogador 1 - {jogador1}: Venceu a flor e ganhou {pontos} pontos", title='Vencedor Flor')

        else:
            self.border_msg(f"Jogador 2 - {jogador2}: Venceu a flor e ganhou {pontos} pontos", title='Vencedor Flor')


    def mostrar_vencedor_envido(self, vencedor, jogador1, jogador1_pontos, jogador2, jogador2_pontos):
        """Exibe o placar entre cada uma das rodadas."""
        if (vencedor == 1):
            self.border_msg(f"Jogador 1 - {jogador1}: Venceu o envido com {jogador1_pontos} pontos\nJogador 2 - {jogador2}: PERDEU o envido com {jogador2_pontos} pontos", title='Jogador 1 Vencedor Envido')
            
        else:
             self.border_msg(f"Jogador 2 - {jogador2}: Venceu o envido com {jogador2_pontos} pontos\nJogador 1 - {jogador1}: PERDEU o envido com {jogador1_pontos} pontos", title='Jogador 2 Vencedor Envido')


    def mostrar_ganhador_jogo(self, jogador):
        """Exibe o jogador que obteu a pontuação necessária para vencer o jogo."""
        print(f"\n{jogador} ganhou o jogo")


    def mostrar_pediu_truco(self, jogador):
        """Exibe aviso de que o pedido de truco já foi realizado."""
        print(f'{jogador} pediu truco e o pedido já foi aceito, escolha outra jogada!')


    def mostrar_jogador_opcoes(self, jogador):
        """Exibe as possibilidades de jogada para o jogador."""
        print(f"Jogador 1 é mão")


    def desenhar_cartas(self, s):
        """Exibe/desenha a carta jogada."""
        l_mostrar_carta = [] 
        l_mostrar_carta.append("┌─────────┐")
        l_mostrar_carta.append("│{}{}. . .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . {}. .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . .{}{}│")
        l_mostrar_carta.append("└─────────┘")

        x = ("│.", s[:2], " . . .│")
        l_mostrar_carta[1] = "".join(x)

        x = ("│. . . ", s[:2], ".│")
        l_mostrar_carta[7] = "".join(x)
        
        #  ["Espadas", "Ouros", "Copas", "Espadas"]
        if "OUROS" in s:
            l_mostrar_carta[4] = "│. . ♦ . .│"

        if "BASTOS" in s:
            l_mostrar_carta[4] = "│. . ♣ . .│"

        if "COPAS" in s:
            l_mostrar_carta[4] = "│. . ♥ . .│"

        if "ESPADAS" in s:
            l_mostrar_carta[4] = "│. . ♠ . .│"

        return l_mostrar_carta

    def exibir_cartas(self, cartas):
        """Chama o método que exibe todas as cartas da mão, fazendo um join entre toda a mão do jogador"""
        print('\n'.join(map('  '.join, zip(*(self.desenhar_cartas(c) for c in cartas)))))

    def exibir_unica_carta(self, carta):
        print('\n'.join(map('  '.join, zip(*(self.desenhar_cartas(carta))))))