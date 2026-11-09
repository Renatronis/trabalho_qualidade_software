from .carta import Carta
import random


class Baralho():
    
    def __init__(self):
        # self.vira = []
        self.manilhas = []
        self.cartas = []
        self.criar_baralho() 

    def criar_baralho(self):
        """Cria o baralho baseado nos 4 diferentes naipes, removendo cartas de 8 a 10."""
        for i in ["ESPADAS", "OUROS", "COPAS", "BASTOS"]:
            for n in range(1, 13):
                if n < 8 or n >= 10:
                    self.cartas.append(Carta(n, i))
    
    def embaralhar(self):
        """Embaralha o baralho de forma aleatõria."""
        random.shuffle(self.cartas)

    def retirar_carta(self):
        """Retira uma carta quando o jogador for receber as cartas na mesa."""
        return self.cartas.pop()
    
    def resetar(self):
        """Resetar variáveis ligadas ao baralho."""
        self.vira = []
        self.manilhas = []
        self.cartas = []
    
    def printar_baralho(self):
        """Exibe o baralho inteiro."""
        for c in self.cartas:
            c.exibir_carta()