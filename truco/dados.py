import pandas as pd
import os

class Dados():
    def __init__(self):
        self.colunas = ['idMao', 'jogadorMao', 'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo', 'cartaAltaHumano', 'cartaMediaHumano', 'cartaBaixaHumano', 'primeiraCartaRobo', 'primeiraCartaHumano', 'segundaCartaRobo', 'segundaCartaHumano', 'terceiraCartaRobo', 'terceiraCartaHumano', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada', 'quemPediuEnvido', 'quemPediuFaltaEnvido', 'quemPediuRealEnvido', 'pontosEnvidoRobo', 'pontosEnvidoHumano', 'quemNegouEnvido', 'quemGanhouEnvido', 'quemFlor', 'quemContraFlor', 'quemContraFlorResto', 'quemNegouFlor', 'pontosFlorRobo', 'pontosFlorHumano', 'quemGanhouFlor', 'quemEscondeuPontosEnvido', 'quemEscondeuPontosFlor', 'quemTruco', 'quemRetruco', 'quemValeQuatro', 'quemNegouTruco', 'quemGanhouTruco','quemEnvidoEnvido', 'quemFlor', 'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo', 'naipeCartaAltaHumano', 'naipeCartaMediaHumano', 'naipeCartaBaixaHumano', 'naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano', 'naipeSegundaCartaRobo', 'naipeSegundaCartaHumano', 'naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano', 'qualidadeMaoRobo', 'qualidadeMaoHumano']
        self.registro = self.carregar_modelo_zerado()
        self.casos = self.tratamento_inicial_df()

    def tratamento_inicial_df(self):
        """Tratamento de dados do dataframe que será utilizado para alimentar a base de casos"""
        df = pd.read_csv('dbtrucoimitacao_maos.csv', usecols=self.colunas, index_col='idMao').fillna(-100)
        colunas_string = [
            'naipeCartaAltaRobo', 'naipeCartaMediaRobo','naipeCartaBaixaRobo', 'naipeCartaAltaHumano','naipeCartaMediaHumano', 'naipeCartaBaixaHumano','naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano',	'naipeSegundaCartaRobo', 'naipeSegundaCartaHumano','naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano',
            ]
        colunas_int = [col for col in df.columns if col not in colunas_string]
        df.replace('ESPADAS', '1', inplace=True)
        df.replace('OURO', '2', inplace=True)
        df.replace('BASTOS', '3', inplace=True)
        df.replace('COPAS', '4', inplace=True)
        df[colunas_string] = df[colunas_string].fillna(-66)
        # df.loc[:, df.dtypes == object] = df.loc[:, df.dtypes == object].astype(int)
        # df = df[df.columns].astype(int)
        df[colunas_int] = df[colunas_int].astype('int16')
        # df = df[colunas_int] > 0 # Desativar essa condição para obter um Bot que vai mais vezes ao baralho
        return df


    def cartas_jogadas_pelo_bot(self, rodada, carta_robo):
        """Adicionada as cartas jogadas pelo bot a base de casos"""
        if (rodada == 'primeira'):
            self.registro.primeiraCartaRobo = carta_robo.retornar_numero()
            self.registro.naipePrimeiraCartaRobo = carta_robo.retornar_naipe_codificado()
        
        if (rodada == 'segunda'):
            self.registro.segundaCartaRobo = carta_robo.retornar_numero()
            self.registro.naipeSegundaCartaRobo = carta_robo.retornar_naipe_codificado()

        if (rodada == 'terceira'):
            self.registro.terceiraCartaRobo = carta_robo.retornar_numero()
            self.registro.naipeTerceiraCartaRobo = carta_robo.retornar_naipe_codificado()

    def primeira_rodada(self, pontuacao_cartas, mao_rank, qualidade_mao_bot, carta_humano):
        """Adiciona na base de casos as cartas jogadas pelo bot na primeira rodada"""
        self.registro.jogadorMao = 1
        self.registro.cartaAltaRobo = pontuacao_cartas[mao_rank.index("Alta")]
        self.registro.cartaMediaRobo = pontuacao_cartas[mao_rank.index("Media")]
        self.registro.cartaBaixaRobo = pontuacao_cartas[mao_rank.index("Baixa")]
        # self.registro.ganhadorPrimeiraRodada = 2
        # self.registro.ganhadorSegundaRodada = 2
        # self.registro.ganhadorTerceiraRodada = 2
        self.registro.qualidadeMaoBot = qualidade_mao_bot
        self.registro.primeiraCartaHumano = carta_humano.retornar_numero()
        self.registro.naipePrimeiraCartaHumano = carta_humano.retornar_naipe_codificado()


    def segunda_rodada(self, primeira_carta_humano, primeira_carta_robo, ganhador_primeira_rodada):
        """Adiciona na base de casos as cartas jogadas pelo oponente na segunda rodada"""
        self.registro.ganhadorPrimeiraRodada = ganhador_primeira_rodada
        self.registro.primeiraCartaHumano = primeira_carta_humano.retornar_numero()
        self.registro.naipePrimeiraCartaHumano = primeira_carta_humano.retornar_naipe_codificado()
        self.registro.terceiraCartaRobo = primeira_carta_robo.retornar_numero()
        self.registro.terceiraCartaRobo = primeira_carta_robo.retornar_numero()

    

    def terceira_rodada(self, segunda_carta_humano, segunda_carta_robo, ganhador_segunda_rodada):
        """Adiciona na base de casos as cartas jogadas pelo oponente na segunda rodada"""
        self.registro.ganhadorSegundaRodada = ganhador_segunda_rodada
        self.registro.SegundaCartaHumano = segunda_carta_humano.retornar_numero()
        self.registro.naipeSegundaCartaHumano = segunda_carta_humano.retornar_naipe_codificado()
        self.registro.terceiraCartaRobo = segunda_carta_robo.retornar_numero()
        self.registro.terceiraCartaRobo = segunda_carta_robo.retornar_numero()



    def finalizar_rodadas(self, terceira_carta_humano, terceira_carta_robo, ganhador_terceira_rodada):
        """Adiciona na base de casos as cartas jogadas pelo oponente na terceira rodada"""
        self.registro.ganhadorTerceiraRodada = ganhador_terceira_rodada
        self.registro.terceiraCartaHumano = terceira_carta_humano.retornar_numero()
        self.registro.naipeTerceiraCartaHumano = terceira_carta_humano.retornar_naipe_codificado()
        self.registro.terceiraCartaRobo = terceira_carta_humano.retornar_numero()
        self.registro.terceiraCartaRobo = terceira_carta_humano.retornar_numero()



    def envido(self, quem_envido, quem_real_envido, quem_falta_envido, quem_ganhou_envido):
        """Adiciona na base de casos as informações referentes ao envido"""
        self.registro.quemEnvido = quem_envido
        self.registro.quemRealEnvido = quem_real_envido
        self.registro.quemFaltaEnvido = quem_falta_envido
        self.registro.quemGanhouEnvido = quem_ganhou_envido


    def truco(self, quem_truco, quem_retruco, quem_vale_quatro, quem_negou_truco, quem_ganhou_truco):
        """Adiciona na base de casos as informações referentes ao truco"""
        self.registro.quemTruco = quem_truco
        self.registro.quemRetruco = quem_retruco
        self.registro.quemValeQuatro = quem_vale_quatro
        self.registro.quemNegouTruco = quem_negou_truco
        self.registro.quemGanhouTruco = quem_ganhou_truco



    def flor(self, quem_flor, quem_contraflor, quem_contraflor_resto, pontos_flor_robo):
        """Adiciona na base de casos as informações referentes a flor"""
        self.registro.quemGanhouFlor = 2
        self.registro.quemFlor = quem_flor
        self.registro.quemContraFlor = quem_contraflor
        self.registro.quemContraFlorResto = quem_contraflor_resto
        self.registro.pontosFlorRobo = pontos_flor_robo
    

    def vencedor_envido(self, quem_ganhou_envido, quem_negou_envido):
        """Adiciona na base de casos as informações referentes ao truco"""
        self.registro.quemGanhouEnvido = quem_ganhou_envido
        self.registro.quemNegouEnvido = quem_negou_envido


    def vencedor_truco(self, quem_ganhou_truco, quem_negou_truco):
        """Adiciona na base de casos as informações referentes ao vencedor do truco"""
        self.registro.quemNegouTruco = quem_negou_truco
        self.registro.quemGanhouTruco = quem_ganhou_truco


    def vencedor_flor(self, quem_ganhou_flor, quem_negou_flor):
        """Adiciona na base de casos as informações referentes ao vencedor da flor"""
        self.registro.quemGanhouFlor = quem_ganhou_flor
        self.registro.quemNegouFlor = quem_negou_flor


    def carregar_modelo_zerado(self):
        """Carrega um dataframe zerado, para ser utilizado como modelo de caso."""
        return pd.read_csv('modelo_registro.csv', usecols=self.colunas, index_col='idMao')


    def retornar_registro(self):
        """Retorna o registro modelo de caso."""
        return self.registro
   

    def retornar_casos(self):
        """Retorna os casos."""
        return self.casos
    
   
    def finalizar_partida(self):
        """Método para salvar as jogadas da partida em um csv."""
        if not(os.path.isfile('jogadas.csv')):
            self.registro.to_csv('jogadas.csv', header=self.registro.columns)
        else:
            self.registro.to_csv('jogadas.csv', mode='a', header=False)


    def resetar(self):
        """Resetar variáveis ligadas a rodada."""
        self.casos = self.tratamento_inicial_df()
        self.registro = self.carregar_modelo_zerado()