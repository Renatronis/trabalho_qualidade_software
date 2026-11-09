class Flor():
    def __init__(self):
        self.valor_flor = 3
        self.quem_pediu_flor = 0
        self.quem_pediu_contraflor = 0
        self.quem_pediu_contraflor_resto = 0
        self.quem_venceu_flor = 0
        self.estado_atual = ""


    def pedir_flor(self, quem_pediu, jogador1, jogador2, interface):
        """Pedido de flor, permitindo controlar os métodos de contraflor ou contraflor e resto."""
        if (self.estado_atual != ""):
            return
            
        else:
            self.estado_atual = "Flor"

        if (quem_pediu == 2):
            jogador2.pediu_flor = True

        else:
            jogador1.pediu_flor = True
            
        if (jogador1.flor and jogador2.flor):
            if (jogador2.pontos < int((jogador1.pontos/1.5))):
                self.estado_atual = "Contraflor e Resto"
                if self.decisao_jogador(): 
                    self.contraflor_resto(2, jogador1, jogador2)

                else:
                    jogador2.pontos += 4

            else: 
                self.estado_atual = "Contraflor"
                if self.decisao_jogador(): 
                    self.contraflor(2, jogador1, jogador2)

                else:
                    jogador2.pontos += 4
            
        elif (jogador1.flor):
            jogador1.pontos += self.valor_flor
            self.quem_venceu_flor = 1
        
        elif (jogador2.flor):
            jogador2.pontos += self.valor_flor
            self.quem_venceu_flor = 2

        interface.mostrar_vencedor_flor(self.quem_venceu_flor, jogador1.nome, jogador2.nome, self.valor_flor)
        # vencedor, jogador1, jogador2, pontos
        


    def contraflor(self, quem_pediu, jogador1, jogador2):
        self.valor_flor = 6
        jogador1_pontos = jogador1.retorna_pontos_envido()
        jogador2_pontos = jogador2.retorna_pontos_envido()

        if jogador1_pontos > jogador2_pontos:
            jogador1.pontos += self.valor_flor
            self.quem_venceu_flor = 1

        elif jogador2_pontos > jogador1_pontos:
            jogador2.pontos += self.valor_flor
            self.quem_venceu_flor = 2

        else:
            jogador1.pontos += self.valor_flor
            self.quem_venceu_flor = 1


    def contraflor_resto(self, quem_pediu, jogador1, jogador2):
        jogador1_pontos = jogador1.retorna_pontos_envido()
        jogador2_pontos = jogador2.retorna_pontos_envido()

        if (quem_pediu == 1):
            self.valor_envido = self.valor_flor

        else:
            self.valor_envido = self.valor_flor

        if jogador1_pontos >= jogador2_pontos:
            jogador1.pontos += self.valor_flor
            self.quem_venceu_flor = 1

        else:
            jogador2.pontos += self.valor_flor
            self.quem_venceu_flor = 2


    def decisao_jogador(self):
        escolha = -1
        while (escolha not in [0, 1]):
            escolha = int(input(f"Jogador 1, você aceita o pedido de {self.estado_atual}?\n[0] Não\n[1] Sim"))
        
        if (escolha == 0):
            return False
        
        else: 
            return True

    def resetar_flor(self):
        self.valor_flor = 3
        self.quem_pediu_flor = 0
        self.quem_pediu_contraflor = 0
        self.quem_pediu_contraflor_resto = 0
        self.quem_venceu_flor = 0
        self.estado_atual = ""