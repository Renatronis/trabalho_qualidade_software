class Truco():
    def __init__(self):
        self.valor_aposta = 1
        self.jogador_bloqueado = 0
        self.jogador_pediu = 0
        self.jogador_retruco = 0
        self.jogador_vale_quatro = 0
        self.jogador_fugiu = 0
        self.estado_atual = ""


    def inverter_jogador_bloqueado(self):
        """Lógica para impedir que o mesmo jogador não peça o aumento de aposta seguidamente."""
        if (self.jogador_bloqueado == 1):
            self.jogador_bloqueado = 2
        
        else:
            self.jogador_bloqueado = 1


    def inicializar_jogador_bloqueado(self, quem_pediu):
        """Inicialização do jogador que foi bloqueado e não pode pedir aumento da aposta do jogo."""
        self.jogador_bloqueado = quem_pediu


    def controlador_truco(self, cbr, dados, quem_pediu, jogador1, jogador2):
        """Controlador de métodos, para selecionar o que pode ser chamado ou não."""
        if (self.estado_atual == "vale_quatro"):
            return None

        if (quem_pediu == self.jogador_bloqueado):
            return None
        else:
            self.inicializar_jogador_bloqueado(quem_pediu)

        if (self.estado_atual == ""):
            estado = self.pedir_truco(cbr, quem_pediu, jogador1, jogador2)

        elif (self.estado_atual == "truco"):
            estado = self.pedir_retruco(cbr, quem_pediu, jogador1, jogador2)

        elif (self.estado_atual == "retruco"):
            estado = self.pedir_retruco(cbr, quem_pediu, jogador1, jogador2)
            
        else:
            return None

        return estado


    def pedir_truco(self, cbr, quem_pediu, jogador1, jogador2):
        """Aumenta a aposta inicial do jogo, que passa a valer 2 pontos."""
        print("Truco")
        self.estado_atual = "truco"

        if (quem_pediu == 1):
            escolha = jogador2.avaliar_truco(cbr, self.estado_atual, quem_pediu)
            self.jogador_bloqueado = 1

        else:
            escolha = -1
            while(escolha not in [0, 1, 2]):
                escolha = int(input(f"{quem_pediu}, você aceita o pedido (a mão passa a valer {(self.valor_aposta)} pontos)\n[0] Recusar\n[1] Aceitar\n[2] Aumentar Aposta"))
            self.jogador_bloqueado = 2
        

        if escolha == 0:
            if (quem_pediu == 1):
                jogador1.pontos += 1

            else:
                jogador2.pontos += 1

            return False

        elif escolha == 1:
            print(f"Jogador {quem_pediu} aceitou o pedido.")
            # self.valor_aposta += self.valor_aposta
            return True
                
        elif escolha == 2:
            print(f"Jogador {quem_pediu} pediu Retruco.")
            self.inverter_jogador_bloqueado()
            return self.pedir_retruco(cbr, self.jogador_bloqueado, jogador1, jogador2)


    def pedir_retruco(self, cbr, quem_pediu, jogador1, jogador2):
        """Aumenta a aposta, que passa a valer 3 pontos."""
        self.valor_aposta = 3
        self.estado_atual = "retruco"
        print("Retruco")

        if (quem_pediu == 1):
            escolha = jogador2.avaliar_truco(cbr, self.estado_atual, quem_pediu)
            self.jogador_bloqueado = 1

        else:
            escolha = -1
            while(escolha not in [0, 1, 2]):
                escolha = int(input(f"Jogador {quem_pediu}, você aceita o pedido (a mão passa a valer {(self.valor_aposta)} pontos)\n[0] Recusar\n[1] Aceitar\n[2] Aumentar Aposta"))
            self.jogador_bloqueado = 2
        

        if escolha == 0:
            if (quem_pediu == 1):
                jogador1.pontos += 2

            else:
                jogador2.pontos += 2

            return False

        elif escolha == 1:
            print(f"Jogador {quem_pediu} aceitou o pedido.")
            # self.valor_aposta += self.valor_aposta
            return True
                
        elif escolha == 2:
            print(f"Jogador {quem_pediu} pediu Retruco.")
            self.inverter_jogador_bloqueado()
            return self.pedir_vale_quatro(cbr, self.jogador_bloqueado, jogador1, jogador2)


    def pedir_vale_quatro(self, cbr, quem_pediu, jogador1, jogador2):
        """Aumenta a aposta, que passa a valer 4 pontos"""
        self.valor_aposta = 4
        print("Vale 4")

        if (quem_pediu == 1):
            escolha = jogador2.avaliar_truco(cbr, self.estado_atual, quem_pediu)
            self.jogador_bloqueado = 1

        else:
            escolha = -1
            while(escolha not in [0, 1]):
                escolha = int(input(f"Jogador {quem_pediu}, você aceita o pedido (a mão passa a valer {(self.valor_aposta)} pontos)\n[0] Recusar\n[1] Aceitar"))
            self.jogador_bloqueado = 2
        

        if escolha == 0:
            if (quem_pediu == 1):
                jogador1.pontos += 3

            else:
                jogador2.pontos += 3

            return False

        else:
            print(f"Jogador {quem_pediu} aceitou o pedido.")
            jogador1.pediu_truco = True
            jogador2.pediu_truco = True
            # self.valor_aposta += self.valor_aposta
            return True


    def retornar_valor_aposta(self):
        """Retorna o valor atual de pontos (normal, truco, retruco, vale quatro)."""
        return self.valor_aposta


    def retornar_quem_fugiu(self):
        """Retorna o jogador que fugiu do truco."""
        return self.retornar_quem_fugiu
    
    
    def resetar(self):
        """Reset dos pontos da classe truco."""
        self.valor_aposta = 1
        self.jogador_bloqueado = 0
        self.jogador_pediu = 0
        self.jogador_aumentou2 = 0
        self.jogador_aumentou4 = 0
        self.jogador_fugiu = 0
        self.estado_atual = ""
