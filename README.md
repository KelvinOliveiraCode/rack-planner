<div align="center">

<img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/testes-54%20passing-brightgreen?style=flat-square" alt="Testes">
<img src="https://img.shields.io/badge/cobertura-96%25-brightgreen?style=flat-square" alt="Cobertura">
<img src="https://img.shields.io/badge/deps-PyYAML%20only-blue?style=flat-square" alt="Dependencias">
<img src="https://img.shields.io/badge/licenca-MIT-yellow?style=flat-square" alt="Licenca">
<img src="https://img.shields.io/badge/CI-Windows-blue?style=flat-square" alt="CI">

</div>

# rack-planner

CLI que planeja o rack de um projeto: unidades (U), peso, potencia por fase, dissipacao termica e avisos de limite, com saida em Markdown.

## Problema / Por que existe

Planejar um rack conferencia quase sempre a altura em U, mas raramente checa junto o peso no chao, a potencia do PDU, a amperagem por fase e a temperatura de saida do ar. Uma planta que fecha no papel pode disjuntar na sala de servidores. O rack-planner executa a conferencia dos quatro limites — U, peso, potencia do PDU e corrente por fase — mais o modelo termico, numa unica execucao, antes de qualquer equipamento ser montado, sem dependencia de ferramenta proprietaria.

## O que faz

- Le equipamentos e capacidade do rack a partir de arquivos YAML (padrao: dados/equipamentos-rack.yaml e dados/capacidade-rack.yaml).
- Soma U usadas, peso total, potencia total, potencia e corrente por fase e por circuito.
- Estima a temperatura de saida do ar com o modelo linear T_saida = T_ambiente + P_W / (k * Q).
- Emite avisos bilinguais (PT-BR e EN) quando um limite e estourado (GRAVE) ou esta comprometido (AVISO): altura, peso, potencia do PDU, corrente por fase, corrente por circuito, temperatura, fluxo de ar, folga de U, sobreposicao de U e folga entre fontes de calor.
- Gera um relatorio em Markdown com resumo, eletrica por fase, carga por circuito, planta por U (todas as U do rack) e avisos.
- Retorna codigo de saida 0 sem violacao, 1 com violacao de limite, 2 em erro de entrada, permitindo encadear o comando em CI.
- Suporta saida JSON com a opcao --json (totais e flag de violacao).
- Inclui a funcao alocar(), que reposiciona equipamentos segundo a política do projeto (fonte redundante primeiro, peso decrescente, 1U de folga entre fontes de calor) e avisa se algum item nao couber no rack.

## Stack

- Python >= 3.10
- PyYAML >= 6.0 (unica dependencia de execucao)
- pytest >= 7.4 e pytest-cov >= 4.1 (apenas desenvolvimento)
- Empacotamento com setuptools, layout src/
- CI: GitHub Actions em windows-latest, Python 3.11

## Como funciona

- modelo.py: dataclasses Equipamento, Pdu e CapacidadeRack; carregamento e validacao dos YAML (campos obrigatorios, categorias validas, numeros nao negativos, nomes unicos). Erro de entrada levanta ErroDeValidacao e a CLI sai com 2.
- dimensionamento.py: somas de U, peso e potencia; unidades ocupadas e livres; sobreposicoes; verifica_altura (GRAVE acima da altura do rack, AVISO acima da altura util com 20% de folga), verifica_peso e verifica_sobreposicao.
- ocupacao.py: alocar() aplica a política de alocacao e levanta ValueError se algum equipamento ficar acima da altura do rack; verificar_folga_entre_fontes() avisa fontes de calor sem 1U de folga; resumo_de_ocupacao() monta os numeros do relatorio.
- eletrica.py: corrente = potencia / tensao; verifica_potencia (PDU), verifica_corrente_por_fase (limite por fase) e verifica_circuito (corrente nominal por circuito, AVISO).
- termica.py: temperatura_estimada() com o modelo adimensional; verifica_termica (GRAVE acima da meta de saida); alertas_de_fluxo (AVISO abaixo de 0,25 m3/h por W).
- relatorio.py: relatorio Markdown deterministico em PT-BR; tem_violacao() indica se ha pelo menos um aviso GRAVE.
- cli.py: ponto de entrada rackplan; subcomando planejar; codigo de saida 0/1/2.

Exemplo com os dados incluidos (25 equipamentos, ficticios, gerados por tools/gerar_dados.py):

```
$env:PYTHONPATH="$PWD\src"
python -m rackplan planejar dados\equipamentos-rack.yaml --capacidade dados\capacidade-rack.yaml --saida exemplos\planta-rack.md
```

Resumo do relatorio gerado:

- Altura do rack: 42U
- Altura usada: 50U
- Altura alvo com 20% de folga: 33U
- U livres: 0
- Peso total: 430.2 kg de 400 kg
- Potencia total: 5000 W de 4800 W
- Temperatura de saida estimada: 39.9 C (meta 40.0 C, ambiente 24.0 C)

Eletrica por fase (127 V):

