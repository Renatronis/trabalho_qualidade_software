# Truco Gaudério com CBR

O presente projeto foi desenvolvido como trabalho para a disciplina de Aplicações em Aprendizado de Máquina, para a Pós-Graduação em Ciência da Computação na Universidade Federal de Santa Maria.

O intuito deste projeto é implementar um jogo Truco em Python, em que um humano possar jogar contra um bot. Sendo que, este bot terá suas decisões baseadas na técnica de **Inteligência Artificial (IA)** denominada **Case-Based Reasoning (CBR)**.

Nessa técnica de **IA**, existe um problema que precisa ser resolvido (caso), e o CBR utiliza uma base de casos com problemas antigos já conhecidos e documentados (podendo apresentar uma solução com sucesso ou até mesmo sem sucesso). Havendo também a viabilidade de utilizar casos que não sejam exatamente idênticos, possibilitando que os casos mais similares possam ser usados como referência de solução para o problema que se quer solucionar.

Sendo assim, o bot do jogo deverá tomar ações de acordo com os eventos situacionais do jogo, ou seja, considerar as cartas que tem em mão, as condições especiais do jogo (Truco, Envido, Flor) e por fim as jogadas do oponente humano.

A base de casos encontra-se no arquivo dbtrucoimitacao_maos.csv, e pode ser alterada conforme nencessário. O modelo de caso encontra-se no arquivo modelo_registro.csv, e deve seguir o mesmo padrão da base de casos.

## Pré-requisitos e Execução do Código

Como pré-requisito, é necessário realizar a instalação dos pacotes pandas e scikit-learn em seu ambiente virtual (ou no seu próprio ambiente base), através do seguinte comando:

```
pip install -r requirements.txt
```

Para executar o jogo, é necessário o seguinte comando:

```
python -m truco
```

## Regras Gerais do Jogo

As regras para o jogo do truco foram retiradas do site [Jogatina](https://www.jogatina.com/regras-como-jogar-truco-gauderio.html), embora existam muitas variantes dessas regras, optou-se por seguir um guia mais direto para simplificar o entendimento do jogo e da implementação.

### Jogo Truco em Python

- **Jogadores**: 1v1 ou 2v2 (na atual implementação do jogo, somente 1v1 disponível)
- **Número de cartas**: 40 (retirando-se 8, 9, 10 e curingas)
- **Distribuição**: 3 cartas para cada participante
- **Objetivo**: O jogador ou a dupla que atingir o total de pontos, ganha a partida.
- **A distribuição das cartas é feita de forma automática e aleatória pelo sistema, não havendo a intervenção de nenhum jogador.**

### Convenções

- **O baralho usado é o baralho espanhol**
- **Sequência de menor para maior**: 4, 5, 6, 7, 10, 11, 12, 1, 2, 3 (de todos os naipes)
- **As manilhas são na sequência de menor para maior**: 7 de ouros, 7 de espadas, 1 de paus e 1 de espadas

### Definições

- **Mão** - Fração da partida, vale 1 ponto e poderá ter seu valor aumentado através das disputas de Truco e Envido. É disputada em melhor de 3 rodadas.
- **Rodada** - É a fração da “mão”, em cada rodada os jogadores mostram uma carta.
- **Falta** - É a diferença entre o placar final do jogo e os pontos da pessoa que está ganhando.
- **Empatar** - Quando a maior carta de cada dupla, numa determinada rodada, tem o mesmo valor.
- **Esconder** - Carta Jogar a carta virada para a mesa, passando assim a não valer nada. Também chamado de carta “coberta”, ou “carta encoberta”.
- **Ir ao baralho** - Quando o jogador ou dupla foge da rodada, entregando os pontos de Truco para o jogador ou dupla adversária.

### Pontos obtidos na disputa de Truco Gaudério

- **Truco** - Disputa para aumentar o valor da “mão” para 2
- **Re-truco** - Disputa para aumentar o valor da “mão” para 3
- **Vale 4** - Disputa para aumentar o valor da “mão” para 4

### Pontos obtidos na disputa de Envido

- **Envido** - Disputa paralela que ocorre durante a primeira rodada de uma mão para aumentar seu valor em até 2 pontos.
- **Real Envido** - Similar ao Envido, mas pode aumentar o valor da mão em até 5 pontos.
- **Falta Envido** - Similar ao Envido, mas pode aumentar o valor da mão para a diferença entre o placar final do jogo e os pontos da pessoa que está ganhando.

### Pontos obtidos na disputa de Flor

- **Flor** - Tipo especial de Envido em que o jogador deve ter 3 cartas do mesmo naipe. É possível aumentar o valor da mão em 3 pontos.
- **Contra-flor** - Uma das possíveis respostas ao pedido de Flor. Pode aumentar o valor da mão em 6 pontos. (Em algumas situações o valor pode ser maior)
- **Contra-flor e o resto** - Disputa similar a Contra-flor que pode aumentar o valor da mão para a diferença entre o placar final do jogo e os pontos da pessoa que está ganhando, além dos pontos da Contra-flor. (Em algumas situações o valor pode ser maior)

### A fundação/base dos códigos no presente projeto, foi baseada no [repositório criado pelo usuário anthonyzutter](https://github.com/anthonyzutter/Truco-Jogo).
