# Planta do rack rack-lab-01

Gerado localmente por `rackplan`. Valores e equipamentos sao ficticios.
Generated locally by `rackplan`. Values and equipment are fictitious.

## Resumo

- Altura do rack: 42U
- Altura usada: 50U
- Altura alvo com 20% de folga: 33U
- U livres: 0
- Peso total: 430.2 kg de 400 kg
- Potencia total: 5000 W de 4800 W
- Temperatura de saida estimada: 39.9 C (meta 40.0 C, ambiente 24.0 C)

## Eletrica por fase

| fase | potencia_w | corrente_a | limite_a |
| --: | --: | --: | --: |
| 1 | 2200 | 17.3 | 16.0 |
| 2 | 1200 | 9.4 | 16.0 |
| 3 | 1600 | 12.6 | 16.0 |

## Carga por circuito

| circuito | potencia_w |
| --: | --: |
| 1 | 180 |
| 2 | 420 |
| 3 | 1920 |
| 4 | 790 |
| 5 | 95 |
| 6 | 55 |
| 7 | 1480 |
| 8 | 60 |

## Planta por U

| U | equipamento | categoria | altura_u | peso_kg | consumo_w | fonte |
| --: | --- | --- | --: | --: | --: | --- |
| 42 | patch-panel-24p-d | patch-panel | 1 | 2.6 | 0 | simples |
| 41 | switch-industrial-16p | switch | 1 | 4.2 | 60 | simples |
| 40 | servidor-virtualizacao-02 | servidor | 4 | 40.0 | 780 | redundante |
| 39 | servidor-virtualizacao-02 | servidor | 4 | 40.0 | 780 | redundante |
| 38 | servidor-virtualizacao-02 | servidor | 4 | 40.0 | 780 | redundante |
| 37 | servidor-virtualizacao-02 | servidor | 4 | 40.0 | 780 | redundante |
| 36 | servidor-virtualizacao-01 | servidor | 4 | 40.0 | 700 | redundante |
| 35 | servidor-virtualizacao-01 | servidor | 4 | 40.0 | 700 | redundante |
| 34 | servidor-virtualizacao-01 | servidor | 4 | 40.0 | 700 | redundante |
| 33 | servidor-virtualizacao-01 | servidor | 4 | 40.0 | 700 | redundante |
| 32 | patch-panel-24p-c | patch-panel | 1 | 2.6 | 0 | simples |
| 31 | kvm-extensor | kvm | 1 | 1.8 | 45 | simples |
| 30 | ups-1kva-b | ups | 2 | 20.0 | 55 | redundante |
| 29 | ups-1kva-b | ups | 2 | 20.0 | 55 | redundante |
| 28 | servidor-banco-02 | servidor | 4 | 42.0 | 480 | redundante |
| 27 | servidor-banco-02 | servidor | 4 | 42.0 | 480 | redundante |
| 26 | servidor-banco-02 | servidor | 4 | 42.0 | 480 | redundante |
| 25 | servidor-banco-02 | servidor | 4 | 42.0 | 480 | redundante |
| 24 | servidor-banco-01 | servidor | 4 | 42.0 | 620 | redundante |
| 23 | servidor-banco-01 | servidor | 4 | 42.0 | 620 | redundante |
| 22 | servidor-banco-01 | servidor | 4 | 42.0 | 620 | redundante |
| 21 | servidor-banco-01 | servidor | 4 | 42.0 | 620 | redundante |
| 20 | organizador-cabos-01 | organizador | 1 | 1.2 | 0 | simples |
| 19 | kvm-16-portas | kvm | 1 | 4.5 | 35 | simples |
| 18 | storage-controladora | storage | 1 | 12.0 | 265 | redundante |
| 17 | ups-2kva | ups | 4 | 38.0 | 60 | redundante |
| 16 | ups-2kva | ups | 4 | 38.0 | 60 | redundante |
| 15 | ups-2kva | ups | 4 | 38.0 | 60 | redundante |
| 14 | ups-2kva | ups | 4 | 38.0 | 60 | redundante |
| 13 | servidor-aplicacao-02 | servidor | 4 | 38.0 | 650 | redundante |
| 12 | servidor-aplicacao-02 | servidor | 4 | 38.0 | 650 | redundante |
| 11 | servidor-aplicacao-02 | servidor | 4 | 38.0 | 650 | redundante |
| 10 | servidor-aplicacao-02 | servidor | 4 | 38.0 | 650 | redundante |
| 9 | servidor-aplicacao-01 | servidor | 4 | 38.0 | 650 | redundante |
| 8 | servidor-aplicacao-01 | servidor | 4 | 38.0 | 650 | redundante |
| 7 | servidor-aplicacao-01 | servidor | 4 | 38.0 | 650 | redundante |
| 6 | servidor-aplicacao-01 | servidor | 4 | 38.0 | 650 | redundante |
| 5 | roteador-borda | roteador | 1 | 7.2 | 220 | redundante |
| 4 | switch-distribuicao-24p | switch | 1 | 5.0 | 140 | simples |
| 3 | switch-acesso-48p | switch | 1 | 6.5 | 180 | simples |
| 2 | patch-panel-24p-b | patch-panel | 1 | 2.8 | 0 | simples |
| 1 | patch-panel-48p | patch-panel | 1 | 3.5 | 0 | simples |

