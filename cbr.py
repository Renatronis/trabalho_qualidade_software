#!/usr/bin/env python
# coding: utf-8

# # Trabalho da Disciplina de Aplicações em Aprendizado de Máquina
# 
# Autor: Fábio Demo da Rosa

# ## Nearest Neighbors
# 
# O princípio por trás do vizinho mais próximo é encontrar um número pré-definido de amostras que podem ser definida por uma constante do usuário (K-Nearest Neighbor Learning) ou variar baseada na densidade de pontos locais.
# 
# Essa distância pode ser qualquer métrica, como por exemplo a Distância Euclidiana.
# 
# Métodos baseados nos vizinhos mais próximos são conhecidos como non-generalizing machine learning methods, já que eles somente lembram todos os dados de treino.
# 
# Apesar da simplificade, os vizinhos mais próximos tem sido bem-sucedidos em diversos problemas de classificação e regressão, como identificação de dígitos escritos a mão ou de classificação de imagens de satélite.

# In[6]:


from IPython.display import Image

Image(url='https://scikit-learn.org/stable/_images/sphx_glr_plot_classification_002.png')


# ## Case-Based Reasoning
# É uma forma de Inteligência Artificial (IA) usada para resolver novos problemas baseados em problemas (similares) passados.
# 
# Quando lembramos de um problema semelhante a um novo problema, tendemos a reutilizar a mesma antiga solução ou em alguns casos adaptar uma solução nova, com o conhecimento retido/antigo.
# 
# É composto por 4 principais processos (dependendo da literatura):
# 1. Recuperação - Recuperação de casos (descrição do problema) relevantes na memória;
# 2. Reuso - Reutilização da solução de casos anteriores ao novo problema;
# 3. Revisão - Após mapear a solução, deve-se testar e revisar a solução.
# 4. Retenção - Após a solução ter sido adaptada ao novo problema, a solução do problema será armazenada como uma nova experiência na memória.

# In[9]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing


# Codificação de Naipes para poder buscar pelo vizinho mais próximo

# In[10]:


def codificar_naipes(x):
    print(x)
    if (x == 'ESPADAS'):
        return 1
    
    if (x == 'OURO'):
        return 2
    
    if (x == 'BASTOS'):
        return 3
    
    if (x == 'COPAS'):
        return 4


# Tratamentos para o dataframe

# In[11]:


df = pd.read_csv('dbtrucoimitacao_maos.csv', index_col='idMao').fillna(0)
colunas_string = [
    'naipeCartaAltaRobo', 'naipeCartaMediaRobo','naipeCartaBaixaRobo', 'naipeCartaAltaHumano','naipeCartaMediaHumano', 'naipeCartaBaixaHumano','naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano',	'naipeSegundaCartaRobo', 'naipeSegundaCartaHumano','naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano',
    ]
colunas_int = [col for col in df.columns if col not in colunas_string]
df[colunas_int] = df[colunas_int].astype('int').apply(abs)
# df[colunas_string] = df[colunas_string].any(axis=1)
# df[colunas_string] = df[colunas_string].apply(lambda x: print(x), axis=1)
# pd.get_dummies(df[colunas_string], prefix=colunas_string)
df.replace('ESPADAS', '1', inplace=True)
df.replace('OURO', '2', inplace=True)
df.replace('BASTOS', '3', inplace=True)
df.replace('COPAS', '4', inplace=True)
df[colunas_string] = df[colunas_string].astype('int')
# df.apply(abs)
# df = df[(df >= 0).all(axis=1)]


# Verificação da codificação de naipes

# In[12]:


df


# In[13]:


for column in df.columns:
    print(column)


# In[14]:


df.primeiraCartaRobo


# Métricas estatísticas de todas as colunas da base de casos

# In[15]:


df.describe().T


# ## sklearn
# Avaliação das métricas da base de dados

# In[16]:


from sklearn.model_selection import train_test_split


# In[17]:


y = df['primeiraCartaRobo']
X = df.drop(['primeiraCartaRobo'], axis=1)

SEED = 42
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=SEED)


# In[18]:


len(X), len(X_train), len(X_test)


# In[19]:


from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)


# In[20]:


scaled_df = pd.DataFrame(X_train, columns=X.columns)
scaled_df.describe().T


# In[21]:


from sklearn.neighbors import KNeighborsRegressor


# In[22]:


regressor = KNeighborsRegressor(n_neighbors=100)
regressor.fit(X_train, y_train)


# In[23]:


y_pred = regressor.predict(X_test)


# Verificação do Mean Absolute Error (MAE), Mean Squared Error (MSE) Root Mean Squared Error (RMSE)
# * MAE é usada para avaliar os erros entre as observações;
# * MSE é usada para avaliar o viés (bias) e a variação;
# * RMSE é utilizada para verificar a acurácia do modelo, ao realizar a raiz quadrada do MSE.

# In[24]:


from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False) # Squared -> If True returns MSE value, if False returns RMSE value.