| fase | potencia_w | corrente_a | limite_a |
| --: | --: | --: | --: |
| 1 | 2200 | 17.3 | 16.0 |
| 2 | 1200 | 9.4 | 16.0 |
| 3 | 1600 | 12.6 | 16.0 |

Avisos emitidos: [GRAVE] ALTURA, [GRAVE] PESO, [GRAVE] POTENCIA, [GRAVE] CORRENTE_FASE. A CLI sai com 1 (comportamento esperado: os valores de teste foram gerados intencionalmente acima dos limites para exercer as quatro verificacoes graves).

## Como rodar

Prerequisito: Python 3.10 ou superior.

```powershell
# 1. Ambiente virtual e dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Testes
python -m pytest tests/ -q

# 3. Executar (PYTHONPATH necessario porque o pacote esta em src/)
$env:PYTHONPATH="$PWD\src"
python -m rackplan planejar dados\equipamentos-rack.yaml --capacidade dados\capacidade-rack.yaml --saida exemplos\planta-rack.md
```

Alternativa, instalando o pacote:

```
pip install -e .
rackplan planejar dados\equipamentos-rack.yaml --capacidade dados\capacidade-rack.yaml --saida exemplos\planta-rack.md
```

Opcoes da CLI: --equipamentos/-e (YAML dos equipamentos), --capacidade/-c (padrao dados/capacidade-rack.yaml), --saida/-s (arquivo Markdown de saida; padrao stdout) e --json (imprime os totais em JSON).

## Estrutura do projeto

```
rack-planner/
├── dados/               # YAML de entrada: equipamentos e capacidade (ficticios, gerados por tools/gerar_dados.py)
├── docs/                # notas: como-dimensionar-um-rack.md, circuito-reservado.md
├── exemplos/            # planta-rack.md: saida de exemplo do relatorio
├── src/rackplan/        # pacote (layout src/)
│   ├── __init__.py, __main__.py, cli.py   # ponto de entrada e CLI
│   ├── modelo.py        # dataclasses, carregamento e validacao de YAML
│   ├── ocupacao.py      # alocacao de U, folga entre fontes de calor
│   ├── dimensionamento.py   # somas de U, peso, potencia; verificacoes de altura, peso, sobreposicao
│   ├── eletrica.py      # corrente, potencia por fase e circuito, limites do PDU
│   ├── termica.py       # temperatura de saida estimada e alertas de fluxo de ar
│   ├── aviso.py         # avisos bilinguais PT-BR/EN
│   └── relatorio.py     # relatorio Markdown deterministico
├── tests/               # testes pytest (54 testes)
├── tools/               # gerar_dados.py, verificar_encoding.py
├── pyproject.toml, requirements.txt
└── LICENSE              # MIT
```

## Trade-offs e decisoes

- Orçamento de watts e diferente de orçamento de amperes. A 127 V, 2200 W na fase 1 resultam em 17.3 A, acima do disjuntor de 16 A, embora o total de 5000 W exceda o PDU por outro motivo. A verificacao e feita por fase porque um desbalanceamento dispara o disjuntor antes do limite global.
- `verifica_*` apenas aponta; `alocar` reposiciona. Sao responsabilidades distintas: `alocar` aplica a política (fonte redundante primeiro, peso decrescente, 1U de folga entre fontes de calor) e lança "nao cabe no rack" se nao couber, sem inventar posicao. Nao e otimizador de orçamento; o orçamento vem das verificacoes.
- O modelo termico e adimensional (k = 0.35) e deixa a conta aberta: com os dados de teste, 39.9 C contra 40.0 C de meta, ou seja, 0.1 C de margem. Uma pequena mudança no fluxo de ar ou em k inverte o veredito, em vez de retornar um OK abstrato.
- Codigo de saida 1 com violacao e sucesso de projeto, nao erro da ferramenta: permite encadear o comando em CI e falhar o build sem falso positivo.
- Dados de entrada ficticios e determinísticos: 25 equipamentos, 42U, 400 kg, 4800 W, gerados por tools/gerar_dados.py. Nao descrevem equipamento real.
- Unica dependencia de execucao (PyYAML) para facilitar a instalacao em ambientes restritos.

## Limitações conhecidas

- Nao mede temperatura real: estima a saida do ar com um modelo linear adimensional em ponto de estado estacionario; nao modela curva de aquecimento nem resfriamento.
- Nao conhece modelo real de PDU ou disjuntor: os limites vem do YAML de capacidade.
- Nao substitui projeto eletrico assinado por profissional habilitado (CREA).
- Nao verifica norma de aterramento, organizacao de cabos nem redundancia fisica de caminhos.
- Nao otimiza a alocacao de U: `alocar` so aplica a política do projeto.
- Valores fictícios (25 equipamentos, 42U, 400 kg, 4800 W).
- Nao calcula custo financeiro nem lead time de equipamentos.

## Licenca

MIT. Veja [LICENSE](LICENSE).

## Autor

Kelvin Oliveira — https://github.com/KelvinOliveiraCode · portfolio: https://kelvinoliveiracode.github.io/portfolio/
