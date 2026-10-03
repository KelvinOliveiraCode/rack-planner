# Como dimensionar um rack com rackplan

## O que é uma unidade (U)

1U = 44,45 mm de altura vertical (1,75 pol) em um rack de 19 pol de largura. A contagem começa no rodapé: o rodapé é a U 1, o topo é a U `altura_u` (42U no exemplo deste repositório).

A seção "Planta por U" da ferramenta lista da U 42 (topo) até a U 1 (rodapé); cada linha é uma U ocupada por um equipamento ou livre. A U é a restrição física mais dura do projeto: ela não se negocia com cálculo de energia, só com espaço. 50U de equipamento não caem em um rack de 42U, ponto final - e a ferramenta marca isso como [GRAVE] ALTURA, sem inventar uma posição.

## Por que peso é a restrição mais ignorada

Um rack de 42U "padrão" suporta entre 300 kg e 400 kg com a altura toda ocupada. O peso é o limite que quase ninguém confere na planta: todos checam U, quase ninguém checa quilograma antes do equipamento entrar. O resultado aparece depois, quando o rack precisa ser virado no elevador ou no caminhão de manutenção.

O rodízio deste repositório exemplifica o erro: 25 equipamentos somam 430,2 kg contra uma carga máxima de 400 kg. O comando acusa PESO GRAVE com excesso de 30,2 kg. É menos custoso deixar duas U de folga na planta do que lidar com um rack que estoura o piso no dia da montagem.

## Como se lê a planta

A saída é um Markdown com cinco seções:

- **Resumo** - totais do projeto: U usadas, altura alvo com a folga recomendada (20%, ou seja, 33U de alvo num rack de 42U), U livres, peso, potência e temperatura estimada.
- **Eletrica por fase** - watts e ampères de cada fase contra o limite. É nesta seção que o desbalanceamento aparece: fase 1 com 2200 W gera 17,3 A e estoura os 16 A, enquanto a soma total ainda bate o limite do PDU.
- **Carga por circuito** - watts por circuito (8 circuitos no exemplo, 1 a 8).
- **Planta por U** - a grade de U, do topo ao rodapé (42 linhas no exemplo). Quando o equipamento estoura a altura do rack, a grade mostra apenas a fatia que entra no rack, e as U excedentes ficam invisíveis fora da grade.
- **Avisos** - [GRAVE] para violação de limite, [AVISO] para alerta de política. As 4 violações gravas do rodízio (ALTURA, PESO, POTENCIA, CORRENTE_FASE) aparecem aqui, com o detalhe técnico em inglês e em PT-BR.

Código de saída: 0 sem violação, 1 com violação de limite, 2 em erro de entrada. Sai 1 quando há violação - isso é comportamento esperado e documentado, não erro da ferramenta.

## As 4 violações e o que fazer com cada uma

1. **ALTURA** - 50U em um rack de 42U (excesso de 8U; no campo da ferramenta o texto diz "faltam -8U"). Não se resolve com realocação. Solução: retirar equipamento ou substituir por modelos de menor altura. É a restrição dominante: todas as outras violações são downstream dela.

2. **PESO** - 430,2 kg contra 400 kg (excesso de 30,2 kg). Peso é cumulativo e não some na realocação. Solução: trocar chassi metálico por modelos mais leves, reduzir densidade ou remover itens. Na prática, trocar um servidor de chassi por um mais leve resolve mais quilograma por U investido.

3. **POTENCIA** - 5000 W contra 4800 W do PDU (excesso de 200 W). Solução: redistribuir a carga para um segundo PDU ou reduzir o consumo. 200 W a 127 V são cerca de 1,6 A, ou seja, uma carga pequena na conta de watts vira amperagem significativa na mesma fase.

4. **CORRENTE_FASE** - fase 1 a 17,3 A contra 16 A (excesso de 1,3 A). Diferente das outras três, esta se resolve com realocação: redistribuir equipamentos entre as fases 2 e 3 equilibra a carga. Aqui a realocação serve, porque a fase 1 tem 2200 W e as demais 1200 W e 1600 W.

Observação importante: as 4 violações plantadas não podem ser fechadas só rearranjando os itens. A altura é dominante e obriga a retirar equipamento; a correção de corrente de fase (item 4) é a única que se fecha por reposicionamento, e mesmo assim só depois de retirar ou reduzir os itens.

## Modelo termico

A temperatura estimada vem de um modelo linear adimensional:

    T_saida = T_ambiente + P_W / (k * Q)

com Q = fluxo de ar em m3/h e k = fator térmico de escala. No exemplo: ambiente 24 C, k = 0,35, fluxo 900 m3/h, 5000 W instalados -> saída estimada 39,9 C, contra meta de 40,0 C. A margem é de 0,1 C: mais potência ou menos fluxo viram 40,1 C e invertem o veredito. Isso não é bug do modelo, é aviso: o projeto está no limite térmico e deve ser refeito antes de qualquer incremento.

A lista de categorias que produzem calor (servidor, storage, ups) é configurável na seção termica.categorias_quentes do YAML de capacidade.

## Politica de posicionamento (a funcao alocar)

`alocar` aplica uma política de posicionamento, não um otimizador de orçamento. A ordem é:

1. Fontes redundantes primeiro - posicionadas nas U mais baixas (rodapé), onde o peso já está concentrado.
2. Peso decrescente - o equipamento mais pesado vai ao rodapé para manter o centro de gravidade baixo.
3. Nome - quebra de empate.

Entre duas fontes de calor consecutivas (servidor, storage, ups) fica 1U livre: `alocar` reserva esse espaço e `verificar_folga_entre_fontes` apenas aponta se ele não estiver respeitado na planta informada.

Se o resultado não couber no rack, `alocar` lança erro ("nao cabe no rack de 42U") em vez de inventar uma posição. Essa é a diferença essencial entre os dois conjuntos de funcoes: `verifica_*` só aponta problemas; `alocar` reposiciona os itens seguindo a política do projeto e falha explicitamente se a política não conseguir encaixar o projeto.

## Resumo

- U é a restrição física dura; peso é a restrição mais ignorada.
- Leia o Resumo, Eletrica por fase, Carga por circuito, Planta por U e Avisos.
- Altura e peso exigem remover ou reduzir equipamento; corrente de fase exige equilibrar as fases.
- O modelo térmico é adimensional e expõe margem fina (39,9 C contra 40,0 C).
- `verifica_*` aponta; `alocar` reposiciona e é uma política, nao um calculo de orçamento.
