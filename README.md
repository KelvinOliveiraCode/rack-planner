# rack-planner

[English](README.en.md) · **Português (Brasil)**

[![Python 3](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](#) [![PyYAML](https://img.shields.io/badge/PyYAML-%C3%BAnica%20dep-3776AB?style=flat-square)](#) [![pytest](https://img.shields.io/badge/pytest-54%20testes-0A9EDC?style=flat-square&logo=pytest)](#) [![MIT License](https://img.shields.io/badge/License-MIT-f4c430?style=flat-square)](LICENSE)

## O que é

**Planejador de rack**: dimensiona alocação de equipamentos (U, peso, potência), verifica requisitos elétricos (corrente por fase, circuitos), térmicos (temperatura de saída, fluxo), ocupação (alocação best-fit, detecção de sobreposições) e gera relatório visual com avisos de violação. É um laboratório educacional de datacenter/infra.

## Status

Laboratório educacional funcional e testado (54 testes).

## Funcionalidades

- **Modelo** (`modelo.py`): `Equipamento`, `Pdu`, `CapacidadeRack`, `carregar_equipamentos` e `carregar_capacidade` (YAML).
- **Dimensionamento** (`dimensionamento.py`): `soma_u`, `soma_peso`, `soma_potencia`, `sobreposicoes`, `verifica_altura/peso`.
- **Elétrica** (`eletrica.py`): `corrente_de_carga`, `corrente_por_fase`, `potencia_por_fase`, `circuitos_usados`, `verifica_corrente_por_fase/circuito/eletrica`.
- **Térmica** (`termica.py`): `temperatura_saida`, `temperatura_estimada`, `verifica_termica`, `alertas_de_fluxo`.
- **Ocupação** (`ocupacao.py`): `alocar` (best-fit), `verificar_folga_entre_fontes`, `resumo_de_ocupacao`.
- **Relatório** (`relatorio.py`): `_planta` (visual), `gerar_relatorio` com `Aviso` por violação, `tem_violacao`.
- **Avisos** (`aviso.py`): `Aviso` e `formatar`.
- **CLI** (`rackplan`).

## Arquitetura

Pacote `rackplan` com `modelo`, `dimensionamento`, `eletrica`, `termica`, `ocupacao`, `relatorio`, `aviso` e `cli`.

## Stack

- Python ≥ 3.10, PyYAML ≥ 6.0
- pytest (dev)

## Estrutura

```
rack-planner/
├── src/rackplan/    # modelo · dimensionamento · eletrica · termica · ocupacao · relatorio · aviso · cli
├── dados/
├── tests/           # 54 testes
└── LICENSE          # MIT
```

## Pré-requisitos e instalação

```bash
pip install -e .
```

## Como executar

```bash
rackplan <subcmd> dados/
```

## Testes e qualidade

```bash
PYTHONPATH=src python -m pytest tests/   # 54 passed
```

## Decisões técnicas

- Alocação best-fit: coloca equipamentos do maior para o menor U.
- Verificação elétrica por fase (monofásica/trifásica) + circuitos.

## Limitações

- Sem refrigeração líquida (só ar: temperatura de saída × fluxo).
- Tensão fixa (127/220V) — configurável no YAML.

## Processo de desenvolvimento

Projeto individual de Kelvin Oliveira, construído com agentes de IA orquestrados e revisado pelo autor.

## Licença e autor

MIT — Copyright (c) 2026 Kelvin Rebelo de Oliveira. Autor: [Kelvin Oliveira](https://github.com/KelvinOliveiraCode) · [Portfólio](https://kelvinoliveiracode.github.io/portfolio/)
