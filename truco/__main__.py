from .baralho import Baralho
from .carta import Carta
from .jogador import Jogador
from .jogo import Jogo
from .cbr import Cbr
from .interface import Interface
from .dados import Dados
from .truco import Truco
from .envido import Envido
from .flor import Flor
import random
import os


def reiniciarJogo():
    """Reseta todos os parâmetros do jogo, referente as rodadas"""
    dados.finalizar_partida()
    jogador1.resetar()
    jogador2.resetar()
    baralho.resetar()
    baralho.criar_baralho()
    baralho.embaralhar()
    jogador1.criar_mao(baralho)
    jogador2.criar_mao(baralho)
    # jogo.resetarTrucoPontos()
    envido.resetar()
    truco.resetar()


def turno_do_humano(jogador2):
    """Turno de jogadas do humano, para selecionar o que ele gostaria de jogar."""
    
    if (len(jogador1.checa_mao()) == 3 and jogador2.envido):
        envido_jogador2 = jogador2.avaliar_envido(cbr, 'Envido', 2, jogador1.pontos)
        if (envido_jogador2):
            jogador1.mostrar_opcoes(interface)
            envido.controlador_envido(cbr, dados, 6, 2, jogador1, jogador2, interface)
    
    carta_escolhida = -1
    while (carta_escolhida > len(jogador1.checa_mao()) or int(carta_escolhida) <= 1):
        print(f"\n<< {jogador1.nome} - Jogador 1 >>")
        jogador1.mostrar_opcoes(interface)
        carta_escolhida = int(input(f"\n{jogador1.nome} Qual carta você quer jogar? "))

        # Chama a flor antes do jogador1 jogar envido 
        if ((len(jogador1.checa_mao()) == 3) and (carta_escolhida in [6, 7, 8]) and (jogador2.flor is True)):
            print('Bloqueou o envido com a flor')
            flor.pedir_flor(1, jogador1, jogador2, interface)
            carta_escolhida = -1
        
        if (carta_escolhida <= len(jogador1.checa_mao()) and int(carta_escolhida) >= 0):
            carta_jogador_01 = jogador1.jogar_carta(carta_escolhida)
            # interface.limpar_tela()
            break

        elif (carta_escolhida == 4):
            chamou_truco = (truco.controlador_truco(cbr, dados, 1, jogador1, jogador2))
            # print(f"temp: {chamou_truco}")
            if ((chamou_truco) is False):
                print('pontos truco', truco.retornar_valor_aposta())
                return -1
                break
                # jogador1.adicionar_rodada()

        elif ((len(jogador1.mao) == 3) and (jogador1.flor) and carta_escolhida == 5):
            print('flor')
            flor.pedir_flor(1, jogador1, jogador2, interface)
            interface.border_msg(f"Jogador 1 - {jogador1.nome}: {jogador1.pontos} Pontos Acumulados\nJogador 2 - {jogador2.nome}: {jogador2.pontos} Pontos Acumulados")

        elif ((len(jogador1.checa_mao()) == 3) and (jogador2.pediu_flor is False) and (carta_escolhida in [6, 7, 8])):
            # print('envido')
            # envido.pedir_envido(1, jogador1, jogador2)
            if (carta_escolhida == 6):
                envido.controlador_envido(cbr, dados, 6, 1, jogador1, jogador2, interface)
            elif (carta_escolhida == 7):
                envido.controlador_envido(cbr, dados, 7, 1, jogador1, jogador2, interface)
            elif (carta_escolhida == 8):
                envido.controlador_envido(cbr, dados, 8, 1, jogador1, jogador2, interface)
                # self, dados, tipo, quem_pediu, jogador1, jogador2, interface
                #  dados, tipo, quem_pediu, jogador1, jogador2, interface

        elif (carta_escolhida == 9):
            jogador2.adicionar_pontos(truco.retornar_valor_aposta())
            carta1 = -1
            return carta1
        
        else:
            print('Selecione um valor válido!')

    carta1 = Carta(carta_jogador_01.retornar_numero(), carta_jogador_01.retornar_naipe())
    return carta1


def turno_do_bot(carta_jogador_01):
    """Turno do Bot, para avaliar o estado atual do jogo e jogar suas cartas."""
    if (len(jogador2.checa_mao()) == 3 and carta_jogador_01):
        jogador2.enriquecer_bot(dados=dados, carta_jogador_01=carta_jogador_01)

    carta_escolhida = -1
    while (carta_escolhida > len(jogador2.checa_mao()) or int(carta_escolhida) <= 1):
        print(f"\n<< {jogador2.nome} - Jogador 2 >>")
        # carta_jogador_02 = jogador2.jogar_carta(cbr, truco)
        # carta_escolhida = -1
        carta_escolhida = jogador2.jogar_carta(cbr, truco)

        if (jogador2.pediu_flor is False and (carta_escolhida == 5 and (len(jogador1.mao) == 3))):
            print('flor do Bot')
            flor.pedir_flor(2, jogador1, jogador2, interface)
            interface.border_msg(f"Jogador 1 - {jogador1.nome}: {jogador1.pontos} Pontos Acumulados\nJogador 2 - {jogador2.nome}: {jogador2.pontos} Pontos Acumulados")
        
        if (carta_escolhida <= len(jogador2.checa_mao()) and int(carta_escolhida) >= 0):
            # interface.limpar_tela()
            carta_jogador_02 = jogador2.mao.pop(carta_escolhida)
            break

        elif (carta_escolhida == 4):
            chamou_truco = (truco.controlador_truco(cbr, dados, 2, jogador1, jogador2))
            # print(f"temp: {chamou_truco}")
            if ((chamou_truco) is False):
                # print('pontos truco', truco.retornar_valor_aposta())
                return -1
                break
                # jogador1.adicionar_rodada()

        elif ((jogador1.pediu_flor or jogador2.pediu_flor) is False and carta_escolhida in [6, 7, 8]):
            print('envido')
            # envido.pedir_envido(2, jogador2, jogador1)
            envido.controlador_envido('Envido', 2, jogador1, jogador2, interface)
            if (carta_escolhida == 6):
                envido.controlador_envido(cbr, dados, 6, 1, jogador1, jogador2, interface)

            if (carta_escolhida == 7):
                envido.controlador_envido(cbr, dados, 7, 1, jogador1, jogador2, interface)

            if (carta_escolhida == 8):
                envido.controlador_envido(cbr, dados, 8, 1, jogador1, jogador2, interface)

        elif (carta_escolhida == 7):
            jogador1.adicionar_pontos(1)
            return -1
        
        else:
            print('Selecione um valor válido!')


    # interface.limpar_tela()
    if (carta_jogador_02 is not None):
        carta2 = Carta(carta_jogador_02.retornar_numero(), carta_jogador_02.retornar_naipe())
    return carta2


jogo = Jogo()
baralho = Baralho()
baralho.embaralhar() # Voltar a embaralhar para o jogo funcionar normalmente.
cbr = Cbr()
interface = Interface()
dados = Dados()
truco = Truco()
flor = Flor()
envido = Envido()

truco_aceito = False
pontos_truco = 0
carta_jogador_01 = 0
carta_jogador_02 = 0
ganhador = 0
nome = str(input("Nome Jogador 1: "))
jogador1 = jogo.criar_jogador(nome, baralho)
nome = str(input("Nome Jogador 2 (Bot): "))
jogador2 = jogo.criar_bot(nome, baralho)
jogador1.primeiro = True
jogador2.ultimo = True
# interface.limpar_tela()
# interface.mostrar_jogador_mao(jogador1.nome)

while True:
    truco_fugiu = False
    ocultar_pontos_ac = False

    if jogador1.primeiro == True:
        carta_jogador_01 = turno_do_humano(jogador2)
        if (carta_jogador_01 != -1):
            interface.mostrar_carta_jogada(jogador1.nome, carta_jogador_01)
            carta_jogador_02 = turno_do_bot(carta_jogador_01)
            if (carta_jogador_02 != -1):
                interface.mostrar_carta_jogada(jogador2.nome, carta_jogador_02)

    elif jogador2.primeiro == True:
        carta_jogador_02 = turno_do_bot(None)
        if (carta_jogador_02 != -1):
            interface.mostrar_carta_jogada(jogador2.nome, carta_jogador_02)
            carta_jogador_01 = turno_do_humano(jogador2)
            if (carta_jogador_01 != -1):
                interface.mostrar_carta_jogada(jogador1.nome, carta_jogador_01)
    
    
    if ((carta_jogador_01 == -1 or carta_jogador_02 == -1)):
        truco_fugiu = True
        if (carta_jogador_01 == -1 or carta_jogador_01 is None):
            # jogo.jogador_fugiu(jogador1, jogador1, jogador2, -1)
            interface.mostrar_placar_total_jogador_fugiu(jogador1, jogador1.nome, jogador1.pontos, jogador2.nome, jogador2.pontos)
        
        else:
            # jogo.jogador_fugiu(jogador2, jogador1, jogador2)
            interface.mostrar_placar_total_jogador_fugiu(jogador2, jogador1.nome, jogador1.pontos, jogador2.nome, jogador2.pontos)
        
        # reiniciarJogo()

    else:
        ganhador = jogo.verificar_ganhador(carta_jogador_01, carta_jogador_02, interface)
        jogo.quem_joga_primeiro(jogador1, jogador2, carta_jogador_01, carta_jogador_02, ganhador)
        jogador_ganhou = jogo.adicionar_rodada(jogador1, jogador2, carta_jogador_01, carta_jogador_02, ganhador)
        if (carta_jogador_01 and carta_jogador_02):
            jogador2.enriquecer_bot(dados, carta_jogador_01, carta_jogador_02, jogador_ganhou)

    if (jogador1.rodadas == 2 or jogador2.rodadas == 2):
        ocultar_pontos_ac = True
        if jogador1.rodadas == 2:
            jogador1.adicionar_pontos(truco.retornar_valor_aposta())
            interface.mostrar_ganhador_rodada(jogador1.nome)
            jogador2.enriquecer_bot(dados, carta_jogador_01, carta_jogador_02, 2)
            reiniciarJogo()

        elif jogador2.rodadas == 2:
            jogador2.adicionar_pontos(truco.retornar_valor_aposta())
            jogador2.enriquecer_bot(dados, carta_jogador_01, carta_jogador_02, 1)
            interface.mostrar_ganhador_rodada(jogador2.nome)
            reiniciarJogo()

        interface.mostrar_placar_total(jogador1.nome, jogador1.pontos, jogador2.nome, jogador2.pontos)

    # Caso acabem as cartas nas mãos dos jogadores, ou houve fuga, finaliza as jogadas
    elif (not(jogador1.checa_mao()) and not(jogador2.checa_mao()) or truco_fugiu is True):
        pontos_truco = truco.retornar_valor_aposta()
        ocultar_pontos_ac = True
        if truco_fugiu is True:

            # jogador1.adicionar_pontos(truco.retornar_valor_aposta())
            # interface.mostrar_ganhador_rodada(jogador1.nome)
            reiniciarJogo()
        
        elif jogador1.rodadas > jogador2.rodadas:
            jogador1.adicionar_pontos(truco.retornar_valor_aposta())
            interface.mostrar_ganhador_rodada(jogador1.nome)
            reiniciarJogo()

        elif jogador2.rodadas > jogador1.rodadas:
            jogador2.adicionar_pontos(truco.retornar_valor_aposta())
            interface.mostrar_ganhador_rodada(jogador2.nome)
            reiniciarJogo()
        
        interface.mostrar_placar_total(jogador1.nome, jogador1.pontos, jogador2.nome, jogador2.pontos)

    if (ocultar_pontos_ac is False):
        interface.mostrar_placar_rodadas(jogador1.nome, jogador1.rodadas, jogador2.nome, jogador2.rodadas)

    if jogador1.pontos >= 12:
        interface.mostrar_ganhador_jogo(jogador1.nome)
        break

    elif jogador2.pontos >= 12:
        interface.mostrar_ganhador_jogo(jogador2.nome)
        break
'''
To do:
- Checar funcionamento do Truco/Envido;
- Diferenciar flag -1 do fugiu_truco da flag de ir ao baralho;
- Pegar valor da aposta de truco da classe Truco e não do Jogo (verificar atribuição de pontos);
- Remover o NA da bases de caso, para que os Nearest Neighbors desconsiderem valores inexistentes. Scikit-Learn não aceita valores NaN, então no estado atual foi usado o método fillna, que não é a abordagem ideal para CBR.
'''