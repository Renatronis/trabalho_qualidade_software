#!/usr/bin/env python
# coding: utf-8

# # Colunas CBR
# Notebook utilizado para analisar as colunas que devem ser consideradas para cálculo de similaridade e utilização no CBR.

# In[2]:


import pandas as pd
import numpy as np


# In[2]:


colunas = ['jogadorMao', 'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo', 'cartaAltaHumano', 'cartaMediaHumano', 'cartaBaixaHumano', 'primeiraCartaRobo', 'primeiraCartaHumano', 'segundaCartaRobo', 'segundaCartaHumano', 'terceiraCartaRobo', 'terceiraCartaHumano', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada', 'quemPediuEnvido', 'quemPediuFaltaEnvido', 'quemPediuRealEnvido', 'pontosEnvidoRobo', 'pontosEnvidoHumano', 'quemNegouEnvido', 'quemGanhouEnvido', 'quemFlor', 'quemContraFlor', 'quemContraFlorResto', 'quemNegouFlor', 'pontosFlorRobo', 'pontosFlorHumano', 'quemGanhouFlor', 'quemEscondeuPontosEnvido', 'quemEscondeuPontosFlor', 'quemTruco', 'quemRetruco', 'quemValeQuatro', 'quemNegouTruco', 'quemGanhouTruco','quemEnvido', 'quemFlor', 'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo', 'naipeCartaAltaHumano', 'naipeCartaMediaHumano', 'naipeCartaBaixaHumano', 'naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano', 'naipeSegundaCartaRobo', 'naipeSegundaCartaHumano', 'naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano', 'qualidadeMaoRobo', 'qualidadeMaoHumano']


# In[3]:


pd.DataFrame(columns=colunas)


# In[12]:


df = pd.read_csv('dbtrucoimitacao_maos.csv', index_col='idMao')
colunas_string = [
    'naipeCartaAltaRobo', 'naipeCartaMediaRobo','naipeCartaBaixaRobo', 'naipeCartaAltaHumano','naipeCartaMediaHumano', 'naipeCartaBaixaHumano','naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano',	'naipeSegundaCartaRobo', 'naipeSegundaCartaHumano','naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano',
    ]
colunas_int = [col for col in df.columns if col not in colunas_string]

# df[colunas_int] = df[colunas_int].astype('int').apply(abs)
# df[colunas_int] = df[colunas_int].fillna(0)
# df[colunas_int] = df[colunas_int].astype('int')
# df[colunas_string] = df[colunas_string].any(axis=1)
# df[colunas_string] = df[colunas_string].apply(lambda x: print(x), axis=1)
# pd.get_dummies(df[colunas_string], prefix=colunas_string)
df.replace('ESPADAS', '1', inplace=True)
df.replace('OURO', '2', inplace=True)
df.replace('BASTOS', '3', inplace=True)
df.replace('COPAS', '4', inplace=True)
df[colunas_string] = df[colunas_string].fillna(0)
df[colunas_string] = df[colunas_string].astype('int16')


# In[13]:


df[colunas_string].info()


# In[16]:


df[colunas_int]


# In[1]:


from truco.dados import Dados
from truco.cbr import Cbr

dados = Dados()
cbr = Cbr()


# In[2]:


dados.retornar_registro()


# In[3]:


cbr.retornar_similares(dados.retornar_registro())


# In[6]:


rodada = 1


# In[34]:


df.info()


# In[46]:


df= cbr.dataset
# df = self.dados
df.loc[:, df.dtypes == object] = df.loc[:, df.dtypes == object].astype(int)
df = df[df.columns].astype(int)
df = df[df>0]
# cols = df.columns
# df = df.apply(lambda x: x > 0)
# df.apply(lambda x: list(cols[x.values]), axis=1)
pontuacao_cartas = [16, 46, 8]
ordem_carta_jogada = 'CartaRobo'
if ((rodada) == 3): ordem_carta_jogada = 'primeira' + ordem_carta_jogada
elif ((rodada) == 2): ordem_carta_jogada = 'segunda' + ordem_carta_jogada
elif ((rodada) == 1): ordem_carta_jogada = 'terceira' + ordem_carta_jogada

carta_escolhida = 0

# for i in reversed(range(len(df[ordem_carta_jogada].value_counts().index.to_list()))): 
#     aux = df[ordem_carta_jogada].value_counts().index.to_list()[i]
#     print(aux)
reversed(range(len(df[ordem_carta_jogada].value_counts().index.to_list())))
    
    # if (carta_escolhida in pontuacao_cartas):
    #     carta_escolhida = aux

if (carta_escolhida == 0):
    valor_referencia = df[ordem_carta_jogada].value_counts().index.to_list()[0]
    carta_escolhida = min(pontuacao_cartas, key=lambda x:abs(x-valor_referencia))


# In[47]:


df[ordem_carta_jogada].value_counts().index.to_list()[0]


# In[ ]:


# Teste de remoção de valores vazios
# df = self.dados
# cols = df.columns
# novo_df = df.apply(lambda x: x > 0)
# novo_df.apply(lambda x: list(cols[x.values]), axis=1)

