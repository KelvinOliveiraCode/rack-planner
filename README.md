<div align="center">

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-54%20passing-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-96%25-brightgreen?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=flat-square" alt="Windows">
</p>

# rack-planner

**CLI que planeja o rack de um projeto: unidades (U), peso, energia por fase, dissipação térmica e avisos de limite, com saída Markdown.**

</div>

---

## PT-BR

### O que é

rack-plan é uma CLI que planta um rack: lê os itens em YAML, calcula as U usadas, o peso, a energia de cada fase e a temperatura estimada do ar, e avisa quando estoura um limite, produzindo um Markdown de planta. Resolve a conferência de orçamento antes de qualquer equipamento ser montado, sem dependência de ferramenta proprietária.

### Por que foi feito

Planejar rack é onde as restrições invisíveis aparecem: a altura em U quase todo mundo checa, o peso no chão raramente. A maioria das plantas fecha no papel e abre um disjuntor na sala de servidores. Esta ferramenta força a conferência dos quatro limites - U, peso, potência do PDU e amperagem por fase - numa única execução, e expõe a margem térmica (39,9 C contra 40,0 C de meta) em vez de apenas dar OK.

### Como rodar

```powershell
# 1. Instalar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Validar (testes + CLI)
python -m pytest tests/ -v

# 3. Executar
$env:PYTHONPATH="$PWD\src"
python -m rackplan planejar dados\equipamentos-rack.yaml --capacidade dados\capacidade-rack.yaml --saida exemplos\planta-rack.md
```

Saída real (topo do relatório + as 4 violações gravas; a CLI devolve 1 porque há violações - comportamento esperado e documentado):

```
# Planta do rack rack-lab-01

Gerado localmente por `rackplan`. Valores e equipamentos sao ficticios.

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

## Avisos

- [GRAVE] ALTURA: altura estoura: 50U em rack de 42U (faltam -8U) / height overflow
- [GRAVE] PESO: peso estoura: 430.2 kg contra carga maxima de 400 kg, excesso de 30.2 kg / weight overflow
- [GRAVE] POTENCIA: potencia estoura o PDU: 5000 W contra 4800 W de pdu-generica-8-circuitos, excesso de 200 W / power exceeds the PDU rating
- [GRAVE] CORRENTE_FASE: corrente da fase 1 estoura: 17.3 A contra 16.0 A, excesso de 1.3 A / phase current overflow
```

O arquivo de saída é a planta completa em Markdown: Resumo, Eletrica por fase, Carga por circuito, Planta por U (42 linhas) e Avisos.

### O que aprendi

- **O modelo térmico é adimensional e a margem é fina.** A saída é `T_ambiente + P_W / (k * Q)`, com k = 0,35 como fator de escala. O jogo de teste fica em 39,9 C contra 40,0 C de meta: 0,1 C de margem. Pequena mudança de fluxo ou de k inverte o veredito; a ferramenta deixa a conta aberta em vez de dar um OK abstrato.
- **Altura é a restrição dominante; as outras violações nascem dela.** 50U de equipamento não caem em 42U só por rearranjo - o comando ALTURA (excesso de 8U) não se resolve movendo itens. Peso (30,2 kg de excesso), potência (200 W) e corrente de fase (1,3 A) só se fecham retirando ou reduzindo equipamento, ou equilibrando fases. As quatro violações plantadas não se fecham ao mesmo tempo com realocação.
- **Código de saída é o gate da CLI.** Sai 0 sem violação, 1 com violação de limite, 2 em erro de entrada. Essa disciplina permite encadear o comando em CI e falhar o build sem falso positivo: sair 1 com violação é sucesso do design, não erro da ferramenta.
- **`verifica_*` aponta; `alocar` reposiciona - são responsabilidades distintas.** `alocar` aplica uma política (fonte redundante primeiro, peso decrescente, 1U de folga entre fontes de calor) e lança "nao cabe no rack" se não couber, em vez de inventar posição. Não é otimizador de orçamento; o orçamento vem dos `verifica_*`.
- **Orçamento de watts não é orçamento de amperes.** A 127 V, a fase 1 carrega 2200 W -> 17,3 A acima dos 16 A, enquanto o total de 5000 W excede o PDU por outro lado. Fase desbalanceada ultrapassa o disjuntor antes do limite global; por isso a verificação é por fase.

### Limitacoes

- Não mede temperatura real - estima a saída do ar com um modelo linear adimensional.
- Não modela curva de aquecimento nem resfriamento; é um ponto de estado estacionário.
- Não conhece modelo de PDU ou disjuntor real; os limites vêm do YAML de capacidade.
- Não substitui projeto elétrico assinado por profissional habilitado (CREA).
- Valores fictícios (25 equipamentos, 42U, 400 kg, 4800 W), gerados por `tools/gerar_dados.py` de forma determinística.
- Não verifica norma de aterramento, organização de cabos nem redundância física de caminhos.
- Não otimiza a alocação de U; `alocar` só aplica a política do projeto.

