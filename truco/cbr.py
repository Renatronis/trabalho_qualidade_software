from sklearn.neighbors import NearestNeighbors
import pandas as pd
import warnings
from .dados import Dados

class Cbr():
    def __init__(self):
        self.indice = 0
        self.dados = Dados()
        self.dataset = self.dados.retornar_casos()
        # self.dados = self.retornarSimilares()
        self.nbrs = self.vizinhos_proximos()


    def carregar_dataset(self):
        """Carrega o dataset, caso necessário"""
        df = pd.read_csv('dbtrucoimitacao_maos.csv', index_col='idMao').fillna(-100)
        df.replace('ESPADAS', '1', inplace=True)
        df.replace('OURO', '2', inplace=True)
        df.replace('BASTOS', '3', inplace=True)
        df.replace('COPAS', '4', inplace=True)
        return df


    def vizinhos_proximos(self, df=None):
        """Cálculo dos 100 Nearest Neighbors."""
        if (df is None):
            return NearestNeighbors(n_neighbors=100, algorithm='ball_tree').fit(self.dataset)
            
        return NearestNeighbors(n_neighbors=100, algorithm='ball_tree').fit(df)


    def jogar_carta(self, rodada, pontuacao_cartas):
        """Método que considera as jogadas em que o bot saiu vitorioso e retorna a pontuação mais próxima a ser jogada em determinada rodada."""
        registro = self.dados.retornar_registro()
        warnings.simplefilter(action='ignore', category=UserWarning)
        distancias, indices = self.nbrs.kneighbors((registro.to_numpy().reshape(1, -1)))
        jogadas_vencidas = self.dataset.iloc[indices.tolist()[0]]
        jogadas_vencidas = jogadas_vencidas[(((jogadas_vencidas.ganhadorPrimeiraRodada == 2) & ((jogadas_vencidas.ganhadorSegundaRodada == 2)) | (jogadas_vencidas.ganhadorPrimeiraRodada == 2)) & (jogadas_vencidas.ganhadorTerceiraRodada == 2) | ((jogadas_vencidas.ganhadorSegundaRodada == 2) & (jogadas_vencidas.ganhadorTerceiraRodada == 2)))]
        ordem_carta_jogada = 'CartaRobo'
        if ((rodada) == 3): ordem_carta_jogada = 'primeira' + ordem_carta_jogada
        elif ((rodada) == 2): ordem_carta_jogada = 'segunda' + ordem_carta_jogada
        elif ((rodada) == 1): ordem_carta_jogada = 'terceira' + ordem_carta_jogada

        valor_referencia = jogadas_vencidas[ordem_carta_jogada].value_counts().index.to_list()[0]
        if (valor_referencia <= 0): 
            return -1

        carta_escolhida = min(pontuacao_cartas, key=lambda x:abs(x-valor_referencia))
        # print(jogadas_vencidas[ordem_carta_jogada].value_counts())
        # print(pontuacao_cartas)
        # print(carta_escolhida)
        # return carta_escolhida
        return pontuacao_cartas.index(int(carta_escolhida))

    def truco(self, tipo, quem_pediu, qualidade_mao_bot):
        """Método que considera o pedido de truco e retorna a melhor opção entre aceitar, aumentar ou fugir."""
        registro = self.dados.retornar_registro()
        warnings.simplefilter(action='ignore', category=UserWarning)
        distancias, indices = self.nbrs.kneighbors((registro.to_numpy().reshape(1, -1)))
        jogadas = perdidas = self.dataset.iloc[indices.tolist()[0]]
        jogadas = jogadas[(jogadas.quemGanhouTruco == 2)]
        perdidas = perdidas[(perdidas.quemGanhouTruco == 1)]

        vencidas = jogadas['quemGanhouTruco'].value_counts().index.to_list()[0]
        perdidas = perdidas['quemGanhouTruco'].value_counts().index.to_list()[0]
        retruco = jogadas['quemRetruco'].value_counts().index.to_list()[0]
        qualidade_mao_humana = jogadas['qualidadeMaoHumano'].dropna().value_counts().index.to_list()[0]


        if (vencidas > perdidas and qualidade_mao_bot > qualidade_mao_humana):
            return 2
        
        elif (qualidade_mao_bot > qualidade_mao_humana):
            return 1
        
        else:
            return 0


    def envido(self, tipo, quem_pediu, pontos_envido_robo, robo_perdendo=None):
        """Método que considera o pedido de envido e retorna a melhor opção entre aceitar, pedir real envido, falta envido ou fugir."""
        registro = self.dados.retornar_registro()
        warnings.simplefilter(action='ignore', category=UserWarning)
        distancias, indices = self.nbrs.kneighbors((registro.to_numpy().reshape(1, -1)))
        jogadas = self.dataset.iloc[indices.tolist()[0]]
        ganhas = jogadas[((jogadas.pontosEnvidoRobo > jogadas.pontosEnvidoHumano) | (jogadas.quemGanhouEnvido == 2))]
        perdidas = jogadas[((jogadas.pontosEnvidoRobo < jogadas.pontosEnvidoHumano) | (jogadas.quemGanhouEnvido == 1))]
        # 'quemPediuEnvido', 'quemPediuFaltaEnvido', 'quemPediuRealEnvido', 'pontosEnvidoRobo', 'pontosEnvidoHumano', 'quemNegouEnvido', 'quemGanhouEnvido', 'quemEscondeuPontosEnvido'
        # print(jogadas)
        envido_ganhas = ganhas['quemGanhouEnvido'].value_counts().index.to_list()[0]
        envido_perdidas = perdidas['quemGanhouEnvido'].value_counts().index.to_list()[0]
        real_envido_ganhas = ganhas['quemPediuRealEnvido'].value_counts().index.to_list()[0]
        real_envido_perdidas = perdidas['quemPediuFaltaEnvido'].value_counts().index.to_list()[0]
        falta_envido_ganhas = ganhas['quemPediuFaltaEnvido'].value_counts().index.to_list()[0]
        falta_envido_perdidas = perdidas['quemPediuFaltaEnvido'].value_counts().index.to_list()[0]
        pontos_jogador = ganhas['pontosEnvidoHumano'].value_counts().index.to_list()[0]

        # Condição especial quando o robô considera pedir o envido na primeira jogada
        if (quem_pediu == 2 and pontos_envido_robo > 5):
            if (pontos_jogador < pontos_envido_robo and real_envido_ganhas > real_envido_perdidas and envido_ganhas > envido_perdidas):
                if (robo_perdendo):
                    return 8

                return 7
            
            elif (envido_ganhas > envido_perdidas or envido_ganhas < envido_perdidas):
                if (robo_perdendo):
                    return 8

                return 6

        if (tipo == 6):
            if (pontos_jogador < pontos_envido_robo and real_envido_ganhas > real_envido_perdidas and envido_ganhas > envido_perdidas):
                return 2

            elif (real_envido_ganhas > real_envido_perdidas and envido_ganhas > envido_perdidas and robo_perdendo):
                return 3

            elif (envido_ganhas > envido_perdidas or envido_ganhas < envido_perdidas):
                return 1

            else:
                return 0

        elif (tipo == 7):
            if ((pontos_jogador < pontos_envido_robo) or (envido_ganhas > envido_perdidas and real_envido_ganhas > real_envido_perdidas)):
                return 1

            else:
                return 0

        else:
            if ((pontos_jogador < pontos_envido_robo) or falta_envido_ganhas > falta_envido_perdidas and pontos_jogador < pontos_envido_robo):
                return 1

            else:
                return 0