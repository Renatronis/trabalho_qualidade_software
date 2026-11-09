class Jogador():
    def __init__(self, nome):
        self.nome = nome
        self.mao = []
        self.mao_rank = []
        self.pontos = 0
        self.rodadas = 0
        self.envido = 0
        self.primeiro = False
        self.ultimo = False
        self.flor = False
        self.pediu_flor = False
        self.pediu_truco = False


    def mostrar_opcoes(self, interface):
        """Mostrar as opções que o jogador pode jogar"""
        # print(f'pontos self.envido: {self.envido}')
        self.mostrar_mao(interface)
        if (len(self.mao) >= 2 and self.pediu_truco is False): 
            print('[4] Truco')

        if ((len(self.mao)) == 3 and self.flor is False and (self.checa_flor())):
            print('[5] Flor')
            self.flor = True

        if ((len(self.mao) == 3)):
            print(f'[6] Envido\n[7] Real Envido\n[8] Falta Envido')

        print('[9] Ir ao baralho')
        cartas = [(f"{carta.numero} de {carta.naipe}") for carta in self.mao]
        # interface.exibir_cartas(cartas)
        # interface.exibir_unica_carta(cartas[0])


    def criar_mao(self, baralho):
        """Cria a mão do jogador e insere três cartas do baralho a ela."""
        for i in range(3):
            self.mao.append(baralho.retirar_carta())

        self.envido = self.calcula_envido(self.mao)


    def jogar_carta(self, carta_escolhida):
        """Joga a carta, removendo da mão do jogador."""
        return self.mao.pop(carta_escolhida)
    

    def mostrar_mao(self, interface):
        """Exibe as cartas que o jogador possui na mão."""
        i = 0
        for carta in self.mao:
            carta.exibir_carta(i)
            i += 1


    def adicionar_pontos(self, pontos):
        """Adiciona pontos a pontuação acumulada do jogador."""
        self.pontos += pontos


    def adicionar_rodada(self):
        """Adiciona uma rodada ganha ao jogador."""
        self.rodadas += 1


    def checa_mao(self):
        """Retorna todas as cartas na mão do Jogador."""
        return self.mao
    

    def calcula_envido(self, mao):
        """Realização do cálculo de envido."""
        pontos_envido = []

        for i in range(len(mao)):
            for j in range(i+1, len(mao)):
                if ((mao[i].retornar_naipe() == mao[j].retornar_naipe())):
                    if (mao[0].retornar_pontos_envido(mao[i]) > 0 and mao[0].retornar_pontos_envido(mao[j]) > 0):
                        pontos_envido.append(20 + (mao[0].retornar_pontos_envido(mao[i]) + mao[0].retornar_pontos_envido(mao[j])))
                    
                    else:
                        pontos_envido.append(0)
                
                else:
                    pontos_envido.append(max(mao[0].retornar_pontos_envido(mao[i]), mao[0].retornar_pontos_envido(mao[j])))
        
        return max(pontos_envido)
    
    
    def checa_flor(self):
        """Verifica se o jogador possui flor em sua mão."""
        if all(carta.retornar_naipe() == self.mao[0].retornar_naipe() for carta in self.mao):
            # print('Flor do Jogador')
            return True
            
        return False

    
    def retorna_pontos_envido(self):
        """Retorna os pontos do envido."""
        return self.envido

    def retorna_pontos_totais(self):
        """Retorna os pontos totais do jogador."""
        return self.pontos

    def resetar(self):
        """Resetar variáveis ligadas a rodada."""
        self.rodadas = 0
        self.mao = []
        self.flor = False
        self.pediu_truco = False