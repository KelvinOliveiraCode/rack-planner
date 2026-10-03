# Por que deixar circuito e U reservados desde o projeto

## A reserva é parte do projeto, nao da manutencao

A política deste projeto reserva 20% de U (`folga_recomendada: 0.20`, de 42U de alvo para 33U num rack de 42U) e 20% de potência de circuito. Essa reserva é planejada na planta, por causa do que acontece quando a reserva some.

Quando a reserva de U acaba, crescer um rack significa cortar um cabo, remover um patch panel ou esperar uma janela de manutenção para subir no rack. Cada uma dessas opções custa parada de rede e mão de obra especializada. Deixar duas U no papel é mais barato que uma hora de técnico na sala de servidores.

Quando a reserva de circuito acaba, crescer significa trocar PDU, redistribuir circuitos e desligar equipamentos para reatar. Erro humano entra aí - e erro de fiação em PDU sob tensão é o tipo de erro que não tem rollback.

## O que aparece quando a reserva some: amperagem, nao potencia

Crescer um rack é quase sempre acrescentar potência, não U. O equipamento novo consome kW, e potência é o que se converte em amperagem no ponto de conexão: a 127 V, 200 W a mais são 1,6 A na mesma fase.

No exemplo deste repositório, a fase 1 já carrega 2200 W e chega a 17,3 A contra um limite de 16 A - 1,3 A de excesso que o disjuntor vai abrir. Olhando só a soma total, 5000 W contra 4800 W do PDU, parece um problema pequeno; olhando por fase, é um disjuntor fora do calibre. O crescimento que não reserva fase destrincha primeiro a fase mais carregada, não o PDU inteiro.

O nobreak novo é o caso clássico: ele consome kW e, ao ser ligado, acrescenta amperagem na fase que já estava perto do limite. Se a fase já está na faixa de 15 A, os primeiros 500 W do nobreak jogam o disjuntor fora sem que ninguém tenha visto o kW somar na planilha. Amperagem não aparece no total de watts - aparece na fase.

## A margem termica e o efeito cumulativo

Potência extra esquenta. O modelo do projeto é

    T_saida = T_ambiente + P_W / (k * Q)

e a meta de saída é 40,0 C com ambiente de 24 C, fluxo de 900 m3/h e k = 0,35. O rodízio já está em 39,9 C: 0,1 C de margem. Mais 500 W virariam cerca de 40,2 C e o veredito invertiria - e a planta não avisou porque os 500 W estavam fora do orçamento antes de serem comprados.

Isso é o que a reserva previne: cada watt que entra sem reserva desce direto para a temperatura de saída. Deixar 20% de circuito e 20% de U livres é o que mantem o projeto abaixo da meta quando o equipamento novo chega.

## Custo de mudar depois

- Rearranjar equipamentos para equilibrar fases gasta horas de janela de manutenção e risco de cabo solto. Na planta, a mesma operação custa mover duas linhas do YAML.
- Substituir PDU, cabos de alimentação e disjuntores é obra cara num rack em uso. Fazer a reserva na planta não custa energia nem espaço extra: custa duas U e dois circuitos no papel, que viram crescimento no dia seguinte.
- O custo final não é o da reserva, é o da surpresa: rack superlotado no dia da montagem, disjuntor aberto no dia do nobreak, temperatura acima da meta no dia do picos.

## Como a ferramenta trata a reserva

A ferramenta não reserva automaticamente: ela calcula a folga atual e avisa. `verifica_altura` compara o total de U usadas (50U) com a altura do rack (42U) e com a altura alvo com a folga (33U); se a planta chegar perto do limite, nasce um aviso FOLGA_U. O compromisso de 20% vem do YAML de capacidade (`folga_recomendada: 0.20`), e ele existe só se você mantiver o hábito de ler o campo de folga antes de aprovar a planta.

## Resumo

- Reserve 20% de U e 20% de circuito desde o projeto, nao no dia da manutencao.
- Crescer um rack é acrescentar amperagem, nao potencia: kW vira A na fase que já está cheia.
- O nobreak novo consome kW e acrescenta A; na fase de 15 A, 500 W já abrem o disjuntor.
- Potência extra desce direto para a temperatura de saída: 39,9 C com 0,1 C de margem no exemplo.
- Rearranjar fases depois custa horas de janela; reservar na planta custa duas U no papel.
- A reserva é um compromisso de leitura: `verifica_altura` mostra a folga atual, e cabe a quem aprova a planta manter o número acima de zero.
