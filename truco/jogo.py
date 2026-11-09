from .baralho import Baralho
from .jogador import Jogador
from .bot import Bot
from .pontos import MANILHA, CARTAS_VALORES
import random

class Jogo():
    def __init__(self):
        self.rodadas = []
        self.trucoPontos = 1
    

    def iniciarJogo(self):
        pass


    def criar_jogador(self, nome, baralho):
        """Criação do jogador, baseado em sua própria classe"""
        jogador = Jogador(nome)
        jogador.criar_mao(baralho)
        return jogador


    def criar_bot(self, nome, baralho):
        """Criação do bot, baseado em sua própria classe"""
        bot = Bot(nome)
        bot.criar_mao(baralho)
        return bot


    def verificar_ganhador(self, carta1, carta2, interface):
        """Função que chama o método para verificar a carta vencedora"""
        ganhador = self.verificar_carta_vencedora(carta1, carta2)
        interface.mostrar_carta_ganhadora(ganhador)
        return ganhador

    
    def adicionar_rodada(self, jogador1, jogador2, carta1, carta2, ganhador):
        """Adição da rodada para cada jogador"""
        # if ganhador == "Empate":
        #     jogador1.adicionar_rodada()
        #     jogador2.adicionar_rodada()
        #     return "Empate"
        
        if (ganhador == carta1):
            jogador1.adicionar_rodada()
            return 1
            # ganhador.adicionar_rodada()
        
        elif (ganhador == carta2):
            jogador2.adicionar_rodada()
            return 2
            # ganhador.adicionar_rodada()
        
        else:
            return "Erro"


    def quem_joga_primeiro(self, jogador1, jogador2, carta1, carta2, ganhador):
        """Definição de quem joga primeiro, a cada round"""
        if (carta1 == ganhador):
            jogador1.primeiro = True
            jogador2.primeiro = False
        
        elif (carta2 == ganhador):
            jogador1.primeiro = False
            jogador2.primeiro = True
        
        # elif ganhador == "Empate":
        #     pass


    def quem_inicia_rodada(self, jogador1, jogador2):
        """Seleção de quem inicia a rodada"""
        if (jogador1.rodadas == 0 and jogador2.rodadas == 0):
            if (jogador1.ultimo == True):
                jogador2.ultimo = True
                jogador1.ultimo = False
                jogador1.primeiro = True
                jogador2.primeiro = False
            
            elif (jogador2.ultimo == True):
                jogador2.ultimo = False
                jogador1.primeiro = False
                jogador2.primeiro = True


    def verificar_carta_vencedora(self, carta_jogador_01, carta_jogador_02):
        """Verifica a carta vencedora entre as duas cartas escolhidas"""
        if ((str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe) in MANILHA and (str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe) in MANILHA):
            if MANILHA[str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe] > MANILHA[str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe]:
                return carta_jogador_01
           
            elif (MANILHA[str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe] > MANILHA[str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe]):
                return carta_jogador_02
        
        elif ((str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe) in MANILHA):
            return carta_jogador_01
        
        elif ((str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe) in MANILHA):
            return carta_jogador_02
        
        else:
            if (CARTAS_VALORES[str(carta_jogador_01.numero)] >= CARTAS_VALORES[str(carta_jogador_02.numero)]):
                return carta_jogador_01
        
            elif (CARTAS_VALORES[str(carta_jogador_01.retornar_numero())] < CARTAS_VALORES[str(carta_jogador_02.retornar_numero())]):
                return carta_jogador_02
        
            # else:
            #     return "Empate"


    def jogador_fugiu(self, jogador, jogador1, jogador2, pontos):
        """Indicação de que o jogador fugiu, resetando a ordem de jogadas com o jogador 1 sendo mão"""
        print(f'Jogador fugiu!')
        jogador1.primeiro = True
        jogador2.primeiro = False