### Licenca

MIT. Ver [LICENSE](LICENSE).

---

## EN

### What it is

rack-plan is a CLI that plants a rack: reads items from YAML, computes U used, weight, per-phase power and estimated air temperature, and warns when a limit is exceeded, producing a Markdown rack plan. It runs the budget check before any equipment is physically mounted, with no proprietary tooling.

### Why it was built

Rack planning is where invisible constraints show up: rack height in U is almost always checked, floor load weight rarely. Most plans close on paper and trip a breaker in the server room. This tool forces a check of the four limits - U, weight, PDU power and per-phase amperage - in a single run, and exposes the thermal margin (39.9 C against a 40.0 C target) instead of just saying OK.

### How to run

```powershell
# 1. Install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Validate (tests + CLI)
python -m pytest tests/ -v

# 3. Run
$env:PYTHONPATH="$PWD\src"
python -m rackplan planejar dados\equipamentos-rack.yaml --capacidade dados\capacidade-rack.yaml --saida exemplos\planta-rack.md
```

Real output (top of the report + the 4 grave violations; the CLI exits with 1 because violations exist - expected and documented behavior):

```
# Planta do rack rack-lab-01

Gerado localmente por `rackplan`. Valores e equipamentos sao ficticios.

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

## Avisos

- [GRAVE] ALTURA: altura estoura: 50U em rack de 42U (faltam -8U) / height overflow
- [GRAVE] PESO: peso estoura: 430.2 kg contra carga maxima de 400 kg, excesso de 30.2 kg / weight overflow
- [GRAVE] POTENCIA: potencia estoura o PDU: 5000 W contra 4800 W de pdu-generica-8-circuitos, excesso de 200 W / power exceeds the PDU rating
- [GRAVE] CORRENTE_FASE: corrente da fase 1 estoura: 17.3 A contra 16.0 A, excesso de 1.3 A / phase current overflow
```

The output file is the full Markdown plan: Summary, Eletrica por fase, Carga por circuito, Planta por U (42 rows) and Avisos.

### What I learned

- **The thermal model is dimensionless and the margin is thin.** The output is `T_ambiente + P_W / (k * Q)`, with k = 0.35 as the scale factor. The test set sits at 39.9 C against a 40.0 C target: 0.1 C of margin. Small changes in airflow or k flip the verdict; the tool leaves the arithmetic open instead of giving an abstract OK.
- **Height is the binding constraint; the other violations are downstream.** 50U of equipment does not fit in a 42U rack by rearrangement alone - the ALTURA command (8U over) does not resolve by moving items. Weight (30.2 kg over), power (200 W) and phase current (1.3 A) only close by removing or downsizing equipment or rebalancing phases. The four planted violations do not all close with rearrangement.
- **Exit code is the CLI gate.** Exits 0 without violation, 1 with a limit violation, 2 on input error. That discipline lets you chain the command in CI and fail the build without false positives: exiting 1 on violation is design success, not a tool error.
- **`verifica_*` points; `alocar` repositions - distinct responsibilities.** `alocar` applies a policy (redundant PSU first, weight descending, 1U clearance between heat sources) and raises "nao cabe no rack" if it does not fit, instead of inventing a position. It is not a budget optimizer; the budget comes from `verifica_*`.
- **A power budget is not an amperage budget.** At 127 V, phase 1 carries 2200 W -> 17.3 A over 16 A, while the 5000 W total exceeds the PDU for another reason. A phase imbalance trips the breaker before the global limit; that is why the check is per phase.

### Limitations

- Does not measure real temperature - it estimates the outlet air temperature with a linear dimensionless model.
- Does not model the warm-up or cool-down curve; it is a single steady-state point.
- Does not know a real PDU or breaker model; limits come from the capacity YAML.
- Does not replace an electrical project signed by a licensed professional (CREA).
- Fictitious values (25 items, 42U, 400 kg, 4800 W), deterministically generated by `tools/gerar_dados.py`.
- Does not check grounding, cable management or physical path redundancy.
- Does not optimize U allocation; `alocar` only applies the project's policy.

### License

MIT. See [LICENSE](LICENSE).

---

<div align="center">
  <sub>Por <a href="https://github.com/KelvinOliveiraCode">Kelvin Oliveira</a> &middot;
  <a href="https://kelvinoliveiracode.github.io/portfolio/">portfolio</a></sub>
</div>
