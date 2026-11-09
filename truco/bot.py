import random 
import pandas as pd

class Bot():
    def __init__(self, nome):
        self.nome = nome
        self.mao = []
        self.mao_rank = []
        self.indices = []
        self.pontuacao_cartas = []
        self.qualidade_mao = 0
        self.pontos = 0
        self.rodadas = 0
        self.envido = 0
        self.rodada = 1
        self.primeiro = False
        self.ultimo = False
        self.flor = False
        self.pediu_flor = False
        self.pediu_truco = False

    def criar_mao(self, baralho):
        """Cria a mão do jogador e insere três cartas do baralho a ela."""
        self.indices = [0, 1, 2]
        for i in range(3):
            self.mao.append(baralho.retirar_carta())

        self.flor = self.checa_flor()
        self.pontuacao_cartas, self.mao_rank = self.mao[0].classificar_carta(self.mao)
        self.calcular_qualidade_mao(self.pontuacao_cartas, self.mao_rank)
        self.envido = self.calcula_envido(self.mao)
        # print(self.mostrar_mao())


    def enriquecer_bot(self, dados=None, carta_jogador_01=None, carta_jogador_02=None, ganhador=None):
        """Enriquece os dados com cartas jogadas pelo oponente, que serão utilizadas como entrada para cálculo de similaridade."""
        if (self.rodada == 1):
            dados.primeira_rodada(self.pontuacao_cartas, self.mao_rank, self.qualidade_mao, carta_jogador_01)

        elif(self.rodada == 2):
            dados.segunda_rodada(carta_jogador_01, carta_jogador_02, ganhador)

        elif(self.rodada == 3):
            dados.terceira_rodada(carta_jogador_01, carta_jogador_02, ganhador)

        elif(self.rodada == 4):
            dados.finalizar_rodadas(carta_jogador_01, carta_jogador_02, ganhador)

    def enriquecer_cartas_bot(self, cbr, carta_jogador_02):
        """Enriquece os dados com cartas jogadas pelo bot, que serão utilizadas como entrada para cálculo de similaridade."""
        # CHAMADA DO CBR OU OUTRA INTELIGÊNCIA DEVE OCORRER AQUI
        cbr.enriquecer_jogadas_bot(carta_jogador_02)


    def jogar_carta(self, cbr, truco):
        """Joga a carta, removendo da mão do jogador."""
        # jogada = self.avaliar_jogada()
        # Envido
        # Flor
        if ((len(self.mao)) == 3 and self.flor is False and (self.checa_flor())):
            # CHAMADA DO CBR OU OUTRA INTELIGÊNCIA DEVE OCORRER AQUI
            flor = cbr.flor()
            if (flor is True):
                return 5

        # Pedir truco
        if (len(self.mao) <= 2 and self.pediu_truco is False):
            # CHAMADA DO CBR OU OUTRA INTELIGÊNCIA DEVE OCORRER AQUI
            truco = cbr.truco('truco', 1, self.qualidade_mao)
            if (truco is None):
                pass

            elif (truco in [1, 2]):
                self.pediu_truco = True
                return 4

        # Manda o valor de acordo com a rodada, para o CBR escolher as colunas/campos necessários
        # CHAMADA DO CBR OU OUTRA INTELIGÊNCIA DEVE OCORRER AQUI
        escolha = cbr.jogar_carta(self.rodada, self.pontuacao_cartas)
        # print(escolha)
        self.ajustar_indices(escolha)
        self.rodada += 1
        # Verificar cartas na mão antes de jogar
        return escolha
        # return self.mao.pop(escolha)


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
    


    def retorna_pontos_envido(self):
        """Retorna os pontos do envido."""
        return self.envido


    def ajustar_indices(self, i):
        """Ajusta os índices, para que bot possa ter opçoões de 0 até o tamanho da self.mao para jogar."""
        # print(f'\n{self.mao_rank},{self.indices},{self.pontuacao_cartas},{self.mao}')
        self.mao_rank.pop(i)
        self.indices.pop(i)
        self.pontuacao_cartas.pop(i)
        # self.mao.pop(i)


    def mostrar_mao(self):
        """Exibe as cartas na mão do bot."""
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
        """Retorna todas as cartas na mão do bot."""
        return self.mao


    def checa_flor(self):
        """Verifica se o bot possui flor em sua mão."""
        if all(carta.retornar_naipe() == self.mao[0].retornar_naipe() for carta in self.mao):
            # print('Flor do Bot!')
            return True

        return False


    def avaliar_truco(self, cbr, tipo, quem_pediu):
        """Verifica se a melhor jogada para o bot deve pedir, aceitar, recusar ou aumentar a aposta do truco."""
        # CHAMADA DO CBR OU OUTRA INTELIGÊNCIA DEVE OCORRER AQUI
        return cbr.truco(tipo, quem_pediu, self.qualidade_mao)
    

    def avaliar_envido(self, cbr, tipo, quem_pediu, pontos_totais_adversario):
        """Verifica se a melhor jogada para o bot seria aceitar, pedir real ou falta envido."""
        if (pontos_totais_adversario > 6 or pontos_totais_adversario > int((self.pontos/1.5))):
            # print(f'{pontos_totais_adversario} - {self.pontos}')
            perdendo = True
        
        else:
            perdendo = False

        # CHAMADA DO CBR OU OUTRA INTELIGÊNCIA DEVE OCORRER AQUI
        return cbr.envido(tipo, quem_pediu, self.envido, perdendo)

    def avaliar_pedir_envido(self):
        """Verifica se a melhor jogada para o bot seria pedir envido."""
        return 1


    def calcular_qualidade_mao(self, lista_pontuacao, lista_mao_rank):
        """Calcula a qualidade da mão do bot, baseado na média harmônica da codificação."""
        m1 = (2 / ((1/lista_pontuacao[int(lista_mao_rank.index('Alta'))]) + (1/lista_pontuacao[int(lista_mao_rank.index('Media'))])))
        m2 = ((2 * lista_pontuacao[int(lista_mao_rank.index('Media'))]) + (lista_pontuacao[int(lista_mao_rank.index('Baixa'))])/2+1)
        m3 = ((2 * m1) + m2) / (2+1)
        self.qualidade_mao = m3

    def retorna_pontos_totais(self):
        """Retorna os pontos totais do bot."""
        return self.pontos


    def resetar(self):
        """Resetar variáveis ligadas a rodada."""
        self.mao = []
        self.mao_rank = []
        self.indices = []
        self.pontuacao_cartas = []
        self.qualidade_mao = 0
        self.rodadas = 0
        self.envido = 0
        self.rodada = 1
        self.flor = False
        self.pediu_flor = False
        self.pediu_truco = False


'''
- Centralizar toda a CBR em uma unica função, que retorna qual seria o tipo de jogada;
- Quando necessário usar outra inteligência/agente, só substitui-la diretamente na classe bot.
'''        