## Avisos

- [GRAVE] ALTURA: altura estoura: 50U em rack de 42U (8U acima do rack) / height overflow
  - EN: [GRAVE] ALTURA: height overflow: 50U in a 42U rack (8U over the rack)
- [GRAVE] PESO: peso estoura: 430.2 kg contra carga maxima de 400 kg, excesso de 30.2 kg / weight overflow
  - EN: [GRAVE] PESO: weight overflow: 430.2 kg against a 400 kg rating, 30.2 kg over
- [GRAVE] POTENCIA: potencia estoura o PDU: 5000 W contra 4800 W de pdu-generica-8-circuitos, excesso de 200 W / power exceeds the PDU rating
  - EN: [GRAVE] POTENCIA: power exceeds the PDU rating: 5000 W against 4800 W on pdu-generica-8-circuitos, 200 W over
- [GRAVE] CORRENTE_FASE: corrente da fase 1 estoura: 17.3 A contra 16.0 A, excesso de 1.3 A / phase current overflow
  - EN: [GRAVE] CORRENTE_FASE: phase 1 current overflow: 17.3 A against 16.0 A, 1.3 A over
- [AVISO] FONTES_JUNTAS: fontes de calor sem folga de 1U entre elas: servidor-aplicacao-01 x servidor-aplicacao-02 (sem folga de 1U), servidor-aplicacao-02 x ups-2kva (sem folga de 1U), ups-2kva x storage-controladora (sem folga de 1U), servidor-banco-01 x servidor-banco-02 (sem folga de 1U), servidor-banco-02 x ups-1kva-b (sem folga de 1U), servidor-virtualizacao-01 x servidor-virtualizacao-02 (sem folga de 1U), libreria-fitas-24-slot x modulo-bateria-ups (sem folga de 1U) / heat sources without clearance
  - EN: [AVISO] FONTES_JUNTAS: heat sources without 1U clearance: servidor-aplicacao-01 x servidor-aplicacao-02 (sem folga de 1U), servidor-aplicacao-02 x ups-2kva (sem folga de 1U), ups-2kva x storage-controladora (sem folga de 1U), servidor-banco-01 x servidor-banco-02 (sem folga de 1U), servidor-banco-02 x ups-1kva-b (sem folga de 1U), servidor-virtualizacao-01 x servidor-virtualizacao-02 (sem folga de 1U), libreria-fitas-24-slot x modulo-bateria-ups (sem folga de 1U)
- [AVISO] FLUXO_AR: fluxo de ar apertado: 0.18 m3/h por W, abaixo de 0.25 / airflow is tight for the installed power
  - EN: [AVISO] FLUXO_AR: airflow is tight for the installed power: 0.18 m3/h per W, below 0.25

Total de avisos: 6 (4 graves).
