class Envido():
    def __init__(self):
        self.valor_envido = 2
        self.estado_atual = 0
        self.jogador_pediu_envido = 0
        self.quem_real_envido = 0
        self.quem_falta_envido = 0
        self.quem_fugiu = 0
        self.quem_venceu_envido = 0
        self.jogador_bloqueado = 0
        self.jogador1_pontos = 0
        self.jogador2_pontos = 0


    def inverter_jogador_bloqueado(self):
        """Lógica para impedir que o mesmo jogador não peça o aumento de aposta seguidamente."""
        if (self.jogador_bloqueado == 1):
            self.jogador_bloqueado = 2
        
        else:
            self.jogador_bloqueado = 1


    def inicializar_jogador_bloqueado(self, quem_pediu):
        """Inicialização do jogador que foi bloqueado e não pode pedir aumento da aposta do jogo."""
        self.jogador_bloqueado = quem_pediu


    def controlador_envido(self, cbr, dados, tipo, quem_pediu, jogador1, jogador2, interface):
        """Controlador de métodos, para selecionar o que pode ser chamado ou não."""
        print(2)
        if (self.estado_atual != 0 or tipo == self.estado_atual):
            return None
        
        if (quem_pediu == self.jogador_bloqueado):
            return None

        else:
            self.inicializar_jogador_bloqueado(quem_pediu)

        self.definir_pontos_jogadores(jogador1, jogador2)

        if (tipo == 6):
            self.envido(cbr, quem_pediu, jogador1, jogador2)

        if (tipo ==  7):
            self.real_envido(cbr, quem_pediu, jogador1, jogador2)

        if (tipo ==  8):
            self.falta_envido(cbr, quem_pediu, jogador1, jogador2)
        
        # else:
        #     return None

        if (self.quem_fugiu == 0):
            interface.mostrar_vencedor_envido(self.quem_venceu_envido, jogador1.nome, self.jogador1_pontos, jogador2.nome, self.jogador2_pontos)

        
    def envido(self, cbr, quem_pediu, jogador1, jogador2):
        self.estado_atual = 6
        print("Jogador pediu Envido!")

        if (quem_pediu == 1):
            self.jogador_pediu_envido = 1
            escolha = jogador2.avaliar_envido(cbr, self.estado_atual, 1, self.jogador2_pontos)
            # cbr, tipo, quem_pediu, pontos_jogador1)

        else:
            self.jogador_pediu_envido = 2
            escolha = -1
            while(escolha not in [0, 1, 2, 3]):
                escolha = int(input(f"Jogador {quem_pediu}, você aceita o pedido de envido?\n[0] Recusar\n[1] Aceitar\n[2] Real Envido\n[3] Falta Envido"))
        

        if escolha == 0:
            print(f"fugiu")
            if (quem_pediu == 1):
                jogador1.pontos += 1
                self.quem_fugiu = 2

            else:
                jogador2.pontos += 1
                self.quem_fugiu = 1

            return

        elif escolha == 1:
            print('Jogador aceitou envido!')
            self.avaliar_vencedor_envido(quem_pediu, jogador1, jogador2)

        elif escolha == 2:
            self.inverter_jogador_bloqueado()
            self.real_envido(cbr, self.jogador_bloqueado, jogador1, jogador2)
        
        else:
            self.inverter_jogador_bloqueado()
            self.falta_envido(cbr, self.jogador_bloqueado, jogador1, jogador2)

        
    def real_envido(self, cbr, quem_pediu, jogador1, jogador2):
        self.estado_atual = 7
        self.valor_envido = 5
        print("Jogador pediu Real Envido")

        if (quem_pediu == 1):
            # self.jogador_pediu_real_envido = 1
            escolha = jogador2.avaliar_envido(cbr, self.estado_atual, 1, self.jogador2_pontos)

        else:
            # self.jogador_pediu_real_envido = 2
            escolha = -1
            while(escolha not in [0, 1, 2]):
                escolha = int(input(f"Jogador {quem_pediu}, você aceita o pedido de Real envido?\n[0] Recusar\n[1] Aceitar\n[2] Falta Envido"))
        

        if escolha == 0:
            print(f"Fugiu do Real Envido!")
            if (quem_pediu == 1):
                jogador1.pontos += 2
                self.quem_fugiu = 2

            else:
                jogador2.pontos += 2
                self.quem_fugiu = 1

            return

        elif escolha == 1:
            print('Jogador aceitou Real envido!')
            self.avaliar_vencedor_envido(quem_pediu, jogador1, jogador2)

        else:
            self.inverter_jogador_bloqueado()
            self.falta_envido(cbr, self.jogador_bloqueado, jogador1, jogador2)


    def falta_envido(self, cbr, quem_pediu, jogador1, jogador2):
        self.estado_atual = 8
        if (quem_pediu == 1):
            print(1)
            self.valor_envido = 12 - jogador2.pontos

        else:
            print(2)
            self.valor_envido = 12 - jogador1.pontos
        print("Jogador pediu Falta Envido!")

        if (quem_pediu == 1):
            self.jogador_pediu_envido = 1
            escolha = jogador2.avaliar_envido(cbr, self.estado_atual, 1, self.jogador2_pontos)

        else:
            self.jogador_pediu_envido = 2
            escolha = -1
            while(escolha not in [0, 1]):
                escolha = int(input(f"Jogador {quem_pediu}, você aceita o pedido de envido?\n[0] Recusar\n[1] Aceitar\n"))
        

        if escolha == 0:
            print(f"Fugiu do falta envido!")
            if (quem_pediu == 1):
                jogador1.pontos += 5
                self.quem_fugiu = 2

            else:
                jogador2.pontos += 5
                self.quem_fugiu = 1

            return False

        else:
            print('Aceitou Falta envido!')
            self.avaliar_vencedor_falta_envido(quem_pediu, jogador1, jogador2)

    
    def avaliar_vencedor_envido(self, quem_pediu, jogador1, jogador2):
        if self.jogador1_pontos >= self.jogador2_pontos:
            jogador1.pontos += self.valor_envido
            self.quem_venceu_envido = 1

        elif self.jogador2_pontos > self.jogador1_pontos:
            jogador2.pontos += self.valor_envido
            self.quem_venceu_envido = 2
        

    def avaliar_vencedor_falta_envido(self, quem_pediu, jogador1, jogador2):
        if self.jogador1_pontos >= self.jogador2_pontos:
            print(3)
            jogador1.pontos += self.valor_envido
            self.quem_venceu_envido = 1

        else:
            print(4)
            jogador2.pontos += self.valor_envido
            self.quem_venceu_envido = 2


    def definir_pontos_jogadores(self, jogador1, jogador2):
        self.jogador1_pontos = jogador1.retorna_pontos_envido()
        self.jogador2_pontos = jogador2.retorna_pontos_envido()


    def retornar_quem_fugiu(self):
        return self.quem_fugiu


    def resetar(self):
        self.valor_envido = 2
        self.estado_atual = 0
        self.jogador_pediu_envido = 0
        self.quem_real_envido = 0
        self.quem_falta_envido = 0
        self.quem_fugiu = 0
        self.quem_venceu_envido = 0
        self.jogador_bloqueado = 0
        self.jogador1_pontos = 0
        self.jogador2_pontos = 0