print(f'mae: {mae}')
print(f'mse: {mse}')
print(f'rmse: {rmse}')


# Coeficiente de determinação da predição

# In[25]:


regressor.score(X_test, y_test)


# In[26]:


y.describe()


# ## Teste com casos da própria base

# In[27]:


X


# In[28]:


X.iloc[0]


# Transformação em array numpy e reshape para poder passar pelo Nearest Neighbors

# In[29]:


X.iloc[0].to_numpy()


# In[30]:


from sklearn.neighbors import NearestNeighbors
neigh = NearestNeighbors(n_neighbors=20)
neigh.fit(X.values)
print(neigh.kneighbors([X.iloc[0]]))


# In[31]:


# Reshape your data either using array.reshape(-1, 1) if your data has a single feature or array.reshape(1, -1) if it contains a single sample.
teste = X.iloc[0].to_numpy().reshape(1, -1)
teste
neigh.kneighbors(teste, return_distance=False)


# In[32]:


teste


# In[33]:


X.iloc[21].to_numpy().reshape(1, -1)


# In[34]:


X.iloc[36].to_numpy().reshape(1, -1)


# In[35]:


X.iloc[90].to_numpy().reshape(1, -1)


# Separar colunas interessantes do truco

# In[36]:


colunas_truco = ['jogadorMao', 'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada', 'quemFlor', 'quemContraFlor', 'pontosFlorRobo', 'pontosFlorHumano', 'quemTruco', 'quandoTruco', 'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo', 'qualidadeMaoRobo', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']
len(colunas_truco)


# A ball tree recursively divides the data into nodes defined by a centroid  and radius , such that each point in the node lies within the hyper-sphere defined by  and . The number of candidate points for a neighbor search is reduced through use of the triangle inequality:

# In[37]:


nbrs = NearestNeighbors(n_neighbors=100, algorithm='ball_tree').fit(df)
# distances, indices = nbrs.kneighbors(df)


# In[38]:


# indices


# In[39]:


# distances


# In[40]:


teste_distancia, teste_indices = nbrs.kneighbors(df.iloc[0].to_numpy().reshape(1, -1))


# In[41]:


teste_distancia


# In[42]:


teste_indices


# colunas_truco = ['jogadorMao', 'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada', 'quemFlor', 'quemContraFlor', 'pontosFlorRobo', 'pontosFlorHumano', 'quemTruco', 'quandoTruco', 'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo', 'qualidadeMaoRobo', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']

# In[43]:


teste_registro = df.iloc[0]
teste_registro = df.apply(lambda x: 0)
teste_registro.jogadorMao = 1
teste_registro.cartaAltaRobo = 52
teste_registro.cartaMediaRobo = 24
teste_registro.cartaBaixaRobo = 12
teste_registro.ganhadorPrimeiraRodada = 2
teste_registro.ganhadorSegundaRodada = 2
teste_registro.ganhadorTerceiraRodada = 2
teste_distancia, teste_indices = nbrs.kneighbors(teste_registro.to_numpy().reshape(1, -1))


# In[44]:


teste_distancia


# In[45]:


teste_indices


# In[46]:


teste_registro.to_numpy().reshape(1, -1)


# In[47]:


df.iloc[2380].to_numpy().reshape(1, -1)


# In[48]:


df['ganhadorPrimeiraRodada'].iloc[553]


# In[49]:


pd.DataFrame(teste_registro).T


# In[50]:


df.iloc[teste_indices.tolist()[0]]


# In[51]:


df.ganhadorSegundaRodada.iloc[teste_indices.tolist()[0]]


# In[52]:


df.iloc[teste_indices.tolist()[0]].ganhadorSegundaRodada == 2


# In[53]:


df.iloc[teste_indices.tolist()[0]].ganhadorPrimeiraRodada == 2


# In[54]:


df.iloc[teste_indices.tolist()[0]].ganhadorPrimeiraRodada == 2


# In[55]:


df.iloc[teste_indices.tolist()[0]].ganhadorSegundaRodada == 2


# In[56]:


df.iloc[teste_indices.tolist()[0]].ganhadorTerceiraRodada == 2


# In[57]:


teste = df.iloc[teste_indices.tolist()[0]]
teste.ganhadorPrimeiraRodada


# In[58]:


teste[((teste.ganhadorPrimeiraRodada == 2) & (teste.ganhadorSegundaRodada == 2) | (teste.ganhadorPrimeiraRodada == 2) & (teste.ganhadorTerceiraRodada == 2) | (teste.ganhadorSegundaRodada == 2) & (teste.ganhadorTerceiraRodada == 2))]


# In[146]:


teste[teste.primeiraCartaRobo == 3]


# In[145]:


teste.primeiraCartaRobo.value_counts()


# In[147]:


teste.segundaCartaRobo.value_counts()


# In[148]:


teste.segundaCartaRobo.value_counts()


# In[122]:


teste.primeiraCartaRobo.value_counts().index.to_list()[0]


# In[ ]:




