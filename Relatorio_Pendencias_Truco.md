# Pendências dos testes automatizados do Truco Gaudério

**Qualidade de Software 2026/02 · Lucas e Renato**

Na revisão, a suíte teve **288 testes aprovados, 26 falhas esperadas, 1 falha e 75% de cobertura de linhas**. Os testes de parâmetros variados, entradas nas apostas e retornos de funções já estão alinhados ao enunciado.

| Prioridade | Pendência | O que fazer |
|---|---|---|
| 1 | Inicialização do jogo (D01 / CT44) | O separador da base já foi corrigido. Retirar o `xfail` do teste, manter a verificação de que a base carrega sem adaptador e atualizar o relatório e o README. |
| 2 | Decisões da IA real (CT36–CT40) | Usar a CBR real com situações conhecidas para verificar escolha de carta, respostas a Truco e Envido, repetição da mesma decisão e uso dos dados da rodada correta. O teste atual só verifica o carregamento da base. |
| 3 | Entradas e cenários de partida (CT31–CT34, CT42–CT43) | Testar texto e índice fora do intervalo na escolha da carta, desistência e entrada de nomes. Simular uma mão com cartas fixas, conferir a pontuação e verificar o fim da partida aos 12 pontos. |
| 4 | Pedido de Envido pelo bot (D04 / CT17) | Executar o turno real do bot em vez de copiar a chamada incorreta para o teste. Assim, o teste acompanha o comportamento do jogo quando o defeito for corrigido. |
| 5 | Registro de jogadas (CT41) | Verificar se as cartas da segunda e da terceira rodadas são gravadas nas colunas corretas, conforme previsto no plano do grupo. |

**Para fechar a entrega**, rodar a suíte novamente, registrar os resultados e os defeitos que persistirem, atualizar o documento de requisitos e cenários, preparar o ZIP com os scripts e gravar o MP4 de 5 a 15 minutos mostrando os testes, a execução e os resultados.
