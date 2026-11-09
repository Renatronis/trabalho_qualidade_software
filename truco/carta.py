import itertools
from .pontos import MANILHA, CARTAS_VALORES, ENVIDO

class Carta():
    def __init__(self, numero, naipe):
        self.numero = numero
        self.naipe = naipe

    def verificar_carta_alta(self, carta_01, carta_02):
        """Verificação de qual carta é a carta mais alta, entre duas cartas."""
        if (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA and (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            if MANILHA[str(carta_01.numero)+" de "+carta_01.naipe] > MANILHA[str(carta_02.numero)+" de "+carta_02.naipe]:
                return carta_01
            elif MANILHA[str(carta_02.numero)+" de "+carta_02.naipe] > MANILHA[str(carta_01.numero)+" de "+carta_01.naipe]:
                return carta_02

        elif (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA:
            return carta_01

        elif (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            return carta_02

        else:
            if CARTAS_VALORES[str(carta_01.numero)] > CARTAS_VALORES[str(carta_02.numero)]:
                return carta_01
            else:
                return carta_02

        return carta_01


    def verificar_carta_baixa(self, carta_01, carta_02):
        """Verificação de qual é a carta mais baixa entre duas cartas."""
        if (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA and (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            if MANILHA[str(carta_01.numero)+" de "+carta_01.naipe] < MANILHA[str(carta_02.numero)+" de "+carta_02.naipe]:
                return carta_01

            elif MANILHA[str(carta_02.numero)+" de "+carta_02.naipe] < MANILHA[str(carta_01.numero)+" de "+carta_01.naipe]:
                return carta_02

        elif (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA:
            return carta_02

        elif (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            return carta_01

        else:
            if CARTAS_VALORES[str(carta_01.numero)] < CARTAS_VALORES[str(carta_02.numero)]:
                return carta_01

            else:
                return carta_02

        return carta_01

    
    def retornar_pontos_carta(self, carta):
        """Retorna a pontuação equivalente de determinada carta."""
        if (str(carta.numero)+" de "+carta.naipe) in MANILHA:
            return MANILHA[str(carta.numero)+" de "+carta.naipe]

        else:
            return CARTAS_VALORES[str(carta.numero)]


    def classificar_carta(self, cartas):
        """Método para classificar as cartas por ranks (alto, médio, baixo) e retorna a pontuação individual de cada carta."""
        carta_alta = self.verificar_carta_alta(self.verificar_carta_alta(cartas[0], cartas[1]), cartas[2])
        carta_baixa = self.verificar_carta_baixa(self.verificar_carta_baixa(cartas[0], cartas[1]), cartas[2])
        lista_classificacao = ['', '', '']
        lista_pontos = ['', '', '']
        
        for i in range(len(lista_classificacao)):
            if carta_alta == cartas[i]: 
                lista_pontos[i] = self.retornar_pontos_carta(cartas[i])
                lista_classificacao[i] = 'Alta'
            
            if carta_baixa == cartas[i]: 
                lista_pontos[i] = self.retornar_pontos_carta(cartas[i])
                lista_classificacao[i] = 'Baixa'
            
            if not lista_classificacao[i]: 
                lista_pontos[i] = self.retornar_pontos_carta(cartas[i])
                lista_classificacao[i] = 'Media'

        return lista_pontos, lista_classificacao


    def exibir_carta(self, i=None):
        """Exibe a carta a ser jogada e a opção para jogá-la."""
        if i == None:
            i = ""
        print(f"[{i}] {self.numero} de {self.naipe}")

    def retornar_carta(self):
        """Retorna o valor legível da carta, contendo o número e o naipe"""
        return f"{self.numero} de {self.naipe}"
    

    def retornar_pontos_envido(self, carta):
        """Retorna os pontos do envido para determinada carta, de acordo com a codificação."""
        return ENVIDO[str(carta.retornar_numero())]


    def retornar_numero(self):
        """Retorna o número de determinada carta."""
        return self.numero
    

    def retornar_naipe(self):
        """Retorna o naipe de determinada carta."""
        return self.naipe


    def retornar_naipe_codificado(self):
        naipe = self.naipe 
        if (naipe == 'ESPADAS'):
            return 1

        elif (naipe == 'OUROS'):
            return 2

        elif (naipe == 'BASTOS'):
            return 3
            
        elif (naipe == 'COPAS'):
            return 4
    
    # Codificação exemplo
    # df.replace('ESPADAS', '1', inplace=True)
    # df.replace('OURO', '2', inplace=True)
    # df.replace('BASTOS', '3', inplace=True)
    # df.replace('COPAS', '4', inplace=